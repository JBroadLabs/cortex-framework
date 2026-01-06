---
name: circular-dependency-resolver
description: Expert guidance for detecting, resolving, and preventing circular dependencies in code, modules, databases, and distributed systems. Use when facing import cycles, dependency injection issues, module loading errors, database foreign key cycles, or architectural circular references. Covers detection, refactoring patterns, and prevention strategies.
---

# Circular Dependency Resolver

Comprehensive framework for detecting, resolving, and preventing circular dependencies across all layers of software systems.

## When to Use

Apply this skill when:
- Encountering module import cycle errors
- Facing "Cannot access before initialization" errors
- Debugging dependency injection container issues
- Resolving database foreign key circular references
- Detecting circular references in data structures
- Refactoring tightly coupled modules
- Designing system architecture to prevent cycles
- Troubleshooting module bundler errors
- Resolving npm/yarn circular dependency warnings

## Core Principles

### 1. Detect Early
- Use linters and static analysis tools
- Add circular dependency detection to CI/CD
- Monitor bundle sizes for unexpected growth
- Catch at design time, not runtime

### 2. Break at the Right Level
- Identify the abstraction boundary
- Extract shared interfaces
- Introduce dependency inversion
- Use events instead of direct calls

### 3. Prevent by Design
- Clear module boundaries
- Dependency direction rules (layers)
- Interface segregation
- Loose coupling

### 4. Understand Root Causes
- Tight coupling between modules
- Missing abstraction layers
- Incorrect responsibility assignment
- Bidirectional knowledge requirements

## Types of Circular Dependencies

### 1. Direct Circular Dependency
```
A → B → A
```

### 2. Indirect Circular Dependency
```
A → B → C → A
```

### 3. Self-Dependency
```
A → A (through exports)
```

## Detection

### JavaScript/TypeScript Module Cycles

**Detection tools:**

```bash
# Using madge
npm install -g madge
madge --circular --extensions ts,tsx src/

# Output circular dependencies
madge --circular --extensions ts src/ --json > circular.json

# Visual graph
madge --circular --extensions ts src/ --image graph.png

# Using dpdm
npm install -g dpdm
dpdm --circular --tree src/index.ts

# ESLint plugin
npm install eslint-plugin-import
# Add to .eslintrc: "import/no-cycle": "error"
```

**Manual detection in code:**

```javascript
// circular.js - Simple cycle detector
const fs = require('fs');
const path = require('path');

function detectCircular(entryPoint, visited = new Set(), stack = []) {
  const cycles = [];
  
  function visit(file) {
    const normalized = path.resolve(file);
    
    if (stack.includes(normalized)) {
      // Found cycle!
      const cycleStart = stack.indexOf(normalized);
      const cycle = stack.slice(cycleStart).concat(normalized);
      cycles.push(cycle);
      return;
    }
    
    if (visited.has(normalized)) {
      return;
    }
    
    visited.add(normalized);
    stack.push(normalized);
    
    // Parse imports from file
    const imports = extractImports(normalized);
    
    for (const importPath of imports) {
      visit(importPath);
    }
    
    stack.pop();
  }
  
  visit(entryPoint);
  return cycles;
}

function extractImports(file) {
  const content = fs.readFileSync(file, 'utf8');
  const imports = [];
  
  // Match ES6 imports
  const importRegex = /import\s+.*\s+from\s+['"](.+)['"]/g;
  let match;
  
  while ((match = importRegex.exec(content)) !== null) {
    const importPath = match[1];
    if (importPath.startsWith('.')) {
      // Resolve relative path
      imports.push(path.resolve(path.dirname(file), importPath));
    }
  }
  
  return imports;
}

// Usage
const cycles = detectCircular('./src/index.ts');
if (cycles.length > 0) {
  console.error('Circular dependencies detected:');
  cycles.forEach(cycle => {
    console.error(cycle.join(' → '));
  });
  process.exit(1);
}
```

### Database Circular Foreign Keys

**SQL to detect cycles:**

```sql
-- PostgreSQL: Find circular foreign key references
WITH RECURSIVE fk_tree AS (
  -- Base case: all foreign keys
  SELECT
    tc.table_name AS from_table,
    ccu.table_name AS to_table,
    tc.constraint_name,
    ARRAY[tc.table_name, ccu.table_name] AS path,
    false AS is_cycle
  FROM information_schema.table_constraints tc
  JOIN information_schema.constraint_column_usage ccu
    ON tc.constraint_name = ccu.constraint_name
  WHERE tc.constraint_type = 'FOREIGN KEY'
  
  UNION ALL
  
  -- Recursive case: follow foreign keys
  SELECT
    tree.from_table,
    ccu.table_name AS to_table,
    tc.constraint_name,
    tree.path || ccu.table_name,
    ccu.table_name = ANY(tree.path) AS is_cycle
  FROM fk_tree tree
  JOIN information_schema.table_constraints tc
    ON tc.table_name = tree.to_table
  JOIN information_schema.constraint_column_usage ccu
    ON tc.constraint_name = ccu.constraint_name
  WHERE tc.constraint_type = 'FOREIGN KEY'
    AND NOT (ccu.table_name = ANY(tree.path))
    AND array_length(tree.path, 1) < 10 -- Limit depth
)
SELECT DISTINCT
  from_table,
  to_table,
  path
FROM fk_tree
WHERE is_cycle = true;
```

### Dependency Injection Cycles

**Detection in DI container:**

```typescript
class DIContainer {
  private services = new Map<string, any>();
  private factories = new Map<string, Function>();
  private resolving = new Set<string>(); // Track current resolution
  
  register(name: string, factory: Function) {
    this.factories.set(name, factory);
  }
  
  resolve<T>(name: string): T {
    // Check if already resolved
    if (this.services.has(name)) {
      return this.services.get(name);
    }
    
    // Detect circular dependency
    if (this.resolving.has(name)) {
      const chain = Array.from(this.resolving).concat(name);
      throw new Error(
        `Circular dependency detected: ${chain.join(' → ')}`
      );
    }
    
    this.resolving.add(name);
    
    try {
      const factory = this.factories.get(name);
      if (!factory) {
        throw new Error(`Service '${name}' not registered`);
      }
      
      // Resolve dependencies
      const instance = factory(this);
      this.services.set(name, instance);
      
      return instance;
      
    } finally {
      this.resolving.delete(name);
    }
  }
}

// Usage
const container = new DIContainer();

container.register('userService', (c) => {
  return new UserService(c.resolve('emailService'));
});

container.register('emailService', (c) => {
  return new EmailService(c.resolve('userService')); // Cycle!
});

try {
  container.resolve('userService');
} catch (error) {
  console.error(error.message);
  // "Circular dependency detected: userService → emailService → userService"
}
```

## Resolution Strategies

### 1. Dependency Inversion (Extract Interface)

**Problem:**
```typescript
// userService.ts
import { EmailService } from './emailService';

export class UserService {
  constructor(private emailService: EmailService) {}
  
  async createUser(data: UserData) {
    const user = await this.db.users.create(data);
    await this.emailService.sendWelcome(user);
    return user;
  }
}

// emailService.ts
import { UserService } from './userService'; // CYCLE!

export class EmailService {
  constructor(private userService: UserService) {}
  
  async sendWelcome(user: User) {
    const preferences = await this.userService.getPreferences(user.id);
    // Send email based on preferences
  }
}
```

**Solution: Extract interface**
```typescript
// interfaces.ts
export interface IUserService {
  getPreferences(userId: string): Promise<UserPreferences>;
}

export interface IEmailService {
  sendWelcome(user: User): Promise<void>;
}

// userService.ts
import { IEmailService } from './interfaces';

export class UserService implements IUserService {
  constructor(private emailService: IEmailService) {}
  
  async createUser(data: UserData) {
    const user = await this.db.users.create(data);
    await this.emailService.sendWelcome(user);
    return user;
  }
  
  async getPreferences(userId: string) {
    return this.db.preferences.findByUserId(userId);
  }
}

// emailService.ts
import { IUserService } from './interfaces';

export class EmailService implements IEmailService {
  constructor(private userService: IUserService) {}
  
  async sendWelcome(user: User) {
    const preferences = await this.userService.getPreferences(user.id);
    // Send email based on preferences
  }
}

// No more circular import!
```

### 2. Move Shared Code to New Module

**Problem:**
```typescript
// orders.ts
import { calculateDiscount } from './customers';

export function processOrder(order: Order, customer: Customer) {
  const discount = calculateDiscount(customer);
  return order.total * (1 - discount);
}

// customers.ts
import { getOrderHistory } from './orders'; // CYCLE!

export function calculateDiscount(customer: Customer) {
  const orders = getOrderHistory(customer.id);
  return orders.length > 10 ? 0.1 : 0;
}
```

**Solution: Extract shared logic**
```typescript
// discounts.ts (new module)
export function calculateDiscount(orderCount: number) {
  return orderCount > 10 ? 0.1 : 0;
}

// orders.ts
import { calculateDiscount } from './discounts';

export function processOrder(order: Order, orderCount: number) {
  const discount = calculateDiscount(orderCount);
  return order.total * (1 - discount);
}

export function getOrderHistory(customerId: string) {
  return db.orders.findByCustomer(customerId);
}

// customers.ts
import { getOrderHistory } from './orders';
import { calculateDiscount } from './discounts';

export function getCustomerDiscount(customer: Customer) {
  const orders = getOrderHistory(customer.id);
  return calculateDiscount(orders.length);
}
```

### 3. Dependency Injection (Break at Runtime)

**Problem:**
```typescript
// a.ts
import { B } from './b';

export class A {
  private b = new B(); // Instantiates B
  
  doSomething() {
    this.b.help();
  }
}

// b.ts
import { A } from './a'; // CYCLE!

export class B {
  private a = new A(); // Instantiates A
  
  help() {
    this.a.doSomething();
  }
}
```

**Solution: Inject dependencies**
```typescript
// a.ts
import type { B } from './b'; // Type-only import

export class A {
  constructor(private b: B) {}
  
  doSomething() {
    this.b.help();
  }
}

// b.ts
import type { A } from './a'; // Type-only import

export class B {
  constructor(private a: A) {}
  
  help() {
    this.a.doSomething();
  }
}

// main.ts (composition root)
import { A } from './a';
import { B } from './b';

// Break cycle at instantiation
const b = new B(null as any); // Temporary
const a = new A(b);
b['a'] = a; // Set after creation

// Better: Use DI container
const container = new DIContainer();
container.register('a', (c) => new A(c.resolve('b')));
container.register('b', (c) => new B(c.resolve('a')));
// This will detect the cycle and fail early
```

**Better solution: Rethink the design**
```typescript
// Maybe A and B shouldn't know about each other
// Extract coordinator or mediator

// coordinator.ts
import { A } from './a';
import { B } from './b';

export class Coordinator {
  constructor(private a: A, private b: B) {}
  
  execute() {
    const result = this.a.doSomething();
    this.b.help(result);
  }
}
```

### 4. Event-Based Decoupling

**Problem:**
```typescript
// orderService.ts
import { InventoryService } from './inventoryService';

export class OrderService {
  constructor(private inventory: InventoryService) {}
  
  async createOrder(items: Item[]) {
    await this.inventory.reserve(items);
    return await db.orders.create({ items });
  }
}

// inventoryService.ts
import { OrderService } from './orderService'; // CYCLE!

export class InventoryService {
  constructor(private orders: OrderService) {}
  
  async checkAvailability(itemId: string) {
    const pendingOrders = await this.orders.getPending();
    // Calculate availability
  }
}
```

**Solution: Use events**
```typescript
// events.ts
export class EventBus {
  private handlers = new Map<string, Function[]>();
  
  on(event: string, handler: Function) {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, []);
    }
    this.handlers.get(event)!.push(handler);
  }
  
  emit(event: string, data: any) {
    const handlers = this.handlers.get(event) || [];
    handlers.forEach(handler => handler(data));
  }
}

// orderService.ts
import { EventBus } from './events';

export class OrderService {
  constructor(private events: EventBus) {}
  
  async createOrder(items: Item[]) {
    const order = await db.orders.create({ items });
    
    // Emit event instead of calling inventory directly
    this.events.emit('order.created', { orderId: order.id, items });
    
    return order;
  }
  
  async getPending() {
    return db.orders.findPending();
  }
}

// inventoryService.ts
import { EventBus } from './events';

export class InventoryService {
  constructor(private events: EventBus) {
    // Listen for order events
    this.events.on('order.created', (data) => {
      this.reserve(data.items);
    });
  }
  
  async reserve(items: Item[]) {
    // Reserve inventory
  }
  
  async checkAvailability(itemId: string) {
    // No dependency on OrderService!
    const reserved = await db.reservations.sum(itemId);
    const stock = await db.inventory.get(itemId);
    return stock - reserved;
  }
}

// No circular dependency!
```

### 5. Lazy Loading / Dynamic Import

**Problem:**
```typescript
// a.ts
import { b } from './b';

export const a = {
  doSomething() {
    b.help();
  }
};

// b.ts
import { a } from './a'; // CYCLE!

export const b = {
  help() {
    a.doSomething();
  }
};
```

**Solution: Dynamic import**
```typescript
// a.ts
export const a = {
  async doSomething() {
    const { b } = await import('./b');
    b.help();
  }
};

// b.ts
export const b = {
  async help() {
    const { a } = await import('./a');
    a.doSomething();
  }
};

// Cycle broken at runtime (though this design still smells)
```

### 6. Layered Architecture

**Problem:**
```typescript
// Domain and Infrastructure are interdependent

// domain/User.ts
import { EmailService } from '../infrastructure/EmailService';

export class User {
  notify() {
    new EmailService().send(this.email);
  }
}

// infrastructure/EmailService.ts
import { User } from '../domain/User'; // CYCLE!

export class EmailService {
  send(user: User) {
    // Send email to user.email
  }
}
```

**Solution: Define clear layers**
```
Presentation Layer (UI, Controllers)
       ↓
Application Layer (Use Cases, Services)
       ↓
Domain Layer (Entities, Business Logic)
       ↓
Infrastructure Layer (Database, External APIs)

Rules:
- Each layer can only depend on layers below
- Lower layers cannot depend on upper layers
- Use dependency inversion for infrastructure
```

```typescript
// domain/User.ts (no infrastructure dependency)
export class User {
  constructor(
    public id: string,
    public email: string,
    public name: string
  ) {}
}

// domain/IEmailService.ts (interface in domain)
export interface IEmailService {
  send(to: string, subject: string, body: string): Promise<void>;
}

// application/UserService.ts
import { User } from '../domain/User';
import { IEmailService } from '../domain/IEmailService';

export class UserService {
  constructor(private emailService: IEmailService) {}
  
  async notifyUser(user: User, message: string) {
    await this.emailService.send(user.email, 'Notification', message);
  }
}

// infrastructure/EmailService.ts (implements domain interface)
import { IEmailService } from '../domain/IEmailService';

export class EmailService implements IEmailService {
  async send(to: string, subject: string, body: string) {
    // Actual email sending logic
  }
}

// No circular dependency! Dependency flows downward.
```

## Database Circular Foreign Keys

### Problem

```sql
-- Circular foreign keys
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  favorite_post_id INT REFERENCES posts(id) -- References posts
);

CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  author_id INT REFERENCES users(id) -- References users
);

-- Can't create either table first!
```

### Solutions

**1. Make one FK nullable**
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  favorite_post_id INT -- No FK yet
);

CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  author_id INT NOT NULL REFERENCES users(id)
);

-- Add FK after both tables exist
ALTER TABLE users
  ADD CONSTRAINT fk_favorite_post
  FOREIGN KEY (favorite_post_id)
  REFERENCES posts(id);
```

**2. Use junction table**
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY
);

CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  author_id INT NOT NULL REFERENCES users(id)
);

-- Separate table for favorites
CREATE TABLE user_favorites (
  user_id INT NOT NULL REFERENCES users(id),
  post_id INT NOT NULL REFERENCES posts(id),
  PRIMARY KEY (user_id, post_id)
);
```

**3. Deferred constraints (PostgreSQL)**
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  favorite_post_id INT
);

CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  author_id INT NOT NULL
);

-- Add constraints as DEFERRABLE
ALTER TABLE users
  ADD CONSTRAINT fk_favorite_post
  FOREIGN KEY (favorite_post_id)
  REFERENCES posts(id)
  DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE posts
  ADD CONSTRAINT fk_author
  FOREIGN KEY (author_id)
  REFERENCES users(id)
  DEFERRABLE INITIALLY DEFERRED;

-- Within transaction, constraints checked at commit
BEGIN;
SET CONSTRAINTS ALL DEFERRED;
INSERT INTO users (id) VALUES (1);
INSERT INTO posts (id, author_id) VALUES (1, 1);
UPDATE users SET favorite_post_id = 1 WHERE id = 1;
COMMIT;
```

## Prevention Strategies

### 1. Module Structure Rules

```
src/
├── core/           # Core domain, no dependencies
│   ├── entities/
│   └── interfaces/
├── services/       # Can depend on core
│   ├── userService.ts
│   └── orderService.ts
├── infrastructure/ # Implements core interfaces
│   ├── database/
│   └── api/
└── presentation/   # Depends on services
    └── controllers/

Rules:
1. Core cannot import from services, infrastructure, or presentation
2. Services can import from core but not from each other (use events)
3. Infrastructure implements core interfaces
4. Presentation coordinates services
```

### 2. Dependency Direction Enforcement

**Using ESLint:**

```javascript
// .eslintrc.js
module.exports = {
  plugins: ['import'],
  rules: {
    'import/no-cycle': ['error', { maxDepth: Infinity }],
    'import/no-restricted-paths': ['error', {
      zones: [
        // Core cannot import from anywhere
        {
          target: './src/core',
          from: './src',
          except: ['./core']
        },
        // Services cannot import from infrastructure
        {
          target: './src/services',
          from: './src/infrastructure'
        },
        // Services cannot import from each other
        {
          target: './src/services',
          from: './src/services',
          except: ['./index.ts']
        }
      ]
    }]
  }
};
```

### 3. Dependency Graphs in CI

```yaml
# .github/workflows/check-dependencies.yml
name: Check Dependencies

on: [pull_request]

jobs:
  check-circular:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install dependencies
        run: npm ci
      
      - name: Check for circular dependencies
        run: |
          npx madge --circular --extensions ts,tsx src/
          if [ $? -ne 0 ]; then
            echo "Circular dependencies detected!"
            exit 1
          fi
      
      - name: Generate dependency graph
        run: npx madge --extensions ts src/ --image deps.png
      
      - name: Upload graph
        uses: actions/upload-artifact@v2
        with:
          name: dependency-graph
          path: deps.png
```

### 4. Design Principles

**Single Responsibility Principle:**
```typescript
// Bad: UserService does too much
class UserService {
  createUser() {}
  sendEmail() {} // Email responsibility
  chargePayment() {} // Payment responsibility
}

// Good: Separate concerns
class UserService {
  createUser() {}
}

class EmailService {
  send() {}
}

class PaymentService {
  charge() {}
}
```

**Dependency Inversion Principle:**
```typescript
// Bad: High-level depends on low-level
class UserService {
  constructor(private db: PostgresDatabase) {}
}

// Good: Both depend on abstraction
interface IDatabase {
  save(entity: any): Promise<void>;
}

class UserService {
  constructor(private db: IDatabase) {}
}

class PostgresDatabase implements IDatabase {
  save(entity: any) {}
}
```

**Interface Segregation:**
```typescript
// Bad: Fat interface creates dependencies
interface IUserService {
  create(): void;
  update(): void;
  delete(): void;
  sendEmail(): void;
  generateReport(): void;
}

// Good: Small, focused interfaces
interface IUserCreator {
  create(): void;
}

interface IUserUpdater {
  update(): void;
}

interface IEmailSender {
  sendEmail(): void;
}
```

## Common Patterns

### Mediator Pattern

```typescript
// Instead of services calling each other
export class Mediator {
  constructor(
    private userService: UserService,
    private emailService: EmailService,
    private paymentService: PaymentService
  ) {}
  
  async registerUser(userData: UserData) {
    // Coordinate services without them knowing about each other
    const user = await this.userService.create(userData);
    await this.emailService.sendWelcome(user);
    await this.paymentService.setupAccount(user);
    return user;
  }
}
```

### Observer Pattern

```typescript
// Services subscribe to events instead of calling each other
class EventEmitter {
  private listeners = new Map<string, Function[]>();
  
  on(event: string, listener: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(listener);
  }
  
  emit(event: string, data: any) {
    const listeners = this.listeners.get(event) || [];
    listeners.forEach(listener => listener(data));
  }
}

// userService.ts
class UserService {
  constructor(private events: EventEmitter) {}
  
  async create(data: UserData) {
    const user = await db.users.create(data);
    this.events.emit('user.created', user);
    return user;
  }
}

// emailService.ts
class EmailService {
  constructor(events: EventEmitter) {
    events.on('user.created', (user) => {
      this.sendWelcome(user);
    });
  }
  
  async sendWelcome(user: User) {
    // Send email
  }
}
```

### Facade Pattern

```typescript
// Instead of complex interdependencies, provide simple interface
class OrderFacade {
  constructor(
    private orderService: OrderService,
    private inventoryService: InventoryService,
    private paymentService: PaymentService,
    private shippingService: ShippingService
  ) {}
  
  async placeOrder(orderData: OrderData) {
    // Facade coordinates without services knowing each other
    await this.inventoryService.reserve(orderData.items);
    const payment = await this.paymentService.charge(orderData.payment);
    const order = await this.orderService.create(orderData);
    await this.shippingService.schedule(order);
    return order;
  }
}
```

## Troubleshooting Guide

### "Cannot access 'X' before initialization"

**Cause:** Circular dependency in module initialization

**Fix:**
1. Find the cycle using madge or dpdm
2. Apply one of the resolution strategies above
3. Consider if both modules should exist

### "Maximum call stack size exceeded"

**Cause:** Runtime circular reference (e.g., objects referencing each other)

**Fix:**
```typescript
// Add circular reference handling
function stringify(obj: any, seen = new WeakSet()) {
  if (seen.has(obj)) {
    return '[Circular]';
  }
  
  if (typeof obj === 'object' && obj !== null) {
    seen.add(obj);
  }
  
  // ... stringify logic
}
```

### Webpack "Module not found" or "Can't resolve"

**Cause:** Circular dependency confusing bundler

**Fix:**
1. Detect cycles: `npx madge --circular src/`
2. Break cycles using strategies above
3. Use dynamic imports as last resort

## Checklist

### Detection
- [ ] Run circular dependency checker (madge, dpdm)
- [ ] Add ESLint import/no-cycle rule
- [ ] Check database foreign keys for cycles
- [ ] Review DI container for cycles

### Resolution
- [ ] Identified root cause (tight coupling, wrong abstraction)?
- [ ] Extracted shared interfaces?
- [ ] Created new module for shared code?
- [ ] Applied dependency inversion?
- [ ] Considered event-based decoupling?

### Prevention
- [ ] Defined clear module boundaries?
- [ ] Established layered architecture?
- [ ] Added CI checks for circular deps?
- [ ] Documented dependency rules?
- [ ] Code reviews check for cycles?

## Integration with Other Skills

**Combines well with:**
- **debugging-methodology** - Debug circular dependency errors
- **critical-thinking** - Evaluate refactoring options
- **api-design** - Design APIs to avoid circular refs
- **database-schema-design** - Avoid circular foreign keys

**When both active:**
Use critical thinking to evaluate which resolution strategy fits best, then apply specific refactoring pattern from this skill.