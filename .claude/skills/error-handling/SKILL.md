---
name: error-handling
description: Comprehensive error handling strategies for robust applications. Covers error types, try-catch patterns, custom errors, logging, monitoring, user-facing errors, retry strategies, graceful degradation, and error recovery. Use when implementing error handling, debugging production issues, designing fault-tolerant systems, or improving error messages.
---

# Error Handling

Comprehensive framework for handling errors gracefully, logging effectively, and building resilient applications.

## When to Use

Apply this skill when:
- Implementing error handling in code
- Designing error responses for APIs
- Creating user-facing error messages
- Setting up logging and monitoring
- Debugging production issues
- Building fault-tolerant systems
- Handling asynchronous errors
- Implementing retry strategies
- Designing error recovery mechanisms

## Core Principles

### 1. Fail Fast, Recover Gracefully
- Detect errors early
- Don't hide problems
- Provide recovery mechanisms
- Degrade gracefully when possible

### 2. Clear Error Messages
- Describe what happened
- Explain why it happened (when safe)
- Suggest how to fix it
- Include relevant context

### 3. Log for Debugging, Not Just Recording
- Log actionable information
- Include context (user ID, request ID, timestamp)
- Use appropriate log levels
- Protect sensitive data

### 4. Handle Errors at the Right Level
- Catch errors where you can handle them
- Let errors bubble up if you can't
- Don't catch just to re-throw
- Use global handlers as last resort

## Error Types

### 1. Expected Errors (Business Logic)

**Validation errors:**
```javascript
class ValidationError extends Error {
  constructor(message, field, value) {
    super(message);
    this.name = 'ValidationError';
    this.field = field;
    this.value = value;
    this.code = 'VALIDATION_ERROR';
  }
}

function validateEmail(email) {
  if (!email) {
    throw new ValidationError('Email is required', 'email', email);
  }
  
  if (!email.includes('@')) {
    throw new ValidationError('Email must be valid', 'email', email);
  }
}

// Usage
try {
  validateEmail(userInput);
} catch (error) {
  if (error instanceof ValidationError) {
    return res.status(422).json({
      error: {
        code: error.code,
        message: error.message,
        field: error.field
      }
    });
  }
  throw error;
}
```

**Business rule violations:**
```javascript
class BusinessRuleError extends Error {
  constructor(message, code) {
    super(message);
    this.name = 'BusinessRuleError';
    this.code = code;
  }
}

async function withdrawMoney(accountId, amount) {
  const account = await getAccount(accountId);
  
  if (account.balance < amount) {
    throw new BusinessRuleError(
      'Insufficient funds',
      'INSUFFICIENT_FUNDS'
    );
  }
  
  if (amount > account.dailyLimit) {
    throw new BusinessRuleError(
      'Amount exceeds daily limit',
      'DAILY_LIMIT_EXCEEDED'
    );
  }
  
  // Process withdrawal
}
```

### 2. Unexpected Errors (System/External)

**Network errors:**
```javascript
class NetworkError extends Error {
  constructor(message, originalError, url) {
    super(message);
    this.name = 'NetworkError';
    this.originalError = originalError;
    this.url = url;
    this.code = 'NETWORK_ERROR';
  }
}

async function fetchData(url) {
  try {
    const response = await fetch(url);
    return await response.json();
  } catch (error) {
    throw new NetworkError(
      `Failed to fetch from ${url}`,
      error,
      url
    );
  }
}
```

**Database errors:**
```javascript
class DatabaseError extends Error {
  constructor(message, operation, originalError) {
    super(message);
    this.name = 'DatabaseError';
    this.operation = operation;
    this.originalError = originalError;
    this.code = 'DATABASE_ERROR';
  }
}

async function createUser(userData) {
  try {
    return await db.users.create(userData);
  } catch (error) {
    if (error.code === '23505') { // Unique violation
      throw new ValidationError('Email already exists', 'email', userData.email);
    }
    
    throw new DatabaseError(
      'Failed to create user',
      'INSERT',
      error
    );
  }
}
```

**External service errors:**
```javascript
class ExternalServiceError extends Error {
  constructor(service, operation, statusCode, originalError) {
    super(`${service} ${operation} failed`);
    this.name = 'ExternalServiceError';
    this.service = service;
    this.operation = operation;
    this.statusCode = statusCode;
    this.originalError = originalError;
    this.code = 'EXTERNAL_SERVICE_ERROR';
  }
}

async function chargePayment(paymentData) {
  try {
    const response = await stripe.charges.create(paymentData);
    return response;
  } catch (error) {
    throw new ExternalServiceError(
      'Stripe',
      'create_charge',
      error.statusCode,
      error
    );
  }
}
```

### 3. Programmer Errors (Bugs)

**These should crash the application:**
```javascript
// Type errors
function calculateTotal(items) {
  if (!Array.isArray(items)) {
    throw new TypeError('items must be an array');
  }
  
  return items.reduce((sum, item) => {
    if (typeof item.price !== 'number') {
      throw new TypeError('item.price must be a number');
    }
    return sum + item.price;
  }, 0);
}

// Assertion errors
function divide(a, b) {
  console.assert(b !== 0, 'Division by zero');
  return a / b;
}

// Unreachable code
function handleStatus(status) {
  switch (status) {
    case 'pending':
      return 'Processing...';
    case 'complete':
      return 'Done!';
    case 'failed':
      return 'Failed';
    default:
      throw new Error(`Unexpected status: ${status}`);
  }
}
```

## Error Handling Patterns

### Try-Catch-Finally

```javascript
async function processOrder(orderId) {
  let transaction;
  
  try {
    // Start transaction
    transaction = await db.transaction();
    
    // Get order
    const order = await db.orders.findById(orderId);
    if (!order) {
      throw new NotFoundError('Order not found', orderId);
    }
    
    // Validate
    if (order.status !== 'pending') {
      throw new BusinessRuleError(
        'Order already processed',
        'ORDER_ALREADY_PROCESSED'
      );
    }
    
    // Process payment
    const payment = await chargePayment(order.paymentMethod, order.total);
    
    // Update order
    await db.orders.update(orderId, {
      status: 'paid',
      paymentId: payment.id
    });
    
    // Commit transaction
    await transaction.commit();
    
    return { success: true, orderId };
    
  } catch (error) {
    // Rollback on any error
    if (transaction) {
      await transaction.rollback();
    }
    
    // Log error with context
    logger.error('Order processing failed', {
      orderId,
      error: error.message,
      stack: error.stack
    });
    
    // Re-throw to be handled by caller
    throw error;
    
  } finally {
    // Cleanup resources (always runs)
    if (transaction) {
      await transaction.release();
    }
  }
}
```

### Error Boundaries (React)

```javascript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    // Log to error reporting service
    logErrorToService(error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="error-container">
          <h2>Something went wrong</h2>
          <p>We've been notified and are looking into it.</p>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }
    
    return this.props.children;
  }
}

// Usage
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

### Global Error Handlers

**Express.js:**
```javascript
// Error handling middleware (must be last)
app.use((err, req, res, next) => {
  // Log error with request context
  logger.error('Request failed', {
    error: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
    userId: req.user?.id,
    requestId: req.id
  });
  
  // Validation errors
  if (err instanceof ValidationError) {
    return res.status(422).json({
      error: {
        code: err.code,
        message: err.message,
        field: err.field
      }
    });
  }
  
  // Business rule errors
  if (err instanceof BusinessRuleError) {
    return res.status(400).json({
      error: {
        code: err.code,
        message: err.message
      }
    });
  }
  
  // Not found errors
  if (err instanceof NotFoundError) {
    return res.status(404).json({
      error: {
        code: 'NOT_FOUND',
        message: err.message
      }
    });
  }
  
  // Authentication errors
  if (err instanceof AuthenticationError) {
    return res.status(401).json({
      error: {
        code: 'UNAUTHORIZED',
        message: 'Authentication required'
      }
    });
  }
  
  // Authorization errors
  if (err instanceof AuthorizationError) {
    return res.status(403).json({
      error: {
        code: 'FORBIDDEN',
        message: 'Insufficient permissions'
      }
    });
  }
  
  // External service errors (often retryable)
  if (err instanceof ExternalServiceError) {
    return res.status(503).json({
      error: {
        code: 'SERVICE_UNAVAILABLE',
        message: 'External service temporarily unavailable',
        retryable: true
      }
    });
  }
  
  // Generic errors (hide details in production)
  const isProduction = process.env.NODE_ENV === 'production';
  
  res.status(500).json({
    error: {
      code: 'INTERNAL_SERVER_ERROR',
      message: isProduction 
        ? 'An unexpected error occurred'
        : err.message,
      ...(isProduction ? {} : { stack: err.stack })
    }
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: {
      code: 'NOT_FOUND',
      message: 'Endpoint not found'
    }
  });
});
```

**Node.js process handlers:**
```javascript
// Uncaught exceptions (should not happen, but...)
process.on('uncaughtException', (error) => {
  logger.fatal('Uncaught exception', {
    error: error.message,
    stack: error.stack
  });
  
  // Give time to log, then exit
  setTimeout(() => {
    process.exit(1);
  }, 1000);
});

// Unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled promise rejection', {
    reason,
    promise
  });
  
  // In production, might want to exit
  if (process.env.NODE_ENV === 'production') {
    process.exit(1);
  }
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully');
  
  // Stop accepting new requests
  server.close(async () => {
    // Close database connections
    await db.close();
    
    // Close other resources
    await cache.disconnect();
    
    logger.info('Shutdown complete');
    process.exit(0);
  });
  
  // Force shutdown after 10 seconds
  setTimeout(() => {
    logger.error('Forced shutdown after timeout');
    process.exit(1);
  }, 10000);
});
```

### Async Error Handling

**Promises:**
```javascript
// Always attach .catch()
fetchData()
  .then(processData)
  .then(saveData)
  .catch(error => {
    logger.error('Data pipeline failed', { error });
    // Handle or re-throw
  });

// Or use async/await with try-catch
async function dataPipeline() {
  try {
    const data = await fetchData();
    const processed = await processData(data);
    await saveData(processed);
  } catch (error) {
    logger.error('Data pipeline failed', { error });
    throw error;
  }
}
```

**Async function wrapper:**
```javascript
// Catch async errors in Express routes
function asyncHandler(fn) {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

// Usage
app.get('/users/:id', asyncHandler(async (req, res) => {
  const user = await db.users.findById(req.params.id);
  
  if (!user) {
    throw new NotFoundError('User not found', req.params.id);
  }
  
  res.json({ user });
}));
```

**Parallel async operations:**
```javascript
async function fetchMultipleResources() {
  try {
    // All succeed or all fail
    const [users, posts, comments] = await Promise.all([
      fetchUsers(),
      fetchPosts(),
      fetchComments()
    ]);
    
    return { users, posts, comments };
    
  } catch (error) {
    // One failure fails everything
    logger.error('Failed to fetch resources', { error });
    throw error;
  }
}

// Or handle partial failures
async function fetchMultipleResourcesWithFallback() {
  const results = await Promise.allSettled([
    fetchUsers(),
    fetchPosts(),
    fetchComments()
  ]);
  
  return {
    users: results[0].status === 'fulfilled' ? results[0].value : [],
    posts: results[1].status === 'fulfilled' ? results[1].value : [],
    comments: results[2].status === 'fulfilled' ? results[2].value : []
  };
}
```

## Logging Best Practices

### Log Levels

```javascript
const logger = {
  // Fatal: Application cannot continue
  fatal: (message, context) => {
    console.error('[FATAL]', message, context);
    // Alert on-call engineer immediately
    alertEngineer({ level: 'fatal', message, context });
  },
  
  // Error: Unexpected errors, but app continues
  error: (message, context) => {
    console.error('[ERROR]', message, context);
    // Log to error tracking service
    logToErrorService({ level: 'error', message, context });
  },
  
  // Warn: Potential issues, degraded functionality
  warn: (message, context) => {
    console.warn('[WARN]', message, context);
  },
  
  // Info: Important business events
  info: (message, context) => {
    console.info('[INFO]', message, context);
  },
  
  // Debug: Detailed information for debugging
  debug: (message, context) => {
    if (process.env.LOG_LEVEL === 'debug') {
      console.debug('[DEBUG]', message, context);
    }
  },
  
  // Trace: Very detailed, usually disabled
  trace: (message, context) => {
    if (process.env.LOG_LEVEL === 'trace') {
      console.trace('[TRACE]', message, context);
    }
  }
};
```

### Structured Logging

```javascript
// Good: Structured logs (easily searchable)
logger.error('Order processing failed', {
  orderId: '12345',
  userId: '67890',
  error: error.message,
  errorCode: error.code,
  amount: 99.99,
  timestamp: new Date().toISOString(),
  requestId: req.id
});

// Bad: Unstructured logs (hard to search)
logger.error(`Order 12345 for user 67890 failed: ${error.message}`);
```

### Sensitive Data Protection

```javascript
function sanitizeForLogging(obj) {
  const sanitized = { ...obj };
  
  // Remove sensitive fields
  const sensitiveFields = [
    'password',
    'creditCard',
    'ssn',
    'token',
    'secret',
    'apiKey'
  ];
  
  for (const field of sensitiveFields) {
    if (field in sanitized) {
      sanitized[field] = '[REDACTED]';
    }
  }
  
  // Mask email (show first char and domain)
  if (sanitized.email) {
    const [local, domain] = sanitized.email.split('@');
    sanitized.email = `${local[0]}***@${domain}`;
  }
  
  return sanitized;
}

// Usage
logger.info('User created', sanitizeForLogging({
  email: 'user@example.com',
  password: 'secret123',
  name: 'John Doe'
}));
// Logs: { email: 'u***@example.com', password: '[REDACTED]', name: 'John Doe' }
```

### Request Tracing

```javascript
// Middleware to add request ID
app.use((req, res, next) => {
  req.id = req.headers['x-request-id'] || generateRequestId();
  res.setHeader('X-Request-ID', req.id);
  next();
});

// Log with request ID
logger.info('Processing request', {
  requestId: req.id,
  method: req.method,
  path: req.path,
  userId: req.user?.id
});

// Include in all subsequent logs
logger.error('Database query failed', {
  requestId: req.id,
  query: 'SELECT * FROM users',
  error: error.message
});
```

## User-Facing Errors

### Error Message Guidelines

**Good error messages:**
```javascript
// ✅ Clear, actionable, friendly
{
  "error": {
    "message": "Your credit card was declined. Please use a different payment method or contact your bank.",
    "code": "PAYMENT_DECLINED",
    "action": "Try a different card or contact your bank"
  }
}

// ✅ Validation error with field
{
  "error": {
    "message": "Invalid email format",
    "code": "VALIDATION_ERROR",
    "field": "email",
    "value": "not-an-email",
    "help": "Email must include an @ symbol"
  }
}
```

**Bad error messages:**
```javascript
// ❌ Technical, not actionable
{
  "error": "SQLException: duplicate key value violates unique constraint"
}

// ❌ Too vague
{
  "error": "Something went wrong"
}

// ❌ Exposes internal details
{
  "error": "Failed to connect to database server at 10.0.1.53:5432"
}
```

### Error Response Structure

```javascript
class ErrorResponse {
  constructor(code, message, details = {}) {
    this.error = {
      code,
      message,
      timestamp: new Date().toISOString(),
      ...details
    };
  }
  
  // User-friendly messages
  static notFound(resource, id) {
    return new ErrorResponse(
      'NOT_FOUND',
      `${resource} not found`,
      { resource, id }
    );
  }
  
  static validation(field, message) {
    return new ErrorResponse(
      'VALIDATION_ERROR',
      message,
      { field }
    );
  }
  
  static unauthorized(message = 'Authentication required') {
    return new ErrorResponse('UNAUTHORIZED', message);
  }
  
  static forbidden(message = 'Insufficient permissions') {
    return new ErrorResponse('FORBIDDEN', message);
  }
  
  static serviceUnavailable(service) {
    return new ErrorResponse(
      'SERVICE_UNAVAILABLE',
      `${service} is temporarily unavailable. Please try again later.`,
      { service, retryable: true }
    );
  }
  
  static rateLimit(retryAfter) {
    return new ErrorResponse(
      'RATE_LIMIT_EXCEEDED',
      'Too many requests. Please slow down.',
      { retryAfter }
    );
  }
}

// Usage
res.status(404).json(ErrorResponse.notFound('User', userId));
```

### Internationalized Errors

```javascript
class I18nErrorResponse {
  constructor(code, key, params = {}) {
    this.code = code;
    this.key = key;
    this.params = params;
  }
  
  toJSON(locale = 'en') {
    return {
      error: {
        code: this.code,
        message: i18n.t(this.key, { locale, ...this.params }),
        params: this.params
      }
    };
  }
}

// translations/en.json
{
  "errors": {
    "user_not_found": "User not found",
    "insufficient_funds": "Insufficient funds. Available: ${available}, Required: ${required}"
  }
}

// Usage
const error = new I18nErrorResponse(
  'INSUFFICIENT_FUNDS',
  'errors.insufficient_funds',
  { available: 50, required: 100 }
);

res.status(400).json(error.toJSON(req.locale));
```

## Retry Strategies

### Exponential Backoff

```javascript
async function retryWithExponentialBackoff(
  fn,
  options = {}
) {
  const {
    maxRetries = 3,
    baseDelay = 1000,
    maxDelay = 30000,
    factor = 2,
    jitter = true
  } = options;
  
  let lastError;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      // Don't retry on certain errors
      if (error instanceof ValidationError || error instanceof AuthorizationError) {
        throw error;
      }
      
      if (attempt < maxRetries) {
        // Calculate delay: base * (factor ^ attempt)
        let delay = Math.min(baseDelay * Math.pow(factor, attempt), maxDelay);
        
        // Add jitter to prevent thundering herd
        if (jitter) {
          delay = delay * (0.5 + Math.random() * 0.5);
        }
        
        logger.warn(`Retry attempt ${attempt + 1}/${maxRetries} after ${delay}ms`, {
          error: error.message
        });
        
        await sleep(delay);
      }
    }
  }
  
  throw new Error(`Failed after ${maxRetries} retries: ${lastError.message}`);
}

// Usage
const data = await retryWithExponentialBackoff(
  () => fetchFromAPI(url),
  { maxRetries: 5, baseDelay: 1000 }
);
```

### Retry with Circuit Breaker

```javascript
class RetryableOperation {
  constructor(operation, circuitBreaker, retryOptions) {
    this.operation = operation;
    this.circuitBreaker = circuitBreaker;
    this.retryOptions = retryOptions;
  }
  
  async execute(...args) {
    // Check circuit breaker first
    if (this.circuitBreaker.isOpen()) {
      throw new Error('Circuit breaker is open');
    }
    
    try {
      const result = await retryWithExponentialBackoff(
        () => this.operation(...args),
        this.retryOptions
      );
      
      this.circuitBreaker.recordSuccess();
      return result;
      
    } catch (error) {
      this.circuitBreaker.recordFailure();
      throw error;
    }
  }
}
```

## Graceful Degradation

### Fallback Mechanisms

```javascript
async function getUserRecommendations(userId) {
  try {
    // Try primary recommendation service
    return await recommendationService.getForUser(userId);
    
  } catch (error) {
    logger.warn('Recommendation service failed, using fallback', {
      userId,
      error: error.message
    });
    
    try {
      // Fallback to cached recommendations
      const cached = await cache.get(`recommendations:${userId}`);
      if (cached) {
        return JSON.parse(cached);
      }
    } catch (cacheError) {
      logger.error('Cache fallback also failed', { cacheError });
    }
    
    // Ultimate fallback: popular items
    return await getPopularItems();
  }
}
```

### Feature Flags for Degradation

```javascript
async function processOrder(orderData) {
  let loyaltyPoints = 0;
  
  // Try to award loyalty points, but don't fail order if it fails
  if (featureFlags.isEnabled('loyalty_points')) {
    try {
      loyaltyPoints = await loyaltyService.awardPoints(orderData);
    } catch (error) {
      logger.warn('Loyalty points failed, continuing without them', {
        orderId: orderData.id,
        error: error.message
      });
      // Optionally disable feature flag if failures persist
      if (await shouldDisableFeature('loyalty_points', error)) {
        featureFlags.disable('loyalty_points');
      }
    }
  }
  
  // Continue with order processing
  return {
    order: await createOrder(orderData),
    loyaltyPoints
  };
}
```

## Error Recovery

### Compensating Actions

```javascript
async function createOrderWithCompensation(orderData) {
  let orderId;
  let paymentId;
  let inventoryReserved = false;
  
  try {
    // Step 1: Create order
    orderId = await db.orders.create(orderData);
    
    // Step 2: Process payment
    paymentId = await paymentService.charge(orderData.payment);
    
    // Step 3: Reserve inventory
    await inventoryService.reserve(orderId, orderData.items);
    inventoryReserved = true;
    
    return { orderId, paymentId };
    
  } catch (error) {
    logger.error('Order creation failed, compensating', {
      orderId,
      paymentId,
      error: error.message
    });
    
    // Compensate in reverse order
    if (inventoryReserved) {
      await inventoryService.release(orderId).catch(err => 
        logger.error('Inventory release failed', { err })
      );
    }
    
    if (paymentId) {
      await paymentService.refund(paymentId).catch(err =>
        logger.error('Payment refund failed', { err })
      );
    }
    
    if (orderId) {
      await db.orders.delete(orderId).catch(err =>
        logger.error('Order deletion failed', { err })
      );
    }
    
    throw error;
  }
}
```

### Dead Letter Queue

```javascript
class DeadLetterQueue {
  constructor(storage) {
    this.storage = storage;
  }
  
  async add(item, error, context) {
    await this.storage.push({
      item,
      error: {
        message: error.message,
        stack: error.stack,
        code: error.code
      },
      context,
      timestamp: new Date(),
      retryCount: (item.retryCount || 0) + 1
    });
    
    logger.error('Item moved to dead letter queue', {
      itemId: item.id,
      error: error.message,
      retryCount: item.retryCount
    });
  }
  
  async reprocess(itemId) {
    const item = await this.storage.get(itemId);
    
    try {
      await processItem(item.item);
      await this.storage.delete(itemId);
      logger.info('DLQ item successfully reprocessed', { itemId });
      
    } catch (error) {
      logger.error('DLQ reprocessing failed', { itemId, error });
      throw error;
    }
  }
  
  async list(options = {}) {
    return await this.storage.list(options);
  }
}
```

## Error Monitoring

### Error Tracking Setup

```javascript
// Using Sentry or similar
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,
  
  beforeSend(event, hint) {
    // Filter out certain errors
    if (event.exception) {
      const error = hint.originalException;
      
      // Don't send validation errors
      if (error instanceof ValidationError) {
        return null;
      }
      
      // Don't send 404s
      if (error instanceof NotFoundError) {
        return null;
      }
    }
    
    // Add custom context
    event.tags = {
      ...event.tags,
      version: process.env.APP_VERSION
    };
    
    return event;
  }
});

// Capture exception with context
function logErrorToTracking(error, context) {
  Sentry.withScope(scope => {
    // Add context
    scope.setContext('custom', context);
    
    // Add user info
    if (context.userId) {
      scope.setUser({ id: context.userId });
    }
    
    // Add tags for filtering
    scope.setTags({
      errorCode: error.code,
      errorType: error.name
    });
    
    // Capture
    Sentry.captureException(error);
  });
}
```

### Health Checks

```javascript
app.get('/health', async (req, res) => {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    checks: {}
  };
  
  // Check database
  try {
    await db.query('SELECT 1');
    health.checks.database = { status: 'up' };
  } catch (error) {
    health.checks.database = { 
      status: 'down',
      error: error.message
    };
    health.status = 'unhealthy';
  }
  
  // Check cache
  try {
    await cache.ping();
    health.checks.cache = { status: 'up' };
  } catch (error) {
    health.checks.cache = {
      status: 'down',
      error: error.message
    };
    health.status = 'degraded';
  }
  
  // Check external services
  try {
    await paymentService.healthCheck();
    health.checks.payment = { status: 'up' };
  } catch (error) {
    health.checks.payment = {
      status: 'down',
      error: error.message
    };
    health.status = 'degraded';
  }
  
  const statusCode = health.status === 'healthy' ? 200 : 503;
  res.status(statusCode).json(health);
});
```

## Error Handling Checklist

### Design Phase
- [ ] Identified possible error scenarios?
- [ ] Designed user-friendly error messages?
- [ ] Planned fallback mechanisms?
- [ ] Decided on retry strategies?
- [ ] Considered graceful degradation?

### Implementation Phase
- [ ] Used custom error classes?
- [ ] Added try-catch where appropriate?
- [ ] Implemented global error handlers?
- [ ] Added request ID tracing?
- [ ] Protected sensitive data in logs?

### Operations Phase
- [ ] Set up error monitoring (Sentry, etc.)?
- [ ] Configured alerting for critical errors?
- [ ] Implemented health checks?
- [ ] Created runbooks for common errors?
- [ ] Set up dead letter queues?

## Common Pitfalls

### 1. Swallowing Errors
**Problem:** Catching errors without logging or handling  
**Solution:** Always log, handle, or re-throw

### 2. Generic Error Messages
**Problem:** "Something went wrong"  
**Solution:** Specific, actionable messages

### 3. Exposing Internal Details
**Problem:** Showing stack traces to users  
**Solution:** User-friendly messages, log details

### 4. Not Using Error Codes
**Problem:** Can't programmatically handle errors  
**Solution:** Consistent error codes

### 5. Synchronous Error Handling for Async Code
**Problem:** Missing errors in promises  
**Solution:** Always use .catch() or try-catch with async/await

## Integration with Other Skills

**Combines well with:**
- **integration-patterns** - Error handling in distributed systems
- **api-design** - Error response design
- **debugging-methodology** - Debug production errors
- **critical-thinking** - Evaluate error handling strategies

**When both active:**
Use critical thinking to design error handling strategy, then apply specific patterns from this skill.