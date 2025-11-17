---
name: performance-optimization
description: Comprehensive performance optimization guide covering frontend, backend, database, and infrastructure. Use when improving application speed, reducing latency, optimizing queries, implementing caching, profiling bottlenecks, or scaling systems. Covers metrics, profiling tools, optimization techniques, and monitoring strategies.
---

# Performance Optimization

Comprehensive framework for identifying and resolving performance bottlenecks across all layers of modern applications.

## When to Use

Apply this skill when:
- Application feels slow or unresponsive
- Page load times are too long
- API response times are high
- Database queries are slow
- Memory usage is growing
- CPU usage is high
- Server costs are too high
- Users complaining about performance
- Preparing for traffic spikes
- Scaling existing systems

## Core Principles

### 1. Measure First, Optimize Second
- Never guess at bottlenecks
- Use profiling tools to identify issues
- Establish baseline metrics
- Measure impact of changes

### 2. Optimize the Right Thing
- Focus on the biggest bottleneck first
- 80/20 rule: 20% of code causes 80% of problems
- User-perceived performance > raw metrics
- Optimize for the common case

### 3. Consider Trade-offs
- Complexity vs performance
- Memory vs CPU
- Development time vs optimization gains
- Maintainability vs speed

### 4. Performance is a Feature
- Budget for performance work
- Monitor continuously
- Prevent regressions
- Set performance SLAs

## Performance Metrics

### Frontend Metrics

**Core Web Vitals (Google):**
```javascript
// Largest Contentful Paint (LCP)
// Target: < 2.5s
// Measures: Loading performance

// First Input Delay (FID)
// Target: < 100ms
// Measures: Interactivity

// Cumulative Layout Shift (CLS)
// Target: < 0.1
// Measures: Visual stability

// Measure with Web Vitals library
import { onLCP, onFID, onCLS } from 'web-vitals';

onLCP(console.log);
onFID(console.log);
onCLS(console.log);
```

**Other Important Metrics:**
```javascript
// Time to First Byte (TTFB)
// Target: < 200ms

// First Contentful Paint (FCP)
// Target: < 1.8s

// Time to Interactive (TTI)
// Target: < 3.8s

// Total Blocking Time (TBT)
// Target: < 200ms

// Speed Index
// Target: < 3.4s
```

**Measuring with Performance API:**
```javascript
// Navigation timing
const perfData = performance.getEntriesByType('navigation')[0];
console.log('DNS lookup:', perfData.domainLookupEnd - perfData.domainLookupStart);
console.log('TCP handshake:', perfData.connectEnd - perfData.connectStart);
console.log('Response time:', perfData.responseEnd - perfData.requestStart);
console.log('DOM processing:', perfData.domComplete - perfData.domLoading);
console.log('Total load time:', perfData.loadEventEnd - perfData.fetchStart);

// Resource timing
performance.getEntriesByType('resource').forEach(resource => {
  console.log(`${resource.name}: ${resource.duration}ms`);
});

// Custom marks and measures
performance.mark('data-fetch-start');
await fetchData();
performance.mark('data-fetch-end');
performance.measure('data-fetch', 'data-fetch-start', 'data-fetch-end');

const measure = performance.getEntriesByName('data-fetch')[0];
console.log(`Data fetch took: ${measure.duration}ms`);
```

### Backend Metrics

**Response Time:**
```javascript
// Express middleware to measure
app.use((req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`${req.method} ${req.path}: ${duration}ms`);
    
    // Send to monitoring
    metrics.histogram('http.request.duration', duration, {
      method: req.method,
      route: req.route?.path,
      status: res.statusCode
    });
  });
  
  next();
});
```

**Key Backend Metrics:**
- Request latency (p50, p95, p99)
- Throughput (requests per second)
- Error rate
- CPU usage
- Memory usage
- Database query time
- External API latency

### Database Metrics

```sql
-- PostgreSQL: Slow query log
-- postgresql.conf: log_min_duration_statement = 100

-- Find slow queries
SELECT 
  query,
  calls,
  total_time,
  mean_time,
  max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;

-- Index usage
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE 'pg_toast%';

-- Table sizes
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;
```

## Frontend Optimization

### 1. JavaScript Optimization

**Code Splitting:**
```javascript
// Bad: Load everything upfront
import { HeavyComponent } from './HeavyComponent';

// Good: Lazy load
const HeavyComponent = React.lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <HeavyComponent />
    </Suspense>
  );
}

// Route-based splitting
const routes = [
  {
    path: '/dashboard',
    component: lazy(() => import('./pages/Dashboard'))
  },
  {
    path: '/profile',
    component: lazy(() => import('./pages/Profile'))
  }
];
```

**Tree Shaking:**
```javascript
// Bad: Imports entire library
import _ from 'lodash';
const result = _.debounce(fn, 300);

// Good: Import only what you need
import debounce from 'lodash/debounce';
const result = debounce(fn, 300);

// Even better: Use native or smaller alternatives
const debounce = (fn, ms) => {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), ms);
  };
};
```

**Debouncing & Throttling:**
```javascript
// Debounce: Wait for user to stop typing
const searchInput = document.querySelector('#search');
const debouncedSearch = debounce((query) => {
  performSearch(query);
}, 300);

searchInput.addEventListener('input', (e) => {
  debouncedSearch(e.target.value);
});

// Throttle: Limit execution rate (scroll, resize)
const throttle = (fn, ms) => {
  let lastRun = 0;
  return (...args) => {
    const now = Date.now();
    if (now - lastRun >= ms) {
      fn(...args);
      lastRun = now;
    }
  };
};

window.addEventListener('scroll', throttle(() => {
  updateScrollPosition();
}, 100));
```

**Web Workers for Heavy Computation:**
```javascript
// worker.js
self.addEventListener('message', (e) => {
  const result = expensiveCalculation(e.data);
  self.postMessage(result);
});

function expensiveCalculation(data) {
  // Heavy computation here
  return result;
}

// main.js
const worker = new Worker('worker.js');

worker.postMessage(largeDataset);

worker.addEventListener('message', (e) => {
  console.log('Result:', e.data);
  updateUI(e.data);
});
```

**Memoization:**
```javascript
// React.memo for components
const ExpensiveComponent = React.memo(({ data }) => {
  return <div>{expensiveRender(data)}</div>;
}, (prevProps, nextProps) => {
  // Only re-render if data changed
  return prevProps.data === nextProps.data;
});

// useMemo for expensive calculations
function Component({ items }) {
  const sortedItems = useMemo(() => {
    return items.sort((a, b) => b.value - a.value);
  }, [items]);
  
  return <List items={sortedItems} />;
}

// useCallback for function references
function Parent() {
  const [count, setCount] = useState(0);
  
  const handleClick = useCallback(() => {
    console.log('Clicked');
  }, []); // Function reference stays same
  
  return <Child onClick={handleClick} />;
}
```

### 2. Asset Optimization

**Image Optimization:**
```html
<!-- Use modern formats -->
<picture>
  <source srcset="image.webp" type="image/webp">
  <source srcset="image.avif" type="image/avif">
  <img src="image.jpg" alt="Description">
</picture>

<!-- Responsive images -->
<img 
  srcset="small.jpg 480w, medium.jpg 800w, large.jpg 1200w"
  sizes="(max-width: 600px) 480px, (max-width: 900px) 800px, 1200px"
  src="medium.jpg"
  alt="Description"
>

<!-- Lazy loading -->
<img src="image.jpg" loading="lazy" alt="Description">
```

```javascript
// Image compression on upload
import sharp from 'sharp';

async function processImage(buffer) {
  // Resize and compress
  const compressed = await sharp(buffer)
    .resize(1200, 1200, { fit: 'inside', withoutEnlargement: true })
    .webp({ quality: 80 })
    .toBuffer();
  
  return compressed;
}
```

**Font Optimization:**
```html
<!-- Preload critical fonts -->
<link rel="preload" href="/fonts/main.woff2" as="font" type="font/woff2" crossorigin>

<!-- Use font-display: swap -->
<style>
  @font-face {
    font-family: 'CustomFont';
    src: url('/fonts/custom.woff2') format('woff2');
    font-display: swap; /* Show fallback immediately */
  }
</style>

<!-- Subset fonts (include only needed characters) -->
<!-- Use tools like glyphhanger -->
```

**Bundle Optimization:**
```javascript
// Webpack configuration
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10
        },
        common: {
          minChunks: 2,
          priority: 5,
          reuseExistingChunk: true
        }
      }
    },
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: true // Remove console.log in production
          }
        }
      })
    ]
  }
};
```

### 3. Rendering Optimization

**Virtual Scrolling:**
```javascript
// React Virtual for large lists
import { FixedSizeList } from 'react-window';

function LargeList({ items }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {({ index, style }) => (
        <div style={style}>
          {items[index].name}
        </div>
      )}
    </FixedSizeList>
  );
}
```

**Intersection Observer for Lazy Loading:**
```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      observer.unobserve(img);
    }
  });
}, {
  rootMargin: '50px' // Load slightly before visible
});

document.querySelectorAll('img[data-src]').forEach(img => {
  observer.observe(img);
});
```

**Request Idle Callback:**
```javascript
// Defer non-critical work
function deferredWork() {
  requestIdleCallback((deadline) => {
    while (deadline.timeRemaining() > 0 && tasks.length > 0) {
      const task = tasks.shift();
      processTask(task);
    }
    
    if (tasks.length > 0) {
      deferredWork(); // Continue in next idle period
    }
  });
}
```

### 4. Network Optimization

**Resource Hints:**
```html
<!-- DNS prefetch for third-party origins -->
<link rel="dns-prefetch" href="https://cdn.example.com">

<!-- Preconnect for critical origins -->
<link rel="preconnect" href="https://api.example.com">

<!-- Prefetch for next page -->
<link rel="prefetch" href="/next-page.html">

<!-- Preload critical resources -->
<link rel="preload" href="/critical.js" as="script">
<link rel="preload" href="/critical.css" as="style">
```

**HTTP/2 Server Push:**
```javascript
// Express with HTTP/2
import http2 from 'http2';

app.get('/', (req, res) => {
  // Push critical resources
  res.push('/styles/critical.css', {
    response: { 'content-type': 'text/css' }
  });
  
  res.push('/scripts/main.js', {
    response: { 'content-type': 'application/javascript' }
  });
  
  res.sendFile('index.html');
});
```

**Service Worker Caching:**
```javascript
// service-worker.js
const CACHE_NAME = 'v1';
const urlsToCache = [
  '/',
  '/styles/main.css',
  '/scripts/main.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }
        
        // Clone request
        const fetchRequest = event.request.clone();
        
        return fetch(fetchRequest).then(response => {
          // Check if valid response
          if (!response || response.status !== 200) {
            return response;
          }
          
          // Clone response
          const responseToCache = response.clone();
          
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });
          
          return response;
        });
      })
  );
});
```

## Backend Optimization

### 1. Database Query Optimization

**N+1 Query Problem:**
```javascript
// Bad: N+1 queries
const users = await User.findAll();
for (const user of users) {
  user.posts = await Post.findAll({ where: { userId: user.id } });
}

// Good: Single query with join
const users = await User.findAll({
  include: [{ model: Post }]
});

// Or: Two queries with IN clause
const users = await User.findAll();
const userIds = users.map(u => u.id);
const posts = await Post.findAll({ where: { userId: userIds } });

// Map posts to users
const postsByUser = posts.reduce((acc, post) => {
  if (!acc[post.userId]) acc[post.userId] = [];
  acc[post.userId].push(post);
  return acc;
}, {});

users.forEach(user => {
  user.posts = postsByUser[user.id] || [];
});
```

**Indexing:**
```sql
-- Find missing indexes
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 123;
-- Look for "Seq Scan" (bad) vs "Index Scan" (good)

-- Add index
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- Composite index for multi-column queries
CREATE INDEX idx_orders_customer_status ON orders(customer_id, status);

-- Partial index
CREATE INDEX idx_orders_pending ON orders(created_at) 
WHERE status = 'pending';

-- Index on JSON field (PostgreSQL)
CREATE INDEX idx_data_email ON users USING gin ((data->>'email'));
```

**Query Optimization:**
```sql
-- Bad: Select all columns
SELECT * FROM users WHERE email = 'user@example.com';

-- Good: Select only needed columns
SELECT id, name, email FROM users WHERE email = 'user@example.com';

-- Bad: OFFSET pagination (slow for large offsets)
SELECT * FROM posts ORDER BY created_at DESC LIMIT 10 OFFSET 10000;

-- Good: Cursor-based pagination
SELECT * FROM posts 
WHERE created_at < '2025-01-01'
ORDER BY created_at DESC 
LIMIT 10;

-- Use EXISTS instead of COUNT when checking existence
-- Bad
SELECT COUNT(*) FROM orders WHERE user_id = 123;
-- Good
SELECT EXISTS(SELECT 1 FROM orders WHERE user_id = 123);

-- Use UNION ALL instead of UNION if duplicates are ok
SELECT name FROM users WHERE active = true
UNION ALL
SELECT name FROM archived_users WHERE active = true;
```

**Connection Pooling:**
```javascript
// PostgreSQL with pg pool
import { Pool } from 'pg';

const pool = new Pool({
  host: 'localhost',
  database: 'mydb',
  max: 20, // Maximum connections
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000
});

// Use pool for queries
async function getUser(id) {
  const client = await pool.connect();
  try {
    const result = await client.query('SELECT * FROM users WHERE id = $1', [id]);
    return result.rows[0];
  } finally {
    client.release(); // Return to pool
  }
}
```

### 2. Caching Strategies

**Memory Cache (Redis):**
```javascript
import Redis from 'ioredis';

const redis = new Redis();

// Cache aside pattern
async function getUser(id) {
  const cacheKey = `user:${id}`;
  
  // Check cache
  const cached = await redis.get(cacheKey);
  if (cached) {
    return JSON.parse(cached);
  }
  
  // Fetch from database
  const user = await db.users.findById(id);
  
  // Store in cache
  await redis.setex(cacheKey, 3600, JSON.stringify(user)); // 1 hour TTL
  
  return user;
}

// Cache invalidation
async function updateUser(id, data) {
  await db.users.update(id, data);
  
  // Invalidate cache
  await redis.del(`user:${id}`);
}
```

**HTTP Caching:**
```javascript
// Express caching headers
app.get('/api/products/:id', async (req, res) => {
  const product = await getProduct(req.params.id);
  
  // Cache for 5 minutes
  res.set('Cache-Control', 'public, max-age=300');
  res.set('ETag', generateETag(product));
  
  // Check if client has fresh copy
  if (req.headers['if-none-match'] === res.get('ETag')) {
    return res.status(304).end();
  }
  
  res.json(product);
});

// CDN caching for static assets
app.use('/static', express.static('public', {
  maxAge: '1y', // Cache for 1 year
  immutable: true
}));
```

**Memoization in Backend:**
```javascript
// Simple memoization
function memoize(fn) {
  const cache = new Map();
  
  return (...args) => {
    const key = JSON.stringify(args);
    
    if (cache.has(key)) {
      return cache.get(key);
    }
    
    const result = fn(...args);
    cache.set(key, result);
    
    return result;
  };
}

// Usage
const expensiveCalculation = memoize((n) => {
  // Heavy computation
  return result;
});

// With TTL
function memoizeWithTTL(fn, ttl = 60000) {
  const cache = new Map();
  
  return (...args) => {
    const key = JSON.stringify(args);
    const cached = cache.get(key);
    
    if (cached && Date.now() - cached.timestamp < ttl) {
      return cached.value;
    }
    
    const result = fn(...args);
    cache.set(key, { value: result, timestamp: Date.now() });
    
    return result;
  };
}
```

**Cache Warming:**
```javascript
// Proactively populate cache
async function warmCache() {
  console.log('Warming cache...');
  
  // Popular products
  const popularIds = await getPopularProductIds();
  for (const id of popularIds) {
    await getProduct(id); // Populates cache
  }
  
  // Frequently accessed data
  await getCategories(); // Populates cache
  
  console.log('Cache warmed');
}

// Run on startup
warmCache();

// Run periodically
setInterval(warmCache, 3600000); // Every hour
```

### 3. Response Optimization

**Compression:**
```javascript
import compression from 'compression';

app.use(compression({
  level: 6, // Compression level (0-9)
  threshold: 1024, // Only compress responses > 1KB
  filter: (req, res) => {
    if (req.headers['x-no-compression']) {
      return false;
    }
    return compression.filter(req, res);
  }
}));
```

**Response Streaming:**
```javascript
// Stream large responses
app.get('/api/export', async (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.write('[');
  
  const stream = db.users.stream();
  let first = true;
  
  for await (const user of stream) {
    if (!first) res.write(',');
    res.write(JSON.stringify(user));
    first = false;
  }
  
  res.write(']');
  res.end();
});
```

**Partial Responses:**
```javascript
// Support field selection
app.get('/api/users/:id', async (req, res) => {
  const fields = req.query.fields?.split(',') || null;
  const user = await getUser(req.params.id);
  
  if (fields) {
    const partial = {};
    fields.forEach(field => {
      if (field in user) {
        partial[field] = user[field];
      }
    });
    return res.json(partial);
  }
  
  res.json(user);
});

// GET /api/users/123?fields=id,name,email
```

### 4. Async Processing

**Don't Block the Request:**
```javascript
// Bad: Synchronous operation blocks request
app.post('/api/orders', async (req, res) => {
  const order = await createOrder(req.body);
  await sendConfirmationEmail(order); // Blocks response!
  await updateInventory(order);       // Blocks response!
  await notifyWarehouse(order);       // Blocks response!
  
  res.json({ order });
});

// Good: Offload to background jobs
app.post('/api/orders', async (req, res) => {
  const order = await createOrder(req.body);
  
  // Queue background jobs
  await queue.add('send-email', { orderId: order.id });
  await queue.add('update-inventory', { orderId: order.id });
  await queue.add('notify-warehouse', { orderId: order.id });
  
  // Return immediately
  res.json({ order });
});
```

## Infrastructure Optimization

### 1. Load Balancing

```nginx
# Nginx load balancer
upstream backend {
    least_conn; # Route to least busy server
    
    server backend1.example.com:3000 weight=3;
    server backend2.example.com:3000 weight=2;
    server backend3.example.com:3000 weight=1;
    
    # Health checks
    server backend4.example.com:3000 backup;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Connection pooling
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        
        # Timeouts
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 2. CDN Configuration

```javascript
// CloudFront example
const distribution = {
  Origins: [{
    DomainName: 'origin.example.com',
    CustomOriginConfig: {
      HTTPPort: 80,
      HTTPSPort: 443,
      OriginProtocolPolicy: 'https-only'
    }
  }],
  DefaultCacheBehavior: {
    TargetOriginId: 'origin',
    ViewerProtocolPolicy: 'redirect-to-https',
    Compress: true,
    CachePolicyId: 'CachingOptimized',
    MinTTL: 0,
    DefaultTTL: 86400, // 1 day
    MaxTTL: 31536000   // 1 year
  },
  CacheBehaviors: [
    // Different caching for API
    {
      PathPattern: '/api/*',
      TargetOriginId: 'origin',
      MinTTL: 0,
      DefaultTTL: 0,
      MaxTTL: 0
    },
    // Long cache for static assets
    {
      PathPattern: '/static/*',
      TargetOriginId: 'origin',
      MinTTL: 31536000,
      DefaultTTL: 31536000,
      MaxTTL: 31536000
    }
  ]
};
```

### 3. Database Replication

```javascript
// Read replicas for scaling reads
const { Pool } = require('pg');

const writePool = new Pool({
  host: 'primary.db.example.com',
  database: 'mydb',
  max: 20
});

const readPool = new Pool({
  host: 'replica.db.example.com',
  database: 'mydb',
  max: 50 // More read connections
});

// Write to primary
async function createUser(data) {
  return await writePool.query(
    'INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *',
    [data.name, data.email]
  );
}

// Read from replica
async function getUser(id) {
  return await readPool.query(
    'SELECT * FROM users WHERE id = $1',
    [id]
  );
}
```

## Profiling & Debugging

### Frontend Profiling

**Chrome DevTools:**
```javascript
// Performance tab
// 1. Open DevTools > Performance
// 2. Click Record
// 3. Perform actions
// 4. Stop recording
// 5. Analyze flame graph

// Lighthouse audit
// DevTools > Lighthouse > Generate report

// Coverage tool
// DevTools > Coverage > Record
// Shows unused CSS/JS

// Memory profiler
// DevTools > Memory > Take heap snapshot
// Compare snapshots to find leaks
```

**React Profiler:**
```javascript
import { Profiler } from 'react';

function onRenderCallback(
  id, // "id" prop of Profiler tree
  phase, // "mount" or "update"
  actualDuration, // Time spent rendering
  baseDuration, // Estimated time without memoization
  startTime,
  commitTime
) {
  console.log(`${id} took ${actualDuration}ms to render`);
}

<Profiler id="MyComponent" onRender={onRenderCallback}>
  <MyComponent />
</Profiler>
```

### Backend Profiling

**Node.js Profiling:**
```bash
# CPU profiling
node --prof app.js
# Generates isolate-*.log
node --prof-process isolate-*.log > processed.txt

# Clinic.js (better)
npm install -g clinic
clinic doctor -- node app.js
# Open HTML report

# Memory profiling
node --inspect app.js
# Open chrome://inspect
# Take heap snapshots
```

**Application Performance Monitoring:**
```javascript
// New Relic, Datadog, or similar
import newrelic from 'newrelic';

// Custom instrumentation
app.get('/api/heavy-operation', async (req, res) => {
  const transaction = newrelic.getTransaction();
  
  const segment = newrelic.startSegment('database-query', true);
  const data = await db.query('SELECT * FROM large_table');
  segment.end();
  
  res.json(data);
});
```

## Performance Budget

**Set and Monitor Budgets:**
```json
{
  "budgets": [
    {
      "path": "/*",
      "timings": [
        {
          "metric": "first-contentful-paint",
          "budget": 2000
        },
        {
          "metric": "interactive",
          "budget": 5000
        }
      ],
      "resourceSizes": [
        {
          "resourceType": "script",
          "budget": 300
        },
        {
          "resourceType": "total",
          "budget": 500
        }
      ]
    }
  ]
}
```

**CI/CD Performance Checks:**
```yaml
# .github/workflows/performance.yml
name: Performance Check

on: [pull_request]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build
        run: npm run build
      
      - name: Run Lighthouse
        uses: treosh/lighthouse-ci-action@v9
        with:
          urls: |
            http://localhost:3000
          uploadArtifacts: true
          budgetPath: ./budget.json
          temporaryPublicStorage: true
```

## Best Practices Checklist

### Frontend
- [ ] Code splitting implemented?
- [ ] Images optimized (WebP, lazy loading)?
- [ ] Fonts optimized (font-display: swap)?
- [ ] Bundle size < 300KB?
- [ ] Removed unused code (tree shaking)?
- [ ] Using service worker for caching?

### Backend
- [ ] Database queries optimized?
- [ ] Indexes added for common queries?
- [ ] Caching implemented (Redis)?
- [ ] Connection pooling configured?
- [ ] Response compression enabled?
- [ ] Async processing for slow tasks?

### Infrastructure
- [ ] CDN for static assets?
- [ ] Load balancing configured?
- [ ] Database read replicas?
- [ ] Auto-scaling enabled?
- [ ] Monitoring and alerting setup?

## Integration with Other Skills

**Combines well with:**
- **database-schema-design** - Query optimization, indexing
- **async-background-jobs** - Offload slow operations
- **css-styling-expert** - CSS performance, animations
- **integration-patterns** - Caching, async communication
- **error-handling** - Performance monitoring alerts

**When both active:**
Use critical thinking to prioritize optimizations, then apply specific techniques from this skill.