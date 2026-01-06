---
name: integration-patterns
description: Comprehensive system integration patterns covering REST APIs, webhooks, message queues, event-driven architecture, ETL/ELT, and service communication. Use when designing integrations between systems, choosing communication patterns, implementing data pipelines, handling distributed transactions, or building microservices communication.
---

# Integration Patterns

Comprehensive framework for designing reliable, scalable integrations between systems and services.

## When to Use

Apply this skill when:
- Integrating third-party APIs or services
- Designing microservices communication
- Building event-driven architectures
- Implementing data synchronization
- Creating webhook systems
- Designing message queue architectures
- Handling distributed transactions
- Building ETL/ELT pipelines
- Managing API rate limits and retries
- Implementing circuit breakers and resilience patterns

## Core Principles

### 1. Loose Coupling
- Systems should not be tightly dependent
- Changes in one system shouldn't break others
- Use contracts/schemas for communication

### 2. Idempotency
- Operations should be safely retryable
- Same request multiple times = same result
- Critical for reliability

### 3. Eventual Consistency
- Accept that distributed systems can't be immediately consistent
- Design for temporary inconsistency
- Provide reconciliation mechanisms

### 4. Graceful Degradation
- System continues functioning when integrations fail
- Circuit breakers prevent cascading failures
- Fallback mechanisms for critical paths

## Integration Patterns Overview

### Synchronous Patterns

**Request-Response (REST, gRPC)**
- Direct communication
- Immediate response expected
- Tight coupling
- Blocking

### Asynchronous Patterns

**Message Queue (RabbitMQ, SQS)**
- Fire and forget
- Decoupled systems
- Guaranteed delivery
- Load leveling

**Pub/Sub (Kafka, SNS, Redis)**
- One-to-many communication
- Event broadcasting
- Time decoupling
- Scalable

**Webhooks**
- Push notifications
- Event-driven
- HTTP callbacks
- Simple integration

## REST API Integration

### Making API Requests

**Best practices:**

```javascript
// Retry logic with exponential backoff
async function callAPIWithRetry(url, options, maxRetries = 3) {
  let lastError;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${API_KEY}`,
          'X-Request-ID': generateRequestId(),
          ...options.headers
        }
      });
      
      // Handle rate limiting
      if (response.status === 429) {
        const retryAfter = response.headers.get('Retry-After') || Math.pow(2, i);
        await sleep(retryAfter * 1000);
        continue;
      }
      
      // Handle server errors with retry
      if (response.status >= 500) {
        await sleep(Math.pow(2, i) * 1000);
        continue;
      }
      
      // Handle client errors (don't retry)
      if (response.status >= 400) {
        throw new Error(`API error: ${response.status}`);
      }
      
      return await response.json();
      
    } catch (error) {
      lastError = error;
      if (i < maxRetries - 1) {
        await sleep(Math.pow(2, i) * 1000);
      }
    }
  }
  
  throw lastError;
}

function generateRequestId() {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

**Idempotency keys:**

```javascript
// For POST/PUT/PATCH requests that modify data
async function createOrder(orderData) {
  const idempotencyKey = generateIdempotencyKey(orderData);
  
  const response = await fetch('/api/orders', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': idempotencyKey
    },
    body: JSON.stringify(orderData)
  });
  
  return response.json();
}

function generateIdempotencyKey(data) {
  // Hash of data + timestamp (within window)
  return `${hash(JSON.stringify(data))}_${Math.floor(Date.now() / 60000)}`;
}
```

**Rate limiting handling:**

```javascript
class APIClient {
  constructor(baseURL, rateLimit = { requests: 100, window: 60000 }) {
    this.baseURL = baseURL;
    this.rateLimit = rateLimit;
    this.requestTimes = [];
  }
  
  async request(endpoint, options) {
    await this.throttle();
    return fetch(`${this.baseURL}${endpoint}`, options);
  }
  
  async throttle() {
    const now = Date.now();
    const windowStart = now - this.rateLimit.window;
    
    // Remove old requests outside window
    this.requestTimes = this.requestTimes.filter(t => t > windowStart);
    
    if (this.requestTimes.length >= this.rateLimit.requests) {
      const oldestRequest = this.requestTimes[0];
      const waitTime = oldestRequest + this.rateLimit.window - now;
      await sleep(waitTime);
    }
    
    this.requestTimes.push(now);
  }
}
```

### Pagination Strategies

**Cursor-based (recommended for large datasets):**

```javascript
async function fetchAllUsers() {
  const allUsers = [];
  let cursor = null;
  
  do {
    const response = await fetch(
      `/api/users?limit=100${cursor ? `&cursor=${cursor}` : ''}`
    );
    const data = await response.json();
    
    allUsers.push(...data.users);
    cursor = data.next_cursor;
    
  } while (cursor);
  
  return allUsers;
}
```

**Page-based:**

```javascript
async function fetchAllProducts() {
  const allProducts = [];
  let page = 1;
  let hasMore = true;
  
  while (hasMore) {
    const response = await fetch(`/api/products?page=${page}&per_page=50`);
    const data = await response.json();
    
    allProducts.push(...data.products);
    hasMore = page < data.total_pages;
    page++;
  }
  
  return allProducts;
}
```

## Webhooks

### Implementing Webhook Consumer

**Secure webhook handling:**

```javascript
import crypto from 'crypto';

// Verify webhook signature
function verifyWebhookSignature(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}

// Webhook endpoint
app.post('/webhooks/stripe', async (req, res) => {
  const signature = req.headers['stripe-signature'];
  const payload = req.rawBody; // Important: use raw body
  
  // Verify signature
  if (!verifyWebhookSignature(payload, signature, WEBHOOK_SECRET)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }
  
  // Respond quickly (< 3 seconds)
  res.status(200).json({ received: true });
  
  // Process asynchronously
  const event = JSON.parse(payload);
  processWebhookAsync(event).catch(error => {
    console.error('Webhook processing failed:', error);
    // Queue for retry
  });
});

async function processWebhookAsync(event) {
  // Idempotency check
  const processed = await checkIfProcessed(event.id);
  if (processed) {
    console.log(`Event ${event.id} already processed`);
    return;
  }
  
  try {
    switch (event.type) {
      case 'payment.succeeded':
        await handlePaymentSucceeded(event.data);
        break;
      case 'payment.failed':
        await handlePaymentFailed(event.data);
        break;
      default:
        console.log(`Unhandled event type: ${event.type}`);
    }
    
    // Mark as processed
    await markAsProcessed(event.id);
    
  } catch (error) {
    // Log and queue for retry
    console.error(`Failed to process event ${event.id}:`, error);
    await queueForRetry(event);
  }
}
```

**Webhook retry logic:**

```javascript
class WebhookRetryQueue {
  constructor(maxRetries = 5) {
    this.maxRetries = maxRetries;
    this.queue = [];
  }
  
  async retry(event, attempt = 0) {
    if (attempt >= this.maxRetries) {
      console.error(`Event ${event.id} failed after ${attempt} attempts`);
      await moveToDeadLetterQueue(event);
      return;
    }
    
    // Exponential backoff: 1s, 2s, 4s, 8s, 16s
    const delay = Math.pow(2, attempt) * 1000;
    
    await sleep(delay);
    
    try {
      await processWebhookAsync(event);
    } catch (error) {
      console.error(`Retry ${attempt + 1} failed:`, error);
      await this.retry(event, attempt + 1);
    }
  }
}
```

### Implementing Webhook Provider

**Sending webhooks:**

```javascript
class WebhookService {
  constructor() {
    this.subscribers = new Map(); // url -> { secret, events }
  }
  
  async send(event, data) {
    const subscribers = Array.from(this.subscribers.entries())
      .filter(([url, config]) => config.events.includes(event));
    
    const promises = subscribers.map(([url, config]) => 
      this.sendWebhook(url, config.secret, event, data)
    );
    
    await Promise.allSettled(promises);
  }
  
  async sendWebhook(url, secret, event, data, attempt = 0) {
    const payload = JSON.stringify({
      id: generateEventId(),
      type: event,
      data: data,
      timestamp: new Date().toISOString()
    });
    
    const signature = crypto
      .createHmac('sha256', secret)
      .update(payload)
      .digest('hex');
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Webhook-Signature': signature,
          'X-Webhook-Event': event
        },
        body: payload,
        timeout: 5000 // 5 second timeout
      });
      
      if (!response.ok && attempt < 5) {
        // Retry with exponential backoff
        await sleep(Math.pow(2, attempt) * 1000);
        return this.sendWebhook(url, secret, event, data, attempt + 1);
      }
      
      return response;
      
    } catch (error) {
      console.error(`Failed to send webhook to ${url}:`, error);
      
      if (attempt < 5) {
        await sleep(Math.pow(2, attempt) * 1000);
        return this.sendWebhook(url, secret, event, data, attempt + 1);
      }
      
      // Move to dead letter queue after max retries
      await this.handleFailedWebhook(url, event, data, error);
    }
  }
  
  async handleFailedWebhook(url, event, data, error) {
    // Log failure
    console.error(`Webhook permanently failed: ${url} ${event}`);
    
    // Optionally disable webhook after repeated failures
    // Notify subscriber about failures
  }
}
```

## Message Queues

### Producer Pattern

**Publishing to queue:**

```javascript
// Using AWS SQS
import { SQSClient, SendMessageCommand } from '@aws-sdk/client-sqs';

class QueueProducer {
  constructor(queueUrl) {
    this.client = new SQSClient({});
    this.queueUrl = queueUrl;
  }
  
  async publish(message, options = {}) {
    const command = new SendMessageCommand({
      QueueUrl: this.queueUrl,
      MessageBody: JSON.stringify(message),
      DelaySeconds: options.delaySeconds || 0,
      MessageAttributes: {
        timestamp: {
          DataType: 'Number',
          StringValue: Date.now().toString()
        },
        messageType: {
          DataType: 'String',
          StringValue: options.type || 'default'
        }
      }
    });
    
    try {
      const response = await this.client.send(command);
      console.log(`Message published: ${response.MessageId}`);
      return response.MessageId;
    } catch (error) {
      console.error('Failed to publish message:', error);
      throw error;
    }
  }
  
  async publishBatch(messages) {
    // SQS supports up to 10 messages per batch
    const batches = chunk(messages, 10);
    
    for (const batch of batches) {
      const entries = batch.map((msg, i) => ({
        Id: i.toString(),
        MessageBody: JSON.stringify(msg)
      }));
      
      await this.client.send(new SendMessageBatchCommand({
        QueueUrl: this.queueUrl,
        Entries: entries
      }));
    }
  }
}
```

### Consumer Pattern

**Processing from queue:**

```javascript
import { ReceiveMessageCommand, DeleteMessageCommand } from '@aws-sdk/client-sqs';

class QueueConsumer {
  constructor(queueUrl, handler) {
    this.client = new SQSClient({});
    this.queueUrl = queueUrl;
    this.handler = handler;
    this.isRunning = false;
  }
  
  async start() {
    this.isRunning = true;
    
    while (this.isRunning) {
      try {
        await this.poll();
      } catch (error) {
        console.error('Polling error:', error);
        await sleep(5000); // Wait before retrying
      }
    }
  }
  
  stop() {
    this.isRunning = false;
  }
  
  async poll() {
    const command = new ReceiveMessageCommand({
      QueueUrl: this.queueUrl,
      MaxNumberOfMessages: 10,
      WaitTimeSeconds: 20, // Long polling
      VisibilityTimeout: 30
    });
    
    const response = await this.client.send(command);
    
    if (!response.Messages || response.Messages.length === 0) {
      return;
    }
    
    // Process messages in parallel
    await Promise.all(
      response.Messages.map(msg => this.processMessage(msg))
    );
  }
  
  async processMessage(message) {
    try {
      const body = JSON.parse(message.Body);
      
      // Process message
      await this.handler(body);
      
      // Delete message from queue (acknowledge)
      await this.client.send(new DeleteMessageCommand({
        QueueUrl: this.queueUrl,
        ReceiptHandle: message.ReceiptHandle
      }));
      
    } catch (error) {
      console.error('Failed to process message:', error);
      // Message will become visible again after VisibilityTimeout
      // Consider moving to DLQ after max retries
    }
  }
}

// Usage
const consumer = new QueueConsumer(QUEUE_URL, async (message) => {
  console.log('Processing:', message);
  await processOrder(message);
});

consumer.start();
```

### Dead Letter Queue Pattern

```javascript
class QueueWithDLQ {
  constructor(mainQueueUrl, dlqUrl) {
    this.mainQueue = new QueueConsumer(mainQueueUrl, this.processMessage.bind(this));
    this.dlqUrl = dlqUrl;
    this.maxRetries = 3;
  }
  
  async processMessage(message) {
    const retryCount = message.retryCount || 0;
    
    try {
      await processBusinessLogic(message);
      
    } catch (error) {
      if (retryCount >= this.maxRetries) {
        // Move to DLQ
        await this.sendToDLQ(message, error);
      } else {
        // Re-throw to let queue re-deliver
        message.retryCount = retryCount + 1;
        throw error;
      }
    }
  }
  
  async sendToDLQ(message, error) {
    await sendToQueue(this.dlqUrl, {
      originalMessage: message,
      error: error.message,
      failedAt: new Date().toISOString(),
      retryCount: message.retryCount
    });
    
    console.error(`Message moved to DLQ after ${message.retryCount} retries`);
  }
}
```

## Pub/Sub (Event-Driven)

### Publishing Events

```javascript
// Using AWS SNS
import { SNSClient, PublishCommand } from '@aws-sdk/client-sns';

class EventPublisher {
  constructor(topicArn) {
    this.client = new SNSClient({});
    this.topicArn = topicArn;
  }
  
  async publish(eventType, data) {
    const event = {
      id: generateEventId(),
      type: eventType,
      timestamp: new Date().toISOString(),
      data: data
    };
    
    const command = new PublishCommand({
      TopicArn: this.topicArn,
      Message: JSON.stringify(event),
      MessageAttributes: {
        eventType: {
          DataType: 'String',
          StringValue: eventType
        }
      }
    });
    
    const response = await this.client.send(command);
    console.log(`Event published: ${response.MessageId}`);
    return response.MessageId;
  }
}

// Usage
const publisher = new EventPublisher(TOPIC_ARN);

await publisher.publish('order.created', {
  orderId: '123',
  customerId: '456',
  total: 99.99
});
```

### Subscribing to Events

```javascript
class EventSubscriber {
  constructor() {
    this.handlers = new Map(); // eventType -> handler[]
  }
  
  on(eventType, handler) {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, []);
    }
    this.handlers.get(eventType).push(handler);
  }
  
  async handle(event) {
    const handlers = this.handlers.get(event.type) || [];
    
    // Execute handlers in parallel
    const results = await Promise.allSettled(
      handlers.map(handler => handler(event.data))
    );
    
    // Log failures
    results.forEach((result, i) => {
      if (result.status === 'rejected') {
        console.error(`Handler ${i} failed:`, result.reason);
      }
    });
  }
}

// Usage
const subscriber = new EventSubscriber();

subscriber.on('order.created', async (data) => {
  await sendConfirmationEmail(data.customerId, data.orderId);
});

subscriber.on('order.created', async (data) => {
  await updateInventory(data.items);
});

subscriber.on('order.created', async (data) => {
  await notifyWarehouse(data.orderId);
});
```

## Saga Pattern (Distributed Transactions)

### Choreography-Based Saga

```javascript
// Each service publishes events and listens to others
class OrderService {
  async createOrder(orderData) {
    // Create order
    const order = await db.orders.create({
      ...orderData,
      status: 'pending'
    });
    
    // Publish event
    await eventBus.publish('order.created', {
      orderId: order.id,
      customerId: order.customerId,
      items: order.items,
      total: order.total
    });
    
    return order;
  }
  
  // Listen for payment events
  async onPaymentSucceeded(data) {
    await db.orders.update(data.orderId, {
      status: 'paid',
      paidAt: new Date()
    });
    
    await eventBus.publish('order.paid', {
      orderId: data.orderId
    });
  }
  
  async onPaymentFailed(data) {
    await db.orders.update(data.orderId, {
      status: 'cancelled',
      cancelledAt: new Date(),
      cancelReason: 'payment_failed'
    });
    
    await eventBus.publish('order.cancelled', {
      orderId: data.orderId,
      reason: 'payment_failed'
    });
  }
}

class PaymentService {
  // Listen for order events
  async onOrderCreated(data) {
    try {
      const payment = await processPayment({
        customerId: data.customerId,
        amount: data.total
      });
      
      await eventBus.publish('payment.succeeded', {
        orderId: data.orderId,
        paymentId: payment.id
      });
      
    } catch (error) {
      await eventBus.publish('payment.failed', {
        orderId: data.orderId,
        error: error.message
      });
    }
  }
}

class InventoryService {
  async onOrderPaid(data) {
    try {
      await reserveInventory(data.orderId);
      
      await eventBus.publish('inventory.reserved', {
        orderId: data.orderId
      });
      
    } catch (error) {
      // Compensating transaction
      await eventBus.publish('inventory.reservation_failed', {
        orderId: data.orderId
      });
    }
  }
  
  async onOrderCancelled(data) {
    // Compensating transaction
    await releaseInventory(data.orderId);
  }
}
```

### Orchestration-Based Saga

```javascript
class OrderSagaOrchestrator {
  async executeOrderSaga(orderData) {
    const sagaId = generateSagaId();
    const state = {
      sagaId,
      status: 'started',
      completedSteps: [],
      orderData
    };
    
    try {
      // Step 1: Create order
      const order = await this.createOrder(orderData);
      state.completedSteps.push('create_order');
      state.orderId = order.id;
      
      // Step 2: Process payment
      const payment = await this.processPayment(order);
      state.completedSteps.push('process_payment');
      state.paymentId = payment.id;
      
      // Step 3: Reserve inventory
      await this.reserveInventory(order);
      state.completedSteps.push('reserve_inventory');
      
      // Step 4: Notify shipping
      await this.notifyShipping(order);
      state.completedSteps.push('notify_shipping');
      
      state.status = 'completed';
      await this.saveSagaState(state);
      
      return { success: true, orderId: order.id };
      
    } catch (error) {
      console.error('Saga failed:', error);
      
      // Compensate completed steps in reverse order
      await this.compensate(state);
      
      state.status = 'compensated';
      state.error = error.message;
      await this.saveSagaState(state);
      
      return { success: false, error: error.message };
    }
  }
  
  async compensate(state) {
    const steps = [...state.completedSteps].reverse();
    
    for (const step of steps) {
      try {
        switch (step) {
          case 'notify_shipping':
            await this.cancelShipping(state.orderId);
            break;
          case 'reserve_inventory':
            await this.releaseInventory(state.orderId);
            break;
          case 'process_payment':
            await this.refundPayment(state.paymentId);
            break;
          case 'create_order':
            await this.cancelOrder(state.orderId);
            break;
        }
      } catch (error) {
        console.error(`Compensation failed for step ${step}:`, error);
        // Log and alert - manual intervention may be needed
      }
    }
  }
}
```

## Circuit Breaker Pattern

```javascript
class CircuitBreaker {
  constructor(service, options = {}) {
    this.service = service;
    this.failureThreshold = options.failureThreshold || 5;
    this.resetTimeout = options.resetTimeout || 60000; // 1 minute
    this.monitoringWindow = options.monitoringWindow || 10000; // 10 seconds
    
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    this.failures = [];
    this.lastFailureTime = null;
  }
  
  async call(method, ...args) {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime >= this.resetTimeout) {
        this.state = 'HALF_OPEN';
        console.log('Circuit breaker: OPEN -> HALF_OPEN');
      } else {
        throw new Error('Circuit breaker is OPEN');
      }
    }
    
    try {
      const result = await this.service[method](...args);
      this.onSuccess();
      return result;
      
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }
  
  onSuccess() {
    if (this.state === 'HALF_OPEN') {
      this.state = 'CLOSED';
      this.failures = [];
      console.log('Circuit breaker: HALF_OPEN -> CLOSED');
    }
  }
  
  onFailure() {
    this.lastFailureTime = Date.now();
    this.failures.push(Date.now());
    
    // Remove old failures outside monitoring window
    const windowStart = Date.now() - this.monitoringWindow;
    this.failures = this.failures.filter(t => t > windowStart);
    
    if (this.failures.length >= this.failureThreshold && this.state === 'CLOSED') {
      this.state = 'OPEN';
      console.log(`Circuit breaker: CLOSED -> OPEN (${this.failures.length} failures)`);
    }
  }
  
  getState() {
    return this.state;
  }
  
  reset() {
    this.state = 'CLOSED';
    this.failures = [];
    this.lastFailureTime = null;
  }
}

// Usage
const paymentService = new PaymentService();
const breaker = new CircuitBreaker(paymentService, {
  failureThreshold: 5,
  resetTimeout: 60000
});

try {
  const result = await breaker.call('processPayment', paymentData);
} catch (error) {
  if (error.message === 'Circuit breaker is OPEN') {
    // Use fallback or queue for later
    await queuePaymentForLater(paymentData);
  }
}
```

## ETL/ELT Patterns

### Extract-Transform-Load (ETL)

```javascript
class ETLPipeline {
  constructor(source, destination) {
    this.source = source;
    this.destination = destination;
    this.transformers = [];
  }
  
  addTransformer(transformer) {
    this.transformers.push(transformer);
    return this;
  }
  
  async run(options = {}) {
    const batchSize = options.batchSize || 100;
    let offset = 0;
    let processedCount = 0;
    
    while (true) {
      // Extract
      const batch = await this.extract(offset, batchSize);
      
      if (batch.length === 0) {
        break;
      }
      
      // Transform
      const transformed = await this.transform(batch);
      
      // Load
      await this.load(transformed);
      
      processedCount += batch.length;
      offset += batchSize;
      
      console.log(`Processed ${processedCount} records`);
      
      // Rate limiting
      if (options.delayMs) {
        await sleep(options.delayMs);
      }
    }
    
    return { processedCount };
  }
  
  async extract(offset, limit) {
    return await this.source.fetch({ offset, limit });
  }
  
  async transform(records) {
    let transformed = records;
    
    for (const transformer of this.transformers) {
      transformed = await Promise.all(
        transformed.map(record => transformer(record))
      );
    }
    
    return transformed;
  }
  
  async load(records) {
    await this.destination.bulkInsert(records);
  }
}

// Usage
const pipeline = new ETLPipeline(legacyDB, modernDB);

pipeline
  .addTransformer(record => ({
    ...record,
    email: record.email.toLowerCase(),
    createdAt: new Date(record.created_at)
  }))
  .addTransformer(async record => {
    const enriched = await enrichWithExternalData(record.id);
    return { ...record, ...enriched };
  });

await pipeline.run({ batchSize: 500, delayMs: 100 });
```

### Change Data Capture (CDC)

```javascript
class CDCProcessor {
  constructor(source, handlers) {
    this.source = source;
    this.handlers = handlers;
    this.lastPosition = null;
  }
  
  async start() {
    // Load last position from checkpoint
    this.lastPosition = await this.loadCheckpoint();
    
    while (true) {
      const changes = await this.source.getChanges(this.lastPosition);
      
      for (const change of changes) {
        await this.processChange(change);
      }
      
      if (changes.length > 0) {
        this.lastPosition = changes[changes.length - 1].position;
        await this.saveCheckpoint(this.lastPosition);
      }
      
      await sleep(1000); // Poll interval
    }
  }
  
  async processChange(change) {
    const handler = this.handlers[change.operation];
    
    if (handler) {
      try {
        await handler(change.data, change.before);
      } catch (error) {
        console.error('Failed to process change:', error);
        // Queue for retry or DLQ
      }
    }
  }
  
  async loadCheckpoint() {
    // Load from persistent storage
    return await db.get('cdc_checkpoint');
  }
  
  async saveCheckpoint(position) {
    await db.set('cdc_checkpoint', position);
  }
}

// Usage
const cdc = new CDCProcessor(database, {
  INSERT: async (data) => {
    await searchIndex.add(data);
    await cache.invalidate(data.id);
  },
  UPDATE: async (data, before) => {
    await searchIndex.update(data);
    await cache.invalidate(data.id);
  },
  DELETE: async (data) => {
    await searchIndex.remove(data.id);
    await cache.invalidate(data.id);
  }
});

cdc.start();
```

## Polling vs Push

### Polling Pattern

```javascript
class PollingService {
  constructor(checkFn, interval = 5000) {
    this.checkFn = checkFn;
    this.interval = interval;
    this.isRunning = false;
  }
  
  start() {
    this.isRunning = true;
    this.poll();
  }
  
  stop() {
    this.isRunning = false;
  }
  
  async poll() {
    while (this.isRunning) {
      try {
        const hasChanges = await this.checkFn();
        
        if (hasChanges) {
          console.log('Changes detected');
          // Process changes
        }
        
      } catch (error) {
        console.error('Polling error:', error);
      }
      
      await sleep(this.interval);
    }
  }
}

// Usage: Poll for order status updates
const poller = new PollingService(async () => {
  const orders = await db.orders.findPending();
  
  for (const order of orders) {
    const status = await externalAPI.checkOrderStatus(order.externalId);
    
    if (status !== order.status) {
      await db.orders.update(order.id, { status });
      return true;
    }
  }
  
  return false;
}, 10000);

poller.start();
```

### Long Polling

```javascript
app.get('/api/notifications/poll', async (req, res) => {
  const userId = req.user.id;
  const timeout = 30000; // 30 seconds
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    const notifications = await db.notifications
      .where({ userId, read: false })
      .limit(10);
    
    if (notifications.length > 0) {
      return res.json({ notifications });
    }
    
    // Wait a bit before checking again
    await sleep(1000);
  }
  
  // Timeout - return empty
  res.json({ notifications: [] });
});
```

## Idempotency Patterns

### Idempotent Consumer

```javascript
class IdempotentConsumer {
  constructor(handler) {
    this.handler = handler;
    this.processedIds = new Set();
  }
  
  async process(message) {
    const messageId = message.id || generateMessageId(message);
    
    // Check if already processed
    const alreadyProcessed = await this.isProcessed(messageId);
    
    if (alreadyProcessed) {
      console.log(`Message ${messageId} already processed, skipping`);
      return { status: 'duplicate' };
    }
    
    try {
      // Process message
      const result = await this.handler(message);
      
      // Mark as processed
      await this.markAsProcessed(messageId, result);
      
      return { status: 'success', result };
      
    } catch (error) {
      console.error(`Failed to process message ${messageId}:`, error);
      throw error;
    }
  }
  
  async isProcessed(messageId) {
    // Check in database or cache
    return await db.processedMessages.exists(messageId);
  }
  
  async markAsProcessed(messageId, result) {
    await db.processedMessages.create({
      id: messageId,
      processedAt: new Date(),
      result: JSON.stringify(result)
    });
  }
}
```

## Integration Patterns Checklist

### Design Phase
- [ ] Chosen appropriate pattern (sync vs async)?
- [ ] Considered failure modes?
- [ ] Designed for idempotency?
- [ ] Planned retry strategy?
- [ ] Considered rate limits?
- [ ] Defined timeout policies?

### Implementation Phase
- [ ] Implemented retry with exponential backoff?
- [ ] Added circuit breaker if needed?
- [ ] Implemented idempotency checking?
- [ ] Added request ID tracing?
- [ ] Implemented dead letter queue?
- [ ] Added monitoring and alerting?

### Security Phase
- [ ] Verified webhook signatures?
- [ ] Used API keys securely?
- [ ] Encrypted sensitive data?
- [ ] Implemented rate limiting?
- [ ] Validated all inputs?

## Common Pitfalls

### 1. No Idempotency
**Problem:** Duplicate messages cause duplicate processing  
**Solution:** Use idempotency keys, check before processing

### 2. No Retry Logic
**Problem:** Temporary failures cause permanent data loss  
**Solution:** Implement exponential backoff, use queues

### 3. Cascading Failures
**Problem:** One service failure brings down entire system  
**Solution:** Circuit breakers, timeouts, fallbacks

### 4. No Dead Letter Queue
**Problem:** Poison messages block queue forever  
**Solution:** Move failed messages to DLQ after max retries

### 5. Tight Coupling
**Problem:** Changes in one service break others  
**Solution:** Async communication, versioned contracts

## Integration with Other Skills

**Combines well with:**
- **api-design** - REST API integration patterns
- **database-schema-design** - Data synchronization patterns
- **critical-thinking** - Evaluate integration trade-offs
- **debugging-methodology** - Debug integration failures

**When both active:**
Use critical thinking for pattern selection, then apply specific implementation from this skill.