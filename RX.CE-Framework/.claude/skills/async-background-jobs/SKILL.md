---
name: async-background-jobs
description: Comprehensive guide for designing and implementing background job processing systems. Covers job queues, workers, scheduling, retries, monitoring, and scalability patterns. Use when building async task processing, scheduled jobs, email sending, report generation, data processing pipelines, or any long-running operations that should happen outside request-response cycles.
---

# Async Background Jobs

Comprehensive framework for designing reliable, scalable background job processing systems.

## When to Use

Apply this skill when:
- Processing tasks that take too long for HTTP requests
- Sending emails, SMS, or notifications
- Generating reports or exports
- Processing uploaded files (images, videos, documents)
- Running scheduled tasks (cron-like functionality)
- Handling webhooks asynchronously
- Building data processing pipelines
- Implementing retry mechanisms for failed operations
- Scaling workload across multiple workers
- Deferred execution of expensive operations

## Core Principles

### 1. Keep Requests Fast
- Never make users wait for slow operations
- Return immediately, process asynchronously
- Provide status updates via polling or webhooks

### 2. Jobs Should Be Idempotent
- Safe to run multiple times
- Same input = same result
- Handle duplicate jobs gracefully

### 3. Jobs Should Be Atomic
- Complete entirely or fail entirely
- No partial state
- Transactional where possible

### 4. Handle Failures Gracefully
- Retry transient failures with backoff
- Dead letter queue for permanent failures
- Alert on repeated failures

### 5. Monitor and Observe
- Track job success/failure rates
- Monitor queue depth
- Alert on stuck jobs
- Provide visibility into processing

## Job Queue Patterns

### Simple In-Memory Queue (Development/Testing)

```javascript
class SimpleJobQueue {
  constructor() {
    this.queue = [];
    this.processing = false;
  }
  
  async enqueue(jobType, data, options = {}) {
    const job = {
      id: generateId(),
      type: jobType,
      data,
      attempts: 0,
      maxAttempts: options.maxAttempts || 3,
      createdAt: new Date(),
      status: 'pending'
    };
    
    this.queue.push(job);
    this.processNext();
    
    return job.id;
  }
  
  async processNext() {
    if (this.processing || this.queue.length === 0) {
      return;
    }
    
    this.processing = true;
    const job = this.queue.shift();
    
    try {
      await this.execute(job);
      job.status = 'completed';
      
    } catch (error) {
      job.attempts++;
      
      if (job.attempts < job.maxAttempts) {
        // Retry with exponential backoff
        const delay = Math.pow(2, job.attempts) * 1000;
        setTimeout(() => {
          this.queue.push(job);
          this.processNext();
        }, delay);
      } else {
        job.status = 'failed';
        job.error = error.message;
        console.error(`Job ${job.id} failed permanently:`, error);
      }
    } finally {
      this.processing = false;
      this.processNext();
    }
  }
  
  async execute(job) {
    const handler = this.handlers[job.type];
    if (!handler) {
      throw new Error(`No handler for job type: ${job.type}`);
    }
    
    return await handler(job.data);
  }
  
  handlers = {};
  
  registerHandler(type, handler) {
    this.handlers[type] = handler;
  }
}

// Usage
const queue = new SimpleJobQueue();

queue.registerHandler('send-email', async (data) => {
  await emailService.send(data.to, data.subject, data.body);
});

// Enqueue job
await queue.enqueue('send-email', {
  to: 'user@example.com',
  subject: 'Welcome',
  body: 'Welcome to our platform!'
});
```

### Redis-Based Queue (Bull/BullMQ)

```javascript
import { Queue, Worker } from 'bullmq';

// Create queue
const emailQueue = new Queue('emails', {
  connection: {
    host: 'localhost',
    port: 6379
  }
});

// Enqueue jobs
async function sendEmailAsync(emailData) {
  const job = await emailQueue.add('send-email', emailData, {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 1000
    },
    removeOnComplete: true,
    removeOnFail: false
  });
  
  return job.id;
}

// Process jobs (in separate worker process)
const emailWorker = new Worker('emails', async (job) => {
  console.log(`Processing job ${job.id}`);
  
  switch (job.name) {
    case 'send-email':
      await emailService.send(
        job.data.to,
        job.data.subject,
        job.data.body
      );
      break;
      
    default:
      throw new Error(`Unknown job type: ${job.name}`);
  }
}, {
  connection: {
    host: 'localhost',
    port: 6379
  },
  concurrency: 5 // Process 5 jobs concurrently
});

// Listen to events
emailWorker.on('completed', (job) => {
  console.log(`Job ${job.id} completed`);
});

emailWorker.on('failed', (job, error) => {
  console.error(`Job ${job.id} failed:`, error);
});

emailWorker.on('progress', (job, progress) => {
  console.log(`Job ${job.id} is ${progress}% complete`);
});

// Usage in API
app.post('/api/users', async (req, res) => {
  const user = await db.users.create(req.body);
  
  // Send welcome email asynchronously
  await sendEmailAsync({
    to: user.email,
    subject: 'Welcome!',
    body: 'Welcome to our platform!'
  });
  
  // Return immediately
  res.status(201).json({ user });
});
```

### AWS SQS Queue

```javascript
import { SQSClient, SendMessageCommand, ReceiveMessageCommand, DeleteMessageCommand } from '@aws-sdk/client-sqs';

const sqsClient = new SQSClient({ region: 'us-east-1' });
const QUEUE_URL = process.env.SQS_QUEUE_URL;

// Enqueue job
async function enqueueJob(jobType, data) {
  const message = {
    id: generateId(),
    type: jobType,
    data,
    timestamp: new Date().toISOString()
  };
  
  await sqsClient.send(new SendMessageCommand({
    QueueUrl: QUEUE_URL,
    MessageBody: JSON.stringify(message),
    MessageAttributes: {
      jobType: {
        DataType: 'String',
        StringValue: jobType
      }
    }
  }));
  
  return message.id;
}

// Worker
class SQSWorker {
  constructor(queueUrl, handlers) {
    this.queueUrl = queueUrl;
    this.handlers = handlers;
    this.isRunning = false;
  }
  
  async start() {
    this.isRunning = true;
    
    while (this.isRunning) {
      try {
        await this.poll();
      } catch (error) {
        console.error('Polling error:', error);
        await sleep(5000);
      }
    }
  }
  
  stop() {
    this.isRunning = false;
  }
  
  async poll() {
    const response = await sqsClient.send(new ReceiveMessageCommand({
      QueueUrl: this.queueUrl,
      MaxNumberOfMessages: 10,
      WaitTimeSeconds: 20, // Long polling
      VisibilityTimeout: 300 // 5 minutes
    }));
    
    if (!response.Messages) {
      return;
    }
    
    // Process messages in parallel
    await Promise.all(
      response.Messages.map(msg => this.processMessage(msg))
    );
  }
  
  async processMessage(message) {
    try {
      const job = JSON.parse(message.Body);
      const handler = this.handlers[job.type];
      
      if (!handler) {
        throw new Error(`No handler for job type: ${job.type}`);
      }
      
      await handler(job.data);
      
      // Delete message (acknowledge)
      await sqsClient.send(new DeleteMessageCommand({
        QueueUrl: this.queueUrl,
        ReceiptHandle: message.ReceiptHandle
      }));
      
      console.log(`Job ${job.id} completed successfully`);
      
    } catch (error) {
      console.error('Job processing failed:', error);
      // Message will become visible again after VisibilityTimeout
      // SQS will retry automatically based on queue settings
    }
  }
}

// Usage
const worker = new SQSWorker(QUEUE_URL, {
  'send-email': async (data) => {
    await emailService.send(data.to, data.subject, data.body);
  },
  'process-image': async (data) => {
    await imageProcessor.resize(data.imageUrl, data.dimensions);
  }
});

worker.start();
```

## Job Patterns

### One-Time Jobs

```javascript
// Simple fire-and-forget
await queue.add('send-email', emailData);

// With result tracking
const job = await queue.add('generate-report', { userId: 123 });
const result = await job.waitUntilFinished();
```

### Scheduled Jobs (Delayed Execution)

```javascript
// Send email in 1 hour
await queue.add('send-email', emailData, {
  delay: 60 * 60 * 1000 // 1 hour in ms
});

// Send reminder at specific time
const reminderTime = new Date('2025-10-23T09:00:00Z');
const delay = reminderTime.getTime() - Date.now();

await queue.add('send-reminder', reminderData, {
  delay: Math.max(0, delay)
});
```

### Recurring Jobs (Cron-like)

```javascript
// Using Bull's repeat option
await queue.add('cleanup-old-data', {}, {
  repeat: {
    cron: '0 2 * * *' // Every day at 2 AM
  }
});

// Send daily report
await queue.add('daily-report', {}, {
  repeat: {
    cron: '0 9 * * 1-5' // Weekdays at 9 AM
  }
});

// Every 15 minutes
await queue.add('health-check', {}, {
  repeat: {
    every: 15 * 60 * 1000 // 15 minutes in ms
  }
});
```

### Batch Jobs

```javascript
// Process multiple items efficiently
async function processBatch(items) {
  const jobs = items.map(item => ({
    name: 'process-item',
    data: item
  }));
  
  await queue.addBulk(jobs);
}

// Worker processes in batches
const worker = new Worker('batch-queue', async (job) => {
  // Group jobs for batch processing
  const batch = await collectBatch(job);
  await processBatchEfficiently(batch);
});

async function collectBatch(firstJob, maxSize = 100, maxWait = 5000) {
  const batch = [firstJob];
  const startTime = Date.now();
  
  while (batch.length < maxSize && Date.now() - startTime < maxWait) {
    const nextJob = await queue.getNextJob();
    if (nextJob) {
      batch.push(nextJob);
    } else {
      break;
    }
  }
  
  return batch;
}
```

### Job Chains (Dependencies)

```javascript
// Sequential chain
const job1 = await queue.add('step1', data);
const job2 = await queue.add('step2', {}, {
  parent: job1.id
});
const job3 = await queue.add('step3', {}, {
  parent: job2.id
});

// Parallel with join
const uploads = [
  queue.add('upload-file', { file: 'file1.jpg' }),
  queue.add('upload-file', { file: 'file2.jpg' }),
  queue.add('upload-file', { file: 'file3.jpg' })
];

const uploadJobs = await Promise.all(uploads);

// Merge results
await queue.add('merge-uploads', {
  uploadIds: uploadJobs.map(j => j.id)
});
```

### Priority Queues

```javascript
// Higher priority = processed first
await queue.add('urgent-email', emailData, {
  priority: 1 // Highest priority
});

await queue.add('newsletter', emailData, {
  priority: 10 // Lower priority
});

// Worker respects priority
const worker = new Worker('emails', processEmail, {
  priorityOrdering: 'ascending' // Lower number = higher priority
});
```

## Job Design Patterns

### Idempotent Jobs

```javascript
// Bad: Not idempotent
async function sendWelcomeEmail(userId) {
  const user = await db.users.findById(userId);
  await emailService.send(user.email, 'Welcome!', '...');
}

// Good: Idempotent with deduplication
async function sendWelcomeEmail(userId, jobId) {
  // Check if already sent
  const sent = await db.sentEmails.exists({
    userId,
    type: 'welcome',
    jobId
  });
  
  if (sent) {
    console.log('Welcome email already sent, skipping');
    return;
  }
  
  const user = await db.users.findById(userId);
  await emailService.send(user.email, 'Welcome!', '...');
  
  // Mark as sent
  await db.sentEmails.create({
    userId,
    type: 'welcome',
    jobId,
    sentAt: new Date()
  });
}
```

### Atomic Jobs with Transactions

```javascript
async function processPayment(orderId, jobId) {
  const transaction = await db.transaction();
  
  try {
    // Check idempotency
    const processed = await transaction.processedJobs.exists({ jobId });
    if (processed) {
      await transaction.rollback();
      return;
    }
    
    // Get order
    const order = await transaction.orders.findById(orderId);
    
    // Charge payment
    const payment = await paymentService.charge(order.amount);
    
    // Update order
    await transaction.orders.update(orderId, {
      status: 'paid',
      paymentId: payment.id
    });
    
    // Mark job as processed
    await transaction.processedJobs.create({ jobId });
    
    // Commit all or nothing
    await transaction.commit();
    
  } catch (error) {
    await transaction.rollback();
    throw error;
  }
}
```

### Progress Tracking

```javascript
async function processLargeFile(fileUrl, job) {
  const chunks = await getFileChunks(fileUrl);
  const total = chunks.length;
  
  for (let i = 0; i < chunks.length; i++) {
    await processChunk(chunks[i]);
    
    // Update progress
    const progress = Math.round(((i + 1) / total) * 100);
    await job.updateProgress(progress);
  }
}

// Client polls for progress
async function checkJobProgress(jobId) {
  const job = await queue.getJob(jobId);
  return {
    status: await job.getState(),
    progress: job.progress
  };
}

// API endpoint
app.get('/api/jobs/:id/progress', async (req, res) => {
  const progress = await checkJobProgress(req.params.id);
  res.json(progress);
});
```

### Job Results Storage

```javascript
// Store results for retrieval
async function generateReport(userId, job) {
  const report = await buildReport(userId);
  
  // Store result
  await job.updateData({
    resultUrl: await uploadReport(report)
  });
  
  return { success: true };
}

// Retrieve result
async function getJobResult(jobId) {
  const job = await queue.getJob(jobId);
  const state = await job.getState();
  
  if (state === 'completed') {
    return job.data.resultUrl;
  } else if (state === 'failed') {
    throw new Error('Job failed');
  } else {
    return { status: state };
  }
}

// API endpoint
app.get('/api/jobs/:id/result', async (req, res) => {
  try {
    const result = await getJobResult(req.params.id);
    res.json({ result });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

## Retry Strategies

### Exponential Backoff

```javascript
// Configure retry with exponential backoff
await queue.add('api-call', data, {
  attempts: 5,
  backoff: {
    type: 'exponential',
    delay: 1000 // Start with 1 second
  }
  // Delays: 1s, 2s, 4s, 8s, 16s
});

// Custom backoff function
await queue.add('custom-retry', data, {
  attempts: 3,
  backoff: {
    type: 'custom',
    delay: (attemptsMade) => {
      // Custom logic
      return Math.min(Math.pow(2, attemptsMade) * 1000, 60000);
    }
  }
});
```

### Selective Retry

```javascript
async function processJob(job) {
  try {
    await riskyOperation(job.data);
    
  } catch (error) {
    // Don't retry validation errors
    if (error instanceof ValidationError) {
      throw new Error('PERMANENT_FAILURE: ' + error.message);
    }
    
    // Don't retry 4xx errors
    if (error.statusCode >= 400 && error.statusCode < 500) {
      throw new Error('PERMANENT_FAILURE: Client error');
    }
    
    // Retry 5xx and network errors
    throw error;
  }
}

// Dead letter queue for permanent failures
worker.on('failed', async (job, error) => {
  if (error.message.startsWith('PERMANENT_FAILURE')) {
    await deadLetterQueue.add('failed-job', {
      originalJob: job.data,
      error: error.message,
      attempts: job.attemptsMade
    });
  }
});
```

### Manual Retry

```javascript
// Allow manual retry of failed jobs
async function retryJob(jobId) {
  const job = await queue.getJob(jobId);
  
  if (!job) {
    throw new Error('Job not found');
  }
  
  const state = await job.getState();
  
  if (state === 'failed') {
    // Reset job and retry
    await job.retry();
    return { status: 'retrying' };
  }
  
  return { status: state };
}

// API endpoint
app.post('/api/jobs/:id/retry', async (req, res) => {
  const result = await retryJob(req.params.id);
  res.json(result);
});
```

## Rate Limiting

### Per-Job Rate Limiting

```javascript
// Limit job processing rate
const rateLimitedQueue = new Queue('rate-limited', {
  limiter: {
    max: 10,        // Max 10 jobs
    duration: 1000  // Per second
  }
});

// Per-key rate limiting (e.g., per user)
await queue.add('send-email', emailData, {
  rateLimiter: {
    max: 5,         // 5 emails
    duration: 60000 // Per minute per user
  },
  rateLimiterKey: userId
});
```

### Token Bucket Rate Limiter

```javascript
class TokenBucketRateLimiter {
  constructor(capacity, refillRate) {
    this.capacity = capacity;
    this.tokens = capacity;
    this.refillRate = refillRate; // Tokens per second
    this.lastRefill = Date.now();
  }
  
  async acquire(tokens = 1) {
    this.refill();
    
    if (this.tokens >= tokens) {
      this.tokens -= tokens;
      return true;
    }
    
    // Wait for tokens
    const needed = tokens - this.tokens;
    const waitTime = (needed / this.refillRate) * 1000;
    
    await sleep(waitTime);
    
    this.refill();
    this.tokens -= tokens;
    return true;
  }
  
  refill() {
    const now = Date.now();
    const elapsed = (now - this.lastRefill) / 1000;
    const tokensToAdd = elapsed * this.refillRate;
    
    this.tokens = Math.min(this.capacity, this.tokens + tokensToAdd);
    this.lastRefill = now;
  }
}

// Usage in worker
const apiLimiter = new TokenBucketRateLimiter(100, 10); // 100 capacity, 10/sec

const worker = new Worker('api-calls', async (job) => {
  await apiLimiter.acquire(); // Wait for token
  await externalAPI.call(job.data);
});
```

## Monitoring & Observability

### Metrics Collection

```javascript
class JobMetrics {
  constructor() {
    this.metrics = {
      processed: 0,
      completed: 0,
      failed: 0,
      processingTime: []
    };
  }
  
  recordStart(jobId) {
    this.metrics.processed++;
    this.startTimes.set(jobId, Date.now());
  }
  
  recordComplete(jobId) {
    this.metrics.completed++;
    
    const startTime = this.startTimes.get(jobId);
    if (startTime) {
      const duration = Date.now() - startTime;
      this.metrics.processingTime.push(duration);
      this.startTimes.delete(jobId);
    }
  }
  
  recordFailure(jobId, error) {
    this.metrics.failed++;
    this.startTimes.delete(jobId);
  }
  
  getStats() {
    const times = this.metrics.processingTime;
    
    return {
      total: this.metrics.processed,
      completed: this.metrics.completed,
      failed: this.metrics.failed,
      successRate: this.metrics.processed > 0
        ? (this.metrics.completed / this.metrics.processed) * 100
        : 0,
      avgProcessingTime: times.length > 0
        ? times.reduce((a, b) => a + b, 0) / times.length
        : 0,
      p95ProcessingTime: this.percentile(times, 95),
      p99ProcessingTime: this.percentile(times, 99)
    };
  }
  
  percentile(arr, p) {
    if (arr.length === 0) return 0;
    const sorted = [...arr].sort((a, b) => a - b);
    const index = Math.ceil((p / 100) * sorted.length) - 1;
    return sorted[index];
  }
  
  startTimes = new Map();
}

// Attach to worker
const metrics = new JobMetrics();

worker.on('active', (job) => {
  metrics.recordStart(job.id);
});

worker.on('completed', (job) => {
  metrics.recordComplete(job.id);
});

worker.on('failed', (job, error) => {
  metrics.recordFailure(job.id, error);
});

// Expose metrics endpoint
app.get('/api/metrics/jobs', (req, res) => {
  res.json(metrics.getStats());
});
```

### Queue Health Monitoring

```javascript
async function checkQueueHealth(queue) {
  const [waiting, active, completed, failed, delayed] = await Promise.all([
    queue.getWaitingCount(),
    queue.getActiveCount(),
    queue.getCompletedCount(),
    queue.getFailedCount(),
    queue.getDelayedCount()
  ]);
  
  const health = {
    status: 'healthy',
    counts: {
      waiting,
      active,
      completed,
      failed,
      delayed
    },
    alerts: []
  };
  
  // Alert on high backlog
  if (waiting > 1000) {
    health.status = 'degraded';
    health.alerts.push('High backlog: ' + waiting + ' waiting jobs');
  }
  
  // Alert on stuck jobs
  if (active > 100) {
    health.status = 'degraded';
    health.alerts.push('Many active jobs: ' + active);
  }
  
  // Alert on high failure rate
  const total = completed + failed;
  if (total > 0 && (failed / total) > 0.1) { // >10% failure rate
    health.status = 'unhealthy';
    health.alerts.push(`High failure rate: ${((failed/total)*100).toFixed(1)}%`);
  }
  
  return health;
}

// Periodic health check
setInterval(async () => {
  const health = await checkQueueHealth(emailQueue);
  
  if (health.status !== 'healthy') {
    console.warn('Queue health issue:', health);
    // Send alert
    await alertService.notify('Queue Health', health);
  }
}, 60000); // Check every minute
```

### Stuck Job Detection

```javascript
async function detectStuckJobs(queue, timeoutMs = 300000) { // 5 minutes
  const activeJobs = await queue.getActive();
  const stuckJobs = [];
  
  for (const job of activeJobs) {
    const age = Date.now() - job.timestamp;
    
    if (age > timeoutMs) {
      stuckJobs.push({
        id: job.id,
        type: job.name,
        age: age,
        data: job.data
      });
    }
  }
  
  if (stuckJobs.length > 0) {
    console.error(`Found ${stuckJobs.length} stuck jobs`);
    
    // Retry or move to failed
    for (const stuck of stuckJobs) {
      const job = await queue.getJob(stuck.id);
      await job.moveToFailed({ message: 'Job timeout' });
    }
  }
  
  return stuckJobs;
}

// Run periodically
setInterval(async () => {
  await detectStuckJobs(queue);
}, 60000);
```

## Scaling Strategies

### Horizontal Scaling (Multiple Workers)

```javascript
// worker.js - Run multiple instances
const worker = new Worker('jobs', processJob, {
  connection: redis,
  concurrency: 10 // Each worker processes 10 jobs concurrently
});

// Start multiple worker processes
// pm2 start worker.js -i 4  // 4 worker processes
// Each process runs 10 concurrent jobs = 40 total concurrency
```

### Priority-Based Routing

```javascript
// High-priority queue with more workers
const highPriorityWorker = new Worker('high-priority', processJob, {
  connection: redis,
  concurrency: 20 // More workers for high priority
});

// Low-priority queue with fewer workers
const lowPriorityWorker = new Worker('low-priority', processJob, {
  connection: redis,
  concurrency: 5 // Fewer workers for low priority
});

// Route based on priority
async function enqueueJob(data, priority) {
  const queueName = priority === 'high' ? 'high-priority' : 'low-priority';
  const queue = queues[queueName];
  
  return await queue.add('process', data);
}
```

### Auto-Scaling Based on Queue Depth

```javascript
class AutoScaler {
  constructor(queue, minWorkers = 1, maxWorkers = 10) {
    this.queue = queue;
    this.minWorkers = minWorkers;
    this.maxWorkers = maxWorkers;
    this.workers = [];
    this.currentWorkers = 0;
  }
  
  async start() {
    // Start minimum workers
    for (let i = 0; i < this.minWorkers; i++) {
      this.addWorker();
    }
    
    // Monitor and scale
    setInterval(() => this.checkAndScale(), 30000); // Every 30 seconds
  }
  
  async checkAndScale() {
    const waiting = await this.queue.getWaitingCount();
    const active = await this.queue.getActiveCount();
    
    const backlog = waiting + active;
    const desiredWorkers = Math.min(
      Math.max(
        Math.ceil(backlog / 100), // 1 worker per 100 jobs
        this.minWorkers
      ),
      this.maxWorkers
    );
    
    if (desiredWorkers > this.currentWorkers) {
      const toAdd = desiredWorkers - this.currentWorkers;
      for (let i = 0; i < toAdd; i++) {
        this.addWorker();
      }
    } else if (desiredWorkers < this.currentWorkers) {
      const toRemove = this.currentWorkers - desiredWorkers;
      for (let i = 0; i < toRemove; i++) {
        this.removeWorker();
      }
    }
  }
  
  addWorker() {
    const worker = new Worker('jobs', processJob, {
      connection: redis,
      concurrency: 5
    });
    
    this.workers.push(worker);
    this.currentWorkers++;
    
    console.log(`Added worker. Total: ${this.currentWorkers}`);
  }
  
  async removeWorker() {
    if (this.workers.length === 0) return;
    
    const worker = this.workers.pop();
    await worker.close();
    this.currentWorkers--;
    
    console.log(`Removed worker. Total: ${this.currentWorkers}`);
  }
}

// Usage
const scaler = new AutoScaler(queue, 2, 20);
scaler.start();
```

## Common Job Types

### Email Sending

```javascript
queue.registerHandler('send-email', async (data) => {
  await emailService.send({
    to: data.to,
    subject: data.subject,
    html: data.html,
    from: data.from || 'noreply@example.com'
  });
});

// Batch emails (newsletter)
queue.registerHandler('send-newsletter', async (data) => {
  const users = await db.users.findAll({ subscribed: true });
  
  // Enqueue individual email jobs
  for (const user of users) {
    await queue.add('send-email', {
      to: user.email,
      subject: data.subject,
      html: personalizeTemplate(data.template, user)
    }, {
      priority: 5 // Lower priority than transactional emails
    });
  }
});
```

### Image Processing

```javascript
queue.registerHandler('process-image', async (data, job) => {
  const image = await downloadImage(data.url);
  
  const sizes = [
    { name: 'thumbnail', width: 150, height: 150 },
    { name: 'medium', width: 600, height: 600 },
    { name: 'large', width: 1200, height: 1200 }
  ];
  
  const results = {};
  
  for (let i = 0; i < sizes.length; i++) {
    const size = sizes[i];
    
    const resized = await sharp(image)
      .resize(size.width, size.height, { fit: 'cover' })
      .toBuffer();
    
    results[size.name] = await uploadImage(resized, `${data.id}_${size.name}.jpg`);
    
    // Update progress
    await job.updateProgress(((i + 1) / sizes.length) * 100);
  }
  
  return results;
});
```

### Report Generation

```javascript
queue.registerHandler('generate-report', async (data, job) => {
  const { userId, reportType, dateRange } = data;
  
  // Fetch data
  await job.updateProgress(10);
  const reportData = await fetchReportData(userId, reportType, dateRange);
  
  // Generate PDF
  await job.updateProgress(50);
  const pdf = await generatePDF(reportData);
  
  // Upload
  await job.updateProgress(90);
  const url = await uploadToS3(pdf, `reports/${userId}/${Date.now()}.pdf`);
  
  // Notify user
  await job.updateProgress(100);
  await notifyUser(userId, url);
  
  return { url };
});
```

### Data Export

```javascript
queue.registerHandler('export-data', async (data, job) => {
  const { userId, exportType } = data;
  
  // Stream data in chunks
  const stream = db.users.streamData(userId);
  const chunks = [];
  
  let processed = 0;
  for await (const chunk of stream) {
    chunks.push(chunk);
    processed += chunk.length;
    await job.updateProgress(Math.min(90, (processed / 10000) * 90));
  }
  
  // Create CSV
  const csv = convertToCSV(chunks);
  const url = await uploadToS3(csv, `exports/${userId}/${Date.now()}.csv`);
  
  await job.updateProgress(100);
  
  // Email download link
  await emailService.send({
    to: data.userEmail,
    subject: 'Your data export is ready',
    html: `Download your export: <a href="${url}">Download</a>`
  });
  
  return { url };
});
```

## Best Practices Checklist

### Design
- [ ] Jobs are idempotent (safe to retry)?
- [ ] Jobs are atomic (all-or-nothing)?
- [ ] Job data is serializable?
- [ ] Job size is reasonable (<1MB)?
- [ ] Failures are handled gracefully?

### Implementation
- [ ] Using appropriate queue technology?
- [ ] Retry strategy configured?
- [ ] Dead letter queue set up?
- [ ] Progress tracking for long jobs?
- [ ] Rate limiting implemented?

### Operations
- [ ] Monitoring and metrics in place?
- [ ] Alerting on failures?
- [ ] Queue health checks?
- [ ] Stuck job detection?
- [ ] Capacity planning done?

### Performance
- [ ] Appropriate concurrency level?
- [ ] Batch processing for efficiency?
- [ ] Connection pooling used?
- [ ] Resource cleanup on completion?
- [ ] Scaling strategy defined?

## Integration with Other Skills

**Combines well with:**
- **integration-patterns** - Async communication patterns
- **error-handling** - Job failure handling
- **database-schema-design** - Job result storage
- **critical-thinking** - Choose queue technology

**When both active:**
Use critical thinking to design job system architecture, then apply specific patterns from this skill.