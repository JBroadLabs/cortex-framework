---
name: code-review
description: Quick, practical code review checklist for catching common issues. Simple scan for duplication, patterns, errors, security, and maintainability. Use during story creation in existing codebases, brownfield analysis, or code review phases. Focused on quick wins, not exhaustive analysis.
---

# Code Review

Fast, practical checklist for reviewing code quality. Focus on quick wins and common issues.

## When to Use

- Story Composer: Check if story will follow patterns
- Brownfield Architect: Identify tech debt during analysis
- Review Agent: Quick quality check before approval
- Developers: Self-review before submission

## Quick Scan (30 seconds)

### ✅ The 5 Essential Checks

```
1. DUPLICATION: Does this logic exist elsewhere?
2. PATTERNS: Does this match existing code style?
3. ERRORS: Is there error handling?
4. NAMES: Are names clear and consistent?
5. SIMPLE: Is this the simplest solution?
```

**If all 5 pass → Approve**  
**If any fail → Fix before proceeding**

## Common Code Smells

### 1. Duplication

```javascript
// 🚩 Red flag: Same logic in multiple places
function validateUserEmail(email) { /* ... */ }
function validateAdminEmail(email) { /* ... */ }
function validateGuestEmail(email) { /* ... */ }

// ✅ Fix: Extract shared logic
function validateEmail(email) { /* ... */ }
```

**Quick check:**
```bash
# Search for similar function names
grep -r "function.*Email" src/
```

### 2. Inconsistent Error Handling

```javascript
// 🚩 Red flag: Mixed patterns
function getUser() {
  return fetch('/api/users'); // No error handling
}

function getOrder() {
  try {
    return fetch('/api/orders');
  } catch (error) {
    throw error;
  }
}

// ✅ Fix: Consistent pattern
async function getUser() {
  try {
    const res = await fetch('/api/users');
    if (!res.ok) throw new Error('Failed');
    return res.json();
  } catch (error) {
    logger.error('getUser failed', { error });
    throw error;
  }
}
```

### 3. Magic Numbers/Strings

```javascript
// 🚩 Red flag
if (status === 'pending') { /* ... */ }
if (status === 'approved') { /* ... */ }
setTimeout(callback, 3000);

// ✅ Fix
const STATUS = {
  PENDING: 'pending',
  APPROVED: 'approved'
};
const RETRY_DELAY_MS = 3000;

if (status === STATUS.PENDING) { /* ... */ }
setTimeout(callback, RETRY_DELAY_MS);
```

### 4. Long Functions

```javascript
// 🚩 Red flag: Function doing too much (>50 lines)
function processOrder(order) {
  // Validate (10 lines)
  // Calculate totals (15 lines)
  // Apply discounts (20 lines)
  // Update inventory (15 lines)
  // Send notifications (10 lines)
  // Update analytics (10 lines)
}

// ✅ Fix: Extract functions
function processOrder(order) {
  validateOrder(order);
  const total = calculateTotal(order);
  const discounted = applyDiscounts(total);
  updateInventory(order.items);
  sendNotifications(order);
  trackAnalytics(order);
}
```

**Rule of thumb:** Function >50 lines → Consider extracting

### 5. Deep Nesting

```javascript
// 🚩 Red flag: Too much nesting (>3 levels)
if (user) {
  if (user.isActive) {
    if (user.hasPermission) {
      if (user.subscription) {
        // Do something
      }
    }
  }
}

// ✅ Fix: Early returns
if (!user) return;
if (!user.isActive) return;
if (!user.hasPermission) return;
if (!user.subscription) return;

// Do something
```

**Rule of thumb:** Nesting >3 levels → Use early returns or extract

### 6. Poor Names

```javascript
// 🚩 Red flag
function fn(d) {
  const x = d.map(i => i.n);
  return x;
}

// ✅ Fix
function extractUserNames(users) {
  const names = users.map(user => user.name);
  return names;
}
```

## Language-Specific Quick Checks

### Python

```python
# 1. Import style
# ✅ Good: Absolute imports
from myapp.utils import validator

# 🚩 Bad: Relative without __init__.py
from ..utils import validator

# 2. Type hints (if used in codebase)
# ✅ Good
def get_user(id: int) -> dict:
    pass

# 🚩 Bad: Inconsistent
def get_user(id):  # No types when others have them
    pass

# 3. PEP 8 naming
# ✅ Good
def calculate_total():  # snake_case
    MAX_RETRIES = 3     # UPPER_SNAKE_CASE
    
# 🚩 Bad
def calculateTotal():   # camelCase (wrong for Python)
    maxRetries = 3      # Wrong
```

### JavaScript/TypeScript

```javascript
// 1. Path aliases
// ✅ Good: Use aliases if defined
import { Button } from '@/components/Button';

// 🚩 Bad: Relative when alias exists
import { Button } from '../../../components/Button';

// 2. Async/await
// ✅ Good
async function fetchData() {
  try {
    return await api.get();
  } catch (error) {
    throw error;
  }
}

// 🚩 Bad: Missing error handling
async function fetchData() {
  return await api.get(); // Unhandled rejection
}

// 3. Types (TypeScript)
// ✅ Good
interface User {
  id: string;
  name: string;
}

function getUser(id: string): Promise<User> {
  // ...
}

// 🚩 Bad: Using 'any'
function getUser(id: any): Promise<any> {
  // ...
}
```

## Security Quick Checks

```javascript
// 1. Hardcoded secrets
// 🚩 Bad
const API_KEY = 'sk_live_abc123';

// ✅ Good
const API_KEY = process.env.API_KEY;

// 2. SQL injection
// 🚩 Bad
const query = `SELECT * FROM users WHERE id = ${userId}`;

// ✅ Good
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [userId]);

// 3. XSS
// 🚩 Bad (React)
<div dangerouslySetInnerHTML={{ __html: userInput }} />

// ✅ Good
<div>{userInput}</div>

// 4. Input validation
// 🚩 Bad
function createUser(email) {
  return db.users.create({ email }); // No validation
}

// ✅ Good
function createUser(email) {
  if (!isValidEmail(email)) {
    throw new ValidationError('Invalid email');
  }
  return db.users.create({ email });
}
```

## Performance Red Flags

```javascript
// 1. N+1 queries
// 🚩 Bad
const users = await User.findAll();
for (const user of users) {
  user.posts = await Post.findByUser(user.id); // N queries
}

// ✅ Good
const users = await User.findAll({
  include: [Post] // Single query with join
});

// 2. Missing index
-- 🚩 Bad: No index on frequently queried column
SELECT * FROM orders WHERE customer_id = 123; -- Seq scan

-- ✅ Good
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

// 3. Unnecessary re-renders (React)
// 🚩 Bad
function Component({ items }) {
  const sorted = items.sort(); // Runs every render
  return <List items={sorted} />;
}

// ✅ Good
function Component({ items }) {
  const sorted = useMemo(() => items.sort(), [items]);
  return <List items={sorted} />;
}
```

## Architecture Red Flags

```javascript
// 1. Circular dependency
// 🚩 Bad
// userService.js imports emailService.js
// emailService.js imports userService.js

// ✅ Fix: Extract interface or use events

// 2. Tight coupling
// 🚩 Bad
class OrderService {
  constructor() {
    this.db = new PostgresDatabase(); // Hard dependency
  }
}

// ✅ Good
class OrderService {
  constructor(database) { // Inject dependency
    this.db = database;
  }
}

// 3. Missing abstraction
// 🚩 Bad: Business logic in controller
app.post('/orders', async (req, res) => {
  // 50 lines of business logic here
});

// ✅ Good: Extract to service
app.post('/orders', async (req, res) => {
  const order = await orderService.create(req.body);
  res.json(order);
});
```

## Review Checklist

### Pre-Approval (Must Pass All)

**Basics:**
- [ ] No obvious duplication
- [ ] Follows existing patterns
- [ ] Has error handling
- [ ] Clear naming
- [ ] Appropriate complexity

**Imports:**
- [ ] Consistent style (absolute vs relative)
- [ ] Uses path aliases if they exist
- [ ] No circular dependencies

**Security:**
- [ ] No hardcoded secrets
- [ ] Input validated
- [ ] SQL parameterized
- [ ] XSS protected

**Performance:**
- [ ] No N+1 queries
- [ ] Indexes on queried columns
- [ ] No unnecessary re-renders

**Maintainability:**
- [ ] Functions <50 lines
- [ ] Nesting <3 levels
- [ ] Magic numbers extracted
- [ ] Comments for complex logic

## Priority Levels

**🔴 Critical (Block merge):**
- Security vulnerabilities
- Breaking changes
- Circular dependencies
- Data loss risks

**🟡 Important (Fix soon):**
- Performance issues (N+1)
- Missing error handling
- Obvious duplication
- Inconsistent patterns

**🟢 Nice to have (Optional):**
- Long functions
- Better names
- More comments
- Additional tests

## When to Skip Deep Review

**Skip detailed review if:**
- Generated code (tests, migrations)
- Configuration files
- One-line changes
- Documentation only
- Prototypes/experiments

**Always review:**
- Business logic
- Security-sensitive code
- Public APIs
- Database migrations
- Authentication/authorization

## Integration with Other Skills

**Works with:**
- **implementation-best-practices** - What to look for
- **critical-thinking** - Decide priority of issues
- **debugging-methodology** - Find root causes
- **error-handling** - Check error patterns
- **performance-optimization** - Spot bottlenecks

**Used by:**
- Story Composer Agent (check story feasibility)
- Brownfield Architect (identify tech debt)
- Review Agent (quality gate)
- Developers (self-review)

## Quick Reference

```bash
# Search for duplication
grep -r "functionName" src/

# Check import patterns
head -20 src/**/*.{js,ts,py}

# Find long functions
grep -A 50 "^function\|^def" src/ | wc -l

# Security scan
grep -r "API_KEY\|SECRET\|PASSWORD" src/

# Find N+1 patterns
grep -r "for.*await\|forEach.*await" src/
```

---

**Remember:** Focus on quick wins. Don't let perfect be the enemy of good. ✅