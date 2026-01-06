---
name: database-schema-design
description: Comprehensive database schema design guidance for relational (SQL) and document (NoSQL) databases. Use when designing database schemas, normalizing data models, choosing database types, optimizing queries, planning migrations, or making data modeling decisions. Covers PostgreSQL, MySQL, MongoDB, and general principles.
---

# Database Schema Design

Comprehensive framework for designing efficient, maintainable, and scalable database schemas.

## When to Use

Apply this skill when:
- Designing new database schemas
- Evaluating or refactoring existing schemas
- Choosing between SQL and NoSQL
- Normalizing or denormalizing data
- Optimizing query performance
- Planning database migrations
- Designing indexes
- Managing relationships between entities

## Core Principles

### 1. Model the Domain First
- Understand business entities and relationships
- Start with conceptual model, then translate to physical
- Don't let database constraints drive domain model

### 2. Balance Normalization and Performance
- Normalize to reduce redundancy
- Denormalize strategically for query performance
- Know when to break the rules

### 3. Plan for Change
- Schema migrations will happen
- Design for extensibility
- Version your migrations

### 4. Choose the Right Database Type
- Relational (SQL) for structured, related data
- Document (NoSQL) for flexible, hierarchical data
- Consider data access patterns

## Database Selection

### SQL (Relational)

**Best for:**
- Structured data with clear relationships
- ACID transactions required
- Complex queries with joins
- Data integrity critical

**Examples:** PostgreSQL, MySQL, SQL Server

### NoSQL (Document)

**Best for:**
- Flexible, hierarchical data
- High write throughput
- Horizontal scaling
- Schema evolution common

**Examples:** MongoDB, Firestore, DynamoDB

### Decision Matrix

| Factor | SQL | NoSQL |
|--------|-----|-------|
| Data structure | ✅ Structured | ✅ Flexible |
| Transactions | ✅ Full ACID | ⚠️ Limited |
| Joins | ✅ Powerful | ❌ Avoid |
| Scale | ⚠️ Vertical | ✅ Horizontal |
| Schema changes | ⚠️ Migrations | ✅ Flexible |

## SQL Schema Design

### Relationships

#### One-to-Many
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_posts_user_id ON posts(user_id);
```

#### Many-to-Many (Join Table)
```sql
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255)
);

CREATE TABLE tags (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE post_tags (
    post_id BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    tag_id BIGINT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)
);
```

### Normalization

#### 1NF (Atomic Values)
**Bad:**
```sql
items VARCHAR(500)  -- "Widget,Gadget" ❌
```

**Good:**
```sql
CREATE TABLE order_items (
    order_id INT,
    item_name VARCHAR(100)
);
```

#### 2NF (No Partial Dependencies)
**Bad:**
```sql
CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    product_name VARCHAR(100),  -- Depends only on product_id ❌
    PRIMARY KEY (order_id, product_id)
);
```

**Good:**
```sql
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE order_items (
    order_id INT,
    product_id INT REFERENCES products(id),
    PRIMARY KEY (order_id, product_id)
);
```

#### 3NF (No Transitive Dependencies)
**Bad:**
```sql
CREATE TABLE employees (
    id INT PRIMARY KEY,
    department_id INT,
    department_name VARCHAR(100)  -- Depends on department_id ❌
);
```

**Good:**
```sql
CREATE TABLE departments (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE employees (
    id INT PRIMARY KEY,
    department_id INT REFERENCES departments(id)
);
```

### Denormalization (Strategic)

**When to denormalize:**

#### Computed Values
```sql
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    total_amount DECIMAL(10,2),  -- Denormalized from order_items
    created_at TIMESTAMPTZ
);
```

#### Frequently Joined Data
```sql
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    author_name VARCHAR(100),  -- Denormalized from users.name
    title VARCHAR(255)
);
```

**Rules:**
- Measure before denormalizing
- Document why
- Strategy to keep in sync

### Primary Keys

**Auto-incrementing (Simple)**
```sql
id BIGSERIAL PRIMARY KEY  -- PostgreSQL
```
**Pros:** Simple, small, sequential  
**Cons:** Predictable, not globally unique

**UUID (Distributed)**
```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
```
**Pros:** Globally unique, distributed-friendly  
**Cons:** Larger, slower indexing

**Recommendation:** Default to `BIGSERIAL`, use UUID for distributed systems

### Indexes

**When to index:**
- Primary keys (automatic)
- Foreign keys (important!)
- WHERE clause columns
- JOIN columns
- ORDER BY columns

**Single column:**
```sql
CREATE INDEX idx_posts_published_at ON posts(published_at);
```

**Composite (order matters!):**
```sql
-- Good for: WHERE user_id = ? AND status = ?
-- Good for: WHERE user_id = ?
-- Bad for:  WHERE status = ?
CREATE INDEX idx_posts_user_status ON posts(user_id, status);
```

**Partial index (PostgreSQL):**
```sql
CREATE INDEX idx_posts_published 
ON posts(published_at) 
WHERE status = 'published';
```

**Trade-offs:**
- ✅ Faster reads
- ❌ Slower writes
- ❌ Storage overhead

### Data Types

**Strings:**
```sql
VARCHAR(255)      -- Variable length
TEXT              -- No length limit
```

**Numbers:**
```sql
INT               -- -2 billion to 2 billion
BIGINT            -- -9 quintillion to 9 quintillion
DECIMAL(10,2)     -- Exact (use for money!)
```

**Dates:**
```sql
DATE              -- Date only
TIMESTAMPTZ       -- Timestamp with timezone (preferred!)
```

**JSON:**
```sql
JSONB             -- Binary, indexable (PostgreSQL)

-- Query
SELECT * FROM products WHERE attributes->>'color' = 'red';

-- Index
CREATE INDEX idx_products_attrs ON products USING gin(attributes);
```

### Common Patterns

#### Soft Deletes
```sql
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255),
    deleted_at TIMESTAMPTZ,  -- NULL = not deleted
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_posts_deleted ON posts(deleted_at) 
WHERE deleted_at IS NULL;
```

#### Audit Trail
```sql
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT REFERENCES users(id),
    updated_at TIMESTAMPTZ,
    updated_by BIGINT REFERENCES users(id)
);
```

#### Hierarchical Data
```sql
CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100),
    parent_id BIGINT REFERENCES categories(id),
    path VARCHAR(500)  -- '/electronics/computers'
);
```

#### Enums
```sql
-- PostgreSQL enum
CREATE TYPE order_status AS ENUM ('pending', 'shipped', 'delivered');

-- Or check constraint
status VARCHAR(20) CHECK (status IN ('pending', 'shipped', 'delivered'))

-- Or lookup table (most flexible)
CREATE TABLE order_statuses (
    id SMALLINT PRIMARY KEY,
    name VARCHAR(20) UNIQUE
);
```

## NoSQL Schema Design (MongoDB)

### Embedded Documents
```javascript
// One-to-few
{
  _id: ObjectId("..."),
  name: "Alice",
  address: {
    street: "123 Main St",
    city: "San Francisco"
  }
}
```

**When to embed:**
- ✅ Data accessed together
- ✅ One-to-few relationship
- ✅ Child doesn't exist outside parent
- ✅ Updates are rare

### Referenced Documents
```javascript
// User
{ _id: ObjectId("user1"), name: "Alice" }

// Posts (many per user)
{ _id: ObjectId("post1"), user_id: ObjectId("user1"), title: "..." }
{ _id: ObjectId("post2"), user_id: ObjectId("user1"), title: "..." }
```

**When to reference:**
- ✅ One-to-many or many-to-many
- ✅ Data grows unbounded
- ✅ Frequently updated independently
- ✅ Need to query separately

### Patterns

#### Extended Reference
```javascript
// Denormalize frequently accessed fields
{
  _id: ObjectId("order1"),
  customer_id: ObjectId("user1"),
  customer_name: "Alice",  // Denormalized
  customer_email: "alice@example.com"  // Denormalized
}
```

#### Subset Pattern
```javascript
// Product with thousands of reviews
{
  _id: ObjectId("product1"),
  name: "Laptop",
  recent_reviews: [  // Only last 10
    { author: "Alice", rating: 5 }
  ],
  review_summary: {
    count: 1523,
    average: 4.5
  }
}
```

#### Bucketing Pattern
```javascript
// Time-series data
{
  _id: ObjectId("..."),
  sensor_id: "sensor_123",
  date: "2025-10-22",
  readings: [
    { time: "00:00", temp: 72.5 },
    { time: "00:15", temp: 72.3 }
  ]
}
```

### MongoDB Indexing
```javascript
// Single field
db.users.createIndex({ email: 1 })

// Compound
db.posts.createIndex({ user_id: 1, created_at: -1 })

// Text search
db.posts.createIndex({ content: "text" })

// Unique
db.users.createIndex({ email: 1 }, { unique: true })
```

## Schema Migrations

### Best Practices

**Migrations should be:**
- ✅ Reversible (up/down)
- ✅ Idempotent
- ✅ Small and focused
- ✅ Tested in staging

**Example:**
```sql
-- Up
ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active';
CREATE INDEX idx_users_status ON users(status);

-- Down
DROP INDEX idx_users_status;
ALTER TABLE users DROP COLUMN status;
```

**Safe changes:**
- ✅ Add nullable column
- ✅ Add table
- ✅ Add index
- ✅ Increase column size

**Requires coordination:**
- ⚠️ Add NOT NULL column (use default first)
- ⚠️ Rename column (multi-step)
- ⚠️ Drop column (stop using first, then drop)

## Query Optimization

### Analyze Queries
```sql
-- PostgreSQL
EXPLAIN ANALYZE
SELECT * FROM posts WHERE user_id = 123;

-- Look for: Index Scan (good) vs Seq Scan (bad)
```

### Optimization Techniques

**1. Use indexes**
```sql
-- Bad: Full table scan
SELECT * FROM users WHERE email = 'alice@example.com';

-- Good: Index scan
CREATE INDEX idx_users_email ON users(email);
```

**2. Limit results**
```sql
-- Bad: Return everything
SELECT * FROM posts;

-- Good: Paginate
SELECT * FROM posts LIMIT 20 OFFSET 0;
```

**3. Select only needed columns**
```sql
-- Bad
SELECT * FROM users;

-- Good
SELECT id, name, email FROM users;
```

**4. Use EXISTS instead of COUNT**
```sql
-- Bad
SELECT COUNT(*) FROM posts WHERE user_id = 123;

-- Good (if you just need to know if any exist)
SELECT EXISTS(SELECT 1 FROM posts WHERE user_id = 123);
```

**5. Avoid N+1 queries**
```sql
-- Bad: N+1 queries
SELECT * FROM users;
-- Then for each user:
SELECT * FROM posts WHERE user_id = ?;

-- Good: Single query with join
SELECT u.*, p.*
FROM users u
LEFT JOIN posts p ON p.user_id = u.id;
```

## Design Checklist

### Planning
- [ ] Identified entities and relationships?
- [ ] Chosen appropriate database type (SQL/NoSQL)?
- [ ] Normalized to 3NF (SQL)?
- [ ] Planned denormalization strategy?
- [ ] Designed primary keys?
- [ ] Planned indexes?

### Implementation
- [ ] Foreign keys defined (SQL)?
- [ ] Constraints added (NOT NULL, CHECK, UNIQUE)?
- [ ] Appropriate data types chosen?
- [ ] Indexes created for common queries?
- [ ] Migration scripts written?

### Testing
- [ ] Query performance tested?
- [ ] Index usage verified (EXPLAIN)?
- [ ] Migrations tested in staging?
- [ ] Rollback strategy tested?

## Common Pitfalls

### 1. Over-normalization
**Problem:** Too many joins hurt performance  
**Solution:** Denormalize strategically for read-heavy tables

### 2. Missing Indexes
**Problem:** Slow queries  
**Solution:** Index foreign keys and WHERE columns

### 3. Wrong Data Types
**Problem:** Using FLOAT for money  
**Solution:** Always use DECIMAL for currency

### 4. No Migration Strategy
**Problem:** Schema changes break production  
**Solution:** Use migration tools, test in staging

### 5. Premature Optimization
**Problem:** Complex schema before understanding access patterns  
**Solution:** Start normalized, optimize based on actual usage

## Examples

### Example 1: Blog Schema (SQL)
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    content TEXT,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    post_id BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_published_at ON posts(published_at);
CREATE INDEX idx_comments_post_id ON comments(post_id);
```

### Example 2: E-commerce (SQL)
```sql
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    CHECK (price >= 0),
    CHECK (stock_quantity >= 0)
);

CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CHECK (status IN ('pending', 'paid', 'shipped', 'delivered'))
);

CREATE TABLE order_items (
    order_id BIGINT REFERENCES orders(id) ON DELETE CASCADE,
    product_id BIGINT REFERENCES products(id),
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_id, product_id)
);
```

### Example 3: Blog Schema (MongoDB)
```javascript
// users collection
{
  _id: ObjectId("..."),
  email: "alice@example.com",
  username: "alice",
  created_at: ISODate("2025-10-22")
}

// posts collection (embedded comments for small count)
{
  _id: ObjectId("..."),
  user_id: ObjectId("..."),
  author_name: "Alice",  // Denormalized
  title: "My Post",
  content: "...",
  comments: [  // Embedded (if few comments)
    {
      _id: ObjectId("..."),
      user_id: ObjectId("..."),
      author_name: "Bob",
      content: "Great post!",
      created_at: ISODate("...")
    }
  ],
  published_at: ISODate("..."),
  created_at: ISODate("...")
}
```

## Integration with Other Skills

**Combines well with:**
- **api-design** - API endpoints map to database queries
- **critical-thinking** - Evaluate schema trade-offs
- **debugging-methodology** - Debug slow queries

**When both active:**
Use critical thinking for schema decisions, then apply specific patterns from this skill.