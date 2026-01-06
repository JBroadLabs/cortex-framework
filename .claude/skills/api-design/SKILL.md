---
name: api-design
description: Comprehensive API design guidance covering REST, GraphQL, and RPC patterns. Use when designing APIs, evaluating API architecture, defining endpoints, structuring requests/responses, versioning strategies, or making API-related decisions. Provides best practices for developer experience, consistency, and maintainability.
---

# API Design

Comprehensive framework for designing high-quality APIs that are intuitive, consistent, and maintainable.

## When to Use

Apply this skill when:
- Designing new APIs or endpoints
- Evaluating existing API architecture
- Making API-related decisions (REST vs GraphQL vs RPC)
- Defining request/response structures
- Planning API versioning strategy
- Reviewing API documentation
- Optimizing developer experience
- Standardizing API patterns across services

## Core Principles

### 1. Developer Experience First
- APIs are products for developers
- Optimize for ease of understanding and use
- Provide excellent documentation and examples
- Make common cases simple, complex cases possible

### 2. Consistency Over Cleverness
- Predictable patterns reduce cognitive load
- Consistent naming, structure, and behavior
- Follow established conventions
- Surprise is the enemy of good API design

### 3. Evolution Over Perfection
- Plan for change from day one
- Version strategically
- Deprecate gracefully
- Balance stability with improvement

### 4. Clarity Over Brevity
- Clear names beat short names
- Explicit is better than implicit
- Self-documenting designs reduce support burden

## API Style Selection

### REST (Representational State Transfer)

**Best for:**
- Resource-oriented operations (CRUD)
- Public APIs with broad client variety
- Caching requirements
- Standardization and tooling support

**Characteristics:**
```
GET    /users           # List users
GET    /users/123       # Get specific user
POST   /users           # Create user
PUT    /users/123       # Update user (full)
PATCH  /users/123       # Update user (partial)
DELETE /users/123       # Delete user
```

**When to choose:**
- Resources map naturally to URLs
- Standard HTTP semantics fit your use case
- Clients benefit from HTTP caching
- Wide client ecosystem (mobile, web, IoT)

### GraphQL

**Best for:**
- Complex data graphs with relationships
- Clients need flexible queries
- Multiple client types with different needs
- Reducing over-fetching and under-fetching

**Characteristics:**
```graphql
query {
  user(id: "123") {
    name
    email
    posts(limit: 10) {
      title
      comments { author }
    }
  }
}
```

**When to choose:**
- Clients need tailored data shapes
- Strong typing benefits development
- Real-time updates are common (subscriptions)
- Backend can handle query complexity

### RPC (Remote Procedure Call)

**Best for:**
- Action-oriented operations (not resource CRUD)
- Internal microservices communication
- High-performance requirements
- Strong typing with code generation (gRPC)

**Characteristics:**
```
// gRPC example
rpc GetUser(GetUserRequest) returns (User);
rpc CreateUser(CreateUserRequest) returns (User);
rpc SendEmail(SendEmailRequest) returns (SendEmailResponse);
```

**When to choose:**
- Operations don't map to resources
- Performance is critical (gRPC with protobuf)
- Internal services with shared type definitions
- Streaming requirements (bidirectional)

### Decision Matrix

| Factor | REST | GraphQL | RPC |
|--------|------|---------|-----|
| Resource-oriented | ✅ Excellent | ⚠️ Possible | ❌ Poor fit |
| Action-oriented | ⚠️ Awkward | ✅ Good | ✅ Excellent |
| Flexible queries | ❌ Fixed | ✅ Excellent | ❌ Fixed |
| Caching | ✅ HTTP built-in | ⚠️ Complex | ⚠️ Custom |
| Real-time | ⚠️ Polling/SSE | ✅ Subscriptions | ✅ Streaming |
| Learning curve | ✅ Low | ⚠️ Medium | ⚠️ Medium |
| Tooling | ✅ Ubiquitous | ✅ Good | ✅ Excellent (gRPC) |
| Performance | ⚠️ Good | ⚠️ Variable | ✅ Excellent |

## REST API Design

### URL Structure

**Good patterns:**
```
# Resource hierarchy
GET /organizations/123/teams/456/members

# Logical grouping
GET /users/123/settings
GET /users/123/notifications

# Actions as subresources (when REST CRUD doesn't fit)
POST /users/123/password-reset
POST /orders/456/cancel
POST /invoices/789/send
```

**Bad patterns:**
```
# Verbs in URLs (use HTTP methods instead)
❌ GET /getUser/123
❌ POST /createUser
❌ POST /deleteUser/123

# Non-resource concepts forced into REST
❌ GET /search?q=...  # Better: POST /searches with body
❌ GET /calculate?x=1&y=2  # Consider RPC instead

# Deep nesting (hard to maintain)
❌ GET /a/1/b/2/c/3/d/4/e/5
```

### HTTP Methods

**Idempotent operations** (safe to retry):
- `GET` - Retrieve resource (no side effects)
- `PUT` - Replace resource (same result if called multiple times)
- `DELETE` - Remove resource (same result if called multiple times)
- `HEAD` - Like GET but no body
- `OPTIONS` - Describe available operations

**Non-idempotent operations** (may change on retry):
- `POST` - Create resource or trigger action
- `PATCH` - Partial update

**Usage guidelines:**
```
GET    /users/123        # Read - always safe, cacheable
POST   /users            # Create - returns 201 + Location header
PUT    /users/123        # Replace entire resource
PATCH  /users/123        # Partial update (send only changed fields)
DELETE /users/123        # Remove resource, returns 204 or 200
```

### Status Codes

**Success codes:**
- `200 OK` - Successful GET, PUT, PATCH, DELETE (with body)
- `201 Created` - Successful POST (include Location header)
- `202 Accepted` - Request accepted for async processing
- `204 No Content` - Successful operation with no response body

**Client error codes:**
- `400 Bad Request` - Malformed request or validation error
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Authenticated but not authorized
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Business logic conflict (e.g., duplicate email)
- `422 Unprocessable Entity` - Validation failed (detailed errors)
- `429 Too Many Requests` - Rate limit exceeded

**Server error codes:**
- `500 Internal Server Error` - Unexpected server error
- `502 Bad Gateway` - Upstream service error
- `503 Service Unavailable` - Temporary unavailability
- `504 Gateway Timeout` - Upstream timeout

**Be specific:**
```json
// Bad: Generic 400 for everything
{
  "error": "Bad request"
}

// Good: Specific status + detailed errors
// 422 Unprocessable Entity
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "fields": {
      "email": ["Must be a valid email address"],
      "age": ["Must be at least 18"]
    }
  }
}
```

### Request/Response Structure

**Consistent envelope:**
```json
// Success response
{
  "data": {
    "id": "123",
    "name": "Alice",
    "email": "alice@example.com"
  },
  "meta": {
    "timestamp": "2025-10-22T10:00:00Z",
    "request_id": "req_abc123"
  }
}

// Error response
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User with ID 123 not found",
    "details": {
      "user_id": "123"
    }
  },
  "meta": {
    "timestamp": "2025-10-22T10:00:00Z",
    "request_id": "req_abc123"
  }
}

// Collection response
{
  "data": [
    { "id": "1", "name": "Alice" },
    { "id": "2", "name": "Bob" }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  },
  "links": {
    "self": "/users?page=1",
    "next": "/users?page=2",
    "last": "/users?page=8"
  }
}
```

### Filtering, Sorting, Pagination

**Query parameters for collections:**
```
# Filtering
GET /users?status=active&role=admin
GET /products?price_min=10&price_max=100
GET /orders?created_after=2025-01-01

# Sorting
GET /users?sort=created_at          # Ascending (default)
GET /users?sort=-created_at         # Descending (- prefix)
GET /users?sort=last_name,first_name  # Multiple fields

# Pagination
GET /users?page=2&per_page=50       # Page-based
GET /users?cursor=xyz123&limit=50   # Cursor-based (better for large datasets)

# Search
GET /users?q=alice                  # Simple search
POST /users/search                  # Complex search (use POST with body)
{
  "query": "alice",
  "filters": { "role": "admin" },
  "sort": ["-created_at"]
}
```

**Cursor-based pagination** (recommended for large datasets):
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTIzfQ==",
    "has_more": true
  }
}
```

### Versioning Strategies

**1. URL Versioning** (Most common, clearest)
```
GET /v1/users/123
GET /v2/users/123
```
**Pros:** Explicit, easy to route, cache-friendly
**Cons:** Clutters URLs, harder to evolve incrementally

**2. Header Versioning**
```
GET /users/123
Accept: application/vnd.myapi.v2+json
```
**Pros:** Clean URLs, more RESTful
**Cons:** Harder to test in browser, less visible

**3. Content Negotiation**
```
GET /users/123
Accept: application/json; version=2
```
**Pros:** Standards-based, flexible
**Cons:** Complex, less common

**Recommendation:** Use URL versioning for major versions, feature flags for minor changes.

**Version policy:**
```
v1 → v2 migration:
- Announce v2 at least 6 months before v1 deprecation
- Run v1 and v2 in parallel during transition
- Set sunset date for v1
- Provide migration guide
- Monitor v1 usage and reach out to heavy users
```

### Authentication & Authorization

**Common patterns:**

**API Keys** (Simple, for server-to-server)
```
GET /api/v1/users
Authorization: Bearer sk_live_abc123...
```

**OAuth 2.0** (For user-based access)
```
GET /api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**JWT (JSON Web Tokens)**
```json
{
  "sub": "user_123",
  "scope": ["read:users", "write:orders"],
  "exp": 1698000000
}
```

**Best practices:**
- Use HTTPS always (no exceptions)
- Implement rate limiting per key/user
- Support key rotation
- Include scopes/permissions in tokens
- Log authentication failures (security monitoring)
- Expire tokens appropriately (short for access, long for refresh)

### Rate Limiting

**Headers to include:**
```
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1698000000
Retry-After: 3600
```

**When limit exceeded:**
```
HTTP/1.1 429 Too Many Requests
Retry-After: 3600

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 1 hour.",
    "retry_after": 3600
  }
}
```

**Rate limit strategies:**
- Per API key
- Per user
- Per IP (for unauthenticated)
- Different limits for different tiers (free vs paid)
- Burst allowance for spikes

### Error Handling

**Comprehensive error response:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "fields": {
      "email": [
        "Email is required",
        "Email must be valid"
      ],
      "password": [
        "Password must be at least 8 characters"
      ]
    },
    "documentation_url": "https://docs.api.com/errors/VALIDATION_ERROR",
    "request_id": "req_abc123"
  }
}
```

**Error code patterns:**
```
# Scoped error codes
USER_NOT_FOUND
PAYMENT_FAILED
INVENTORY_INSUFFICIENT

# Or namespaced
user.not_found
payment.failed
inventory.insufficient

# Avoid generic codes
ERROR
FAILED
INVALID
```

**Retry guidance:**
```json
{
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Service temporarily unavailable",
    "retryable": true,
    "retry_after": 60
  }
}
```

## GraphQL API Design

### Schema Design

**Type definitions:**
```graphql
type User {
  id: ID!
  email: String!
  name: String
  posts: [Post!]!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  published: Boolean!
}

type Query {
  user(id: ID!): User
  users(filter: UserFilter, limit: Int, offset: Int): UserConnection!
  post(id: ID!): Post
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
  deleteUser(id: ID!): DeleteUserPayload!
}

input CreateUserInput {
  email: String!
  name: String
}

type CreateUserPayload {
  user: User
  errors: [Error!]
}
```

**Connection pattern** (for pagination):
```graphql
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

# Usage
query {
  users(first: 10, after: "cursor123") {
    edges {
      node { id name }
      cursor
    }
    pageInfo { hasNextPage endCursor }
  }
}
```

### Error Handling in GraphQL

**Errors array:**
```json
{
  "data": {
    "createUser": null
  },
  "errors": [
    {
      "message": "Email already exists",
      "extensions": {
        "code": "EMAIL_ALREADY_EXISTS",
        "field": "email"
      }
    }
  ]
}
```

**Union types for explicit errors:**
```graphql
type CreateUserPayload {
  result: CreateUserResult!
}

union CreateUserResult = CreateUserSuccess | ValidationError | DuplicateEmailError

type CreateUserSuccess {
  user: User!
}

type ValidationError {
  fields: [FieldError!]!
}

type DuplicateEmailError {
  email: String!
}
```

### N+1 Query Problem

**Problem:**
```graphql
query {
  users {
    name
    posts {  # N queries (one per user)
      title
    }
  }
}
```

**Solutions:**
1. DataLoader (batching)
2. Eager loading in resolvers
3. Database query optimization
4. Field-level caching

## RPC API Design (gRPC)

### Service Definition

```protobuf
syntax = "proto3";

service UserService {
  rpc GetUser (GetUserRequest) returns (User);
  rpc ListUsers (ListUsersRequest) returns (ListUsersResponse);
  rpc CreateUser (CreateUserRequest) returns (User);
  rpc UpdateUser (UpdateUserRequest) returns (User);
  rpc DeleteUser (DeleteUserRequest) returns (google.protobuf.Empty);
  
  // Streaming
  rpc StreamUserUpdates (StreamUserUpdatesRequest) returns (stream User);
}

message User {
  string id = 1;
  string email = 2;
  string name = 3;
  int64 created_at = 4;
}

message GetUserRequest {
  string id = 1;
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
  string filter = 3;
}

message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;
}
```

### Error Handling in gRPC

**Status codes:**
```
OK (0) - Success
INVALID_ARGUMENT (3) - Client error
NOT_FOUND (5) - Resource not found
ALREADY_EXISTS (6) - Duplicate
PERMISSION_DENIED (7) - Authorization failure
RESOURCE_EXHAUSTED (8) - Rate limit
FAILED_PRECONDITION (9) - Business logic error
INTERNAL (13) - Server error
UNAVAILABLE (14) - Service unavailable
```

**Rich error details:**
```protobuf
import "google/rpc/error_details.proto";

// Server sends
status {
  code: 3  // INVALID_ARGUMENT
  message: "Invalid email format"
  details: [
    {
      type: "google.rpc.BadRequest"
      value: {
        field_violations: [
          {
            field: "email"
            description: "Must be valid email"
          }
        ]
      }
    }
  ]
}
```

## API Documentation

### What to Document

**For each endpoint:**

1. **Purpose** - What does it do?
2. **Authentication** - What auth is required?
3. **Request** - Parameters, headers, body
4. **Response** - Success and error responses
5. **Examples** - Real curl/code examples
6. **Rate limits** - Usage restrictions
7. **Errors** - Possible error codes and meanings

**Example documentation:**

````markdown
## Create User

Creates a new user account.

### Endpoint
```
POST /v1/users
```

### Authentication
Requires API key with `users:write` scope.

### Request Body
```json
{
  "email": "alice@example.com",
  "name": "Alice Smith",
  "role": "member"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | User's email (must be unique) |
| name | string | No | User's full name |
| role | string | No | User role (default: "member") |

### Response
**Success (201 Created)**
```json
{
  "data": {
    "id": "usr_abc123",
    "email": "alice@example.com",
    "name": "Alice Smith",
    "role": "member",
    "created_at": "2025-10-22T10:00:00Z"
  }
}
```

**Error (422 Unprocessable Entity)**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "fields": {
      "email": ["Email already exists"]
    }
  }
}
```

### Example
```bash
curl -X POST https://api.example.com/v1/users \
  -H "Authorization: Bearer sk_live_abc123" \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","name":"Alice Smith"}'
```

### Rate Limits
- 100 requests per minute per API key
- Burst limit: 10 requests per second

### See Also
- [Get User](#get-user)
- [Authentication Guide](/docs/authentication)
````

### Interactive Documentation

**Use tools:**
- **OpenAPI/Swagger** for REST APIs
- **GraphQL Playground** for GraphQL
- **gRPC reflection** + UI tools for gRPC

**Generate from code:**
```yaml
# OpenAPI spec
openapi: 3.0.0
paths:
  /users:
    post:
      summary: Create user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
```

## API Design Checklist

### Design Phase
- [ ] Chosen appropriate style (REST/GraphQL/RPC)?
- [ ] Defined clear resource hierarchy or service methods?
- [ ] Consistent naming conventions?
- [ ] Planned for versioning?
- [ ] Considered pagination for collections?
- [ ] Designed error responses?
- [ ] Planned authentication strategy?
- [ ] Defined rate limits?

### Implementation Phase
- [ ] Used appropriate HTTP methods/status codes?
- [ ] Implemented proper error handling?
- [ ] Added request validation?
- [ ] Included request IDs for tracing?
- [ ] Implemented rate limiting?
- [ ] Added logging for debugging?
- [ ] Used idempotency keys where needed?

### Documentation Phase
- [ ] Documented all endpoints/methods?
- [ ] Included request/response examples?
- [ ] Listed possible error codes?
- [ ] Provided authentication guide?
- [ ] Created getting started tutorial?
- [ ] Generated interactive docs (Swagger/GraphQL Playground)?
- [ ] Documented rate limits?

### Testing Phase
- [ ] Unit tests for business logic?
- [ ] Integration tests for endpoints?
- [ ] Error case testing?
- [ ] Rate limit testing?
- [ ] Load testing?
- [ ] Security testing (auth, injection)?

### Deployment Phase
- [ ] Versioning strategy in place?
- [ ] Monitoring and alerting configured?
- [ ] Rate limiting enforced?
- [ ] Logging sufficient for debugging?
- [ ] Documentation accessible?
- [ ] Deprecation policy defined?

## Common Pitfalls

### 1. Breaking Changes Without Versioning
**Problem:** Adding required fields, removing fields, changing types
**Solution:** Version your API, maintain backward compatibility

### 2. Inconsistent Naming
**Problem:** Mix of camelCase, snake_case, PascalCase
**Solution:** Pick one convention (typically camelCase for JSON) and enforce it

### 3. Poor Error Messages
**Problem:** Generic errors that don't help debugging
**Solution:** Specific error codes, field-level errors, documentation links

### 4. No Pagination
**Problem:** Returning all results causes performance issues
**Solution:** Always paginate collections, document limits

### 5. Ignoring Idempotency
**Problem:** POST requests fail halfway, retry creates duplicates
**Solution:** Idempotency keys for critical operations

### 6. Overfetching/Underfetching
**Problem:** REST returns too much or too little data
**Solution:** GraphQL for complex needs, or REST with field selection

### 7. No Rate Limiting
**Problem:** Abuse or bugs can overwhelm service
**Solution:** Implement and document rate limits from day one

### 8. Leaking Implementation Details
**Problem:** Database IDs, internal codes in responses
**Solution:** Use opaque IDs, abstract internal concepts

## Examples

### Example 1: RESTful CRUD API

```
# Users Resource
GET    /v1/users                    # List users
GET    /v1/users/:id                # Get user
POST   /v1/users                    # Create user
PATCH  /v1/users/:id                # Update user
DELETE /v1/users/:id                # Delete user

# Nested Resources
GET    /v1/users/:id/posts          # User's posts
POST   /v1/users/:id/posts          # Create post for user

# Actions (when CRUD doesn't fit)
POST   /v1/users/:id/password-reset # Trigger password reset
POST   /v1/users/:id/verify-email   # Verify email
```

### Example 2: GraphQL Schema

```graphql
type Query {
  user(id: ID!): User
  users(filter: UserFilter, pagination: PaginationInput): UserConnection!
  currentUser: User
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
  deleteUser(id: ID!): DeleteUserPayload!
  resetPassword(email: String!): ResetPasswordPayload!
}

type Subscription {
  userUpdated(id: ID!): User!
  newNotification: Notification!
}
```

### Example 3: gRPC Service

```protobuf
service OrderService {
  rpc CreateOrder(CreateOrderRequest) returns (Order);
  rpc GetOrder(GetOrderRequest) returns (Order);
  rpc ListOrders(ListOrdersRequest) returns (stream Order);
  rpc CancelOrder(CancelOrderRequest) returns (google.protobuf.Empty);
  
  // Bidirectional streaming for real-time updates
  rpc TrackOrders(stream TrackOrdersRequest) returns (stream OrderUpdate);
}
```

## Integration with Other Skills

**Combines well with:**
- **critical-thinking** - Apply to API architecture decisions
- **debugging-methodology** - Debug API issues systematically
- **security** - Security considerations in API design

**When both active:**
Use critical thinking to evaluate API design trade-offs, then apply this skill's specific patterns and best practices.