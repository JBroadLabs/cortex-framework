---
name: implementation-best-practices
description: Tactical guidance for writing clean, maintainable code that integrates well with existing codebases. Covers import conventions, code organization, avoiding duplication, pattern matching, and common implementation pitfalls. Use when implementing features in established codebases, following team conventions, or ensuring code consistency.
---

# Implementation Best Practices

Tactical guidance for writing code that integrates seamlessly with existing codebases and follows established conventions.

## When to Use

Apply this skill when:
- Implementing features in existing codebases
- Adding code to established projects
- Following team conventions and patterns
- Ensuring consistency with existing code
- Avoiding common implementation mistakes
- Working with legacy code
- Onboarding to new codebases
- Code reviews (as reviewer or reviewee)

## Core Principles

### 1. Discovery Before Creation
**Always search for existing patterns before writing new code**
- Check if functionality already exists
- Look for similar implementations
- Review established patterns
- Find relevant utilities/helpers

### 2. Pattern Consistency
**Match the existing patterns in the codebase**
- Follow naming conventions
- Use same import style
- Match file organization
- Maintain code structure
- Keep consistent formatting

### 3. Simplicity First
**Start simple, add complexity only when needed**
- Don't over-engineer
- Avoid premature abstraction
- Follow YAGNI (You Aren't Gonna Need It)
- Match existing complexity level

### 4. Integration Over Isolation
**Make code that works with what exists**
- Reuse existing utilities
- Follow established interfaces
- Don't duplicate logic
- Maintain backward compatibility

## Discovery & Pattern Recognition

### Before Writing Code: The Discovery Checklist

```bash
# 1. Search for similar functionality
grep -r "functionName" src/
git grep "pattern" 

# 2. Check common locations
ls utils/
ls helpers/
ls lib/
ls services/

# 3. Review similar files
# Find files that do similar things
find . -name "*user*" -type f

# 4. Check imports in similar files
# See how others import and use utilities
head -20 src/components/Dashboard.tsx

# 5. Look at tests
# Tests show how code is actually used
cat src/utils/__tests__/validators.test.js
```

### Pattern Recognition Examples

**Example 1: Import Patterns**
```javascript
// Step 1: Check 2-3 existing files
// File: src/components/UserList.tsx
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/Button';
import { fetchUsers } from '@/api/users';

// File: src/components/Dashboard.tsx
import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '@/components/ui/Card';
import { fetchStats } from '@/api/stats';

// Pattern identified:
// - External libs: direct import
// - Components: @/components/* path alias
// - API: @/api/* path alias

// Step 2: Match the pattern
// ✅ Good: Your new file
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Table } from '@/components/ui/Table';
import { fetchOrders } from '@/api/orders';

// ❌ Bad: Inconsistent
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Table } from '../../components/ui/Table'; // Wrong!
import { fetchOrders } from '../api/orders'; // Wrong!
```

**Example 2: Error Handling Patterns**
```javascript
// Step 1: Check existing API calls
// File: src/api/users.js
export async function getUser(id) {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) {
      throw new ApiError(response.status, await response.text());
    }
    return await response.json();
  } catch (error) {
    logger.error('Failed to fetch user', { id, error });
    throw error;
  }
}

// Pattern identified:
// - try-catch wraps fetch
// - Check response.ok
// - Throw custom ApiError
// - Log with context
// - Re-throw error

// Step 2: Match the pattern
// ✅ Good: Your new API call
export async function getOrder(id) {
  try {
    const response = await fetch(`/api/orders/${id}`);
    if (!response.ok) {
      throw new ApiError(response.status, await response.text());
    }
    return await response.json();
  } catch (error) {
    logger.error('Failed to fetch order', { id, error });
    throw error;
  }
}

// ❌ Bad: Different pattern
export async function getOrder(id) {
  const response = await fetch(`/api/orders/${id}`); // No try-catch
  return response.json(); // No error checking
}
```

**Example 3: Component Structure Patterns**
```typescript
// Step 1: Check existing components
// File: src/components/UserCard.tsx
interface UserCardProps {
  user: User;
  onEdit?: (user: User) => void;
}

export function UserCard({ user, onEdit }: UserCardProps) {
  // Component logic
  return (/* JSX */);
}

// File: src/components/ProductCard.tsx
interface ProductCardProps {
  product: Product;
  onSelect?: (product: Product) => void;
}

export function ProductCard({ product, onSelect }: ProductCardProps) {
  // Component logic
  return (/* JSX */);
}

// Pattern identified:
// - Interface named {ComponentName}Props
// - Props destructured in function params
// - Named export (not default)
// - Optional callbacks with ? notation

// Step 2: Match the pattern
// ✅ Good: Your new component
interface OrderCardProps {
  order: Order;
  onView?: (order: Order) => void;
}

export function OrderCard({ order, onView }: OrderCardProps) {
  // Component logic
  return (/* JSX */);
}

// ❌ Bad: Different pattern
type Props = {  // Wrong: Should be OrderCardProps
  order: Order;
  onView: (order: Order) => void; // Wrong: Should be optional
};

export default function OrderCard(props: Props) { // Wrong: default export, no destructuring
  return (/* JSX */);
}
```

## Import Conventions

### Python Import Best Practices

**Problem: Relative imports fail without `__init__.py`**

```python
# Project structure WITHOUT __init__.py
myapp/
  utils/
    validators.py
  services/
    user_service.py

# ❌ Bad: Relative import (fails without __init__.py)
# In user_service.py
from ..utils.validators import validate_email  # ModuleNotFoundError

# ✅ Good Option 1: Absolute imports
from myapp.utils.validators import validate_email

# ✅ Good Option 2: Add __init__.py files
myapp/
  __init__.py
  utils/
    __init__.py
    validators.py
  services/
    __init__.py
    user_service.py

# Now relative imports work
from ..utils.validators import validate_email
```

**When to use which:**

```python
# Absolute imports (RECOMMENDED)
# ✅ Pros: Work everywhere, clear, no __init__.py needed
# ❌ Cons: Longer import statements
from myapp.utils.validators import validate_email
from myapp.services.auth import authenticate
from myapp.models.user import User

# Relative imports
# ✅ Pros: Shorter, easier refactoring
# ❌ Cons: Requires __init__.py, can be confusing
from ..utils.validators import validate_email
from .auth import authenticate
from ..models.user import User

# Recommendation: Use absolute imports unless team uses relative
```

**Check existing Python files:**
```bash
# See what pattern the codebase uses
head -10 src/**/*.py | grep "^import\|^from"

# If you see mostly "from myapp.*", use absolute
# If you see mostly "from ..*", ensure __init__.py exists
```

### JavaScript/TypeScript Import Best Practices

**Problem: Inconsistent import paths**

```javascript
// Check for path aliases in tsconfig.json or jsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@utils/*": ["src/utils/*"]
    }
  }
}

// ❌ Bad: Relative paths when aliases exist
import { Button } from '../../../components/ui/Button';
import { formatDate } from '../../../../utils/date';

// ✅ Good: Use aliases
import { Button } from '@/components/ui/Button';
import { formatDate } from '@/utils/date';

// Or with specific aliases
import { Button } from '@components/ui/Button';
import { formatDate } from '@utils/date';
```

**Check existing files:**
```bash
# See import patterns in existing files
grep -h "^import" src/**/*.tsx | head -20

# Common patterns:
# 1. @/* for everything: import { X } from '@/...'
# 2. Specific aliases: import { X } from '@components/...'
# 3. Relative only: import { X } from '../...'

# Match whatever pattern you see most
```

**Import ordering:**
```javascript
// Check existing files for order preference
// Common pattern (React projects):

// 1. External libraries
import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import clsx from 'clsx';

// 2. Internal components
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

// 3. Hooks
import { useAuth } from '@/hooks/useAuth';

// 4. Utils
import { formatDate } from '@/utils/date';
import { cn } from '@/utils/classnames';

// 5. Types
import type { User } from '@/types/user';

// 6. Styles
import styles from './Component.module.css';

// Follow whatever order exists in the codebase
```

## Avoiding Duplication

### Search Before Creating

**Checklist before writing a new function:**

```bash
# 1. Search by functionality name
grep -r "validate" src/

# 2. Search by similar patterns
grep -r "email.*valid" src/

# 3. Check common utility locations
ls src/utils/
ls src/helpers/
ls src/lib/

# 4. Check tests (shows what exists)
ls src/**/*.test.{js,ts}
grep -r "validate" src/**/*.test.js

# 5. Search imports in similar files
# If others are validating emails, where do they import from?
grep -r "import.*valid" src/
```

**Example: Discovering existing validation**

```javascript
// You need to validate an email
// DON'T immediately write:
function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// FIRST search:
// $ grep -r "validateEmail\|isValidEmail\|emailValid" src/

// Found: src/utils/validators.ts
// ✅ Use existing
import { validateEmail } from '@/utils/validators';

// If NOT found, then create it in the right place
// Check where other validators live
// $ ls src/utils/
// validators.ts exists!

// Add to existing file instead of creating new one
// src/utils/validators.ts
export function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
```

### Consolidating Duplicates

**When you find duplicated logic:**

```javascript
// Found 3 places with similar code
// File: src/api/users.js
async function fetchUserData(id) {
  const token = localStorage.getItem('token');
  const response = await fetch(`/api/users/${id}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.json();
}

// File: src/api/orders.js
async function fetchOrderData(id) {
  const token = localStorage.getItem('token');
  const response = await fetch(`/api/orders/${id}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.json();
}

// File: src/api/products.js
async function fetchProductData(id) {
  const token = localStorage.getItem('token');
  const response = await fetch(`/api/products/${id}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.json();
}

// ✅ Good: Extract shared logic
// File: src/api/client.js
export async function apiRequest(endpoint) {
  const token = localStorage.getItem('token');
  const response = await fetch(endpoint, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.json();
}

// File: src/api/users.js
import { apiRequest } from './client';
export const fetchUserData = (id) => apiRequest(`/api/users/${id}`);

// File: src/api/orders.js
import { apiRequest } from './client';
export const fetchOrderData = (id) => apiRequest(`/api/orders/${id}`);

// File: src/api/products.js
import { apiRequest } from './client';
export const fetchProductData = (id) => apiRequest(`/api/products/${id}`);
```

## File Organization

### Understand Before Adding

```bash
# Before creating a new file, understand the structure
tree src/ -L 2

# Typical React structure:
src/
├── components/     # UI components
├── hooks/          # Custom React hooks
├── utils/          # Pure utility functions
├── api/            # API calls
├── services/       # Business logic
├── types/          # TypeScript types
├── constants/      # Constants
└── styles/         # Global styles

# Where should your code go?
# - Reusable UI? → components/
# - React-specific logic? → hooks/
# - Pure function? → utils/
# - API call? → api/
# - Business logic? → services/

# Check existing files for examples
ls src/utils/      # See what "utils" means here
ls src/services/   # See what "services" means here
```

**Example: Where to put validation?**

```javascript
// Check existing structure
// $ ls src/utils/
// validators.ts  formatters.ts  helpers.ts

// ✅ Good: Add to existing validators.ts
// src/utils/validators.ts
export function validateEmail(email) { /* ... */ }
export function validatePassword(password) { /* ... */ }
export function validatePhoneNumber(phone) { /* ... */ } // Add here

// ❌ Bad: Create new file for one function
// src/utils/phoneValidation.ts
export function validatePhoneNumber(phone) { /* ... */ }
```

### Component Organization

```typescript
// Check how existing components are organized
// Option 1: Single file
// src/components/Button.tsx
export function Button() { /* ... */ }

// Option 2: Folder with index
// src/components/Button/index.tsx
export { Button } from './Button';

// Option 3: Folder with multiple files
// src/components/Button/
//   Button.tsx
//   Button.styles.ts
//   Button.test.tsx
//   index.ts

// ✅ Match whatever pattern exists
// If most components are single files, use single file
// If most components are folders, use folder

// Don't mix patterns unnecessarily
```

## Naming Conventions

### Discover Naming Patterns

```bash
# Check file naming
ls src/components/
# UserCard.tsx, ProductList.tsx → PascalCase
# user-card.tsx, product-list.tsx → kebab-case

# Check function naming
grep -h "^function\|^const.*=.*function\|^export function" src/**/*.js
# function getUserData() → camelCase
# function get_user_data() → snake_case

# Check variable naming
grep -h "^const\|^let\|^var" src/**/*.js
# const userId → camelCase
# const user_id → snake_case

# Match what you see
```

**Common Patterns:**

```javascript
// JavaScript/TypeScript (typical)
// Files: PascalCase for components, camelCase for utilities
// UserCard.tsx, Button.tsx
// utils.ts, validators.ts

// Functions: camelCase
function getUserData() {}
const fetchOrders = () => {};

// Classes: PascalCase
class UserService {}

// Constants: UPPER_SNAKE_CASE
const API_BASE_URL = 'https://api.example.com';
const MAX_RETRY_COUNT = 3;

// Types/Interfaces: PascalCase
interface UserData {}
type OrderStatus = 'pending' | 'completed';

// Python (typical)
# Files: snake_case
# user_service.py, validators.py

# Functions: snake_case
def get_user_data():
    pass

# Classes: PascalCase
class UserService:
    pass

# Constants: UPPER_SNAKE_CASE
API_BASE_URL = "https://api.example.com"
MAX_RETRY_COUNT = 3
```

### Boolean Naming

```javascript
// Check existing boolean names
// Common prefixes: is, has, should, can, will

// ✅ Good
const isLoggedIn = true;
const hasPermission = false;
const shouldUpdate = true;
const canEdit = false;
const willRetry = true;

// ❌ Bad (not descriptive)
const loggedIn = true;
const permission = false;
const update = true;

// Match what exists in the codebase
grep -r "const is\|const has\|const should" src/
```

## Code Style Consistency

### Formatting

```javascript
// Check if project has formatter config
ls .prettierrc .prettierrc.json .prettierrc.js
ls .eslintrc .eslintrc.json .eslintrc.js

// If yes, run formatter before committing
npm run format
# or
yarn format
# or
npx prettier --write .

// Match existing style:
// - Semicolons or no semicolons?
// - Single quotes or double quotes?
// - Trailing commas or not?
// - Tab or spaces (2 or 4)?

// Look at 5 random files to see the pattern
```

### Comments

```javascript
// Check existing comment style
// JSDoc style:
/**
 * Fetches user data by ID
 * @param {string} id - User ID
 * @returns {Promise<User>} User object
 */
function getUserData(id) {}

// Simple comments:
// Fetch user data from API
function getUserData(id) {}

// No comments:
function getUserData(id) {}

// ✅ Match what exists
// If codebase has JSDoc, use JSDoc
// If minimal comments, keep it minimal
// If self-documenting code, don't over-comment
```

### Error Handling Style

```javascript
// Pattern 1: Try-catch everywhere
try {
  const data = await fetchData();
  return processData(data);
} catch (error) {
  handleError(error);
  throw error;
}

// Pattern 2: Let errors bubble
const data = await fetchData(); // Caller handles errors
return processData(data);

// Pattern 3: Error returns
const [error, data] = await fetchData();
if (error) return handleError(error);
return processData(data);

// ✅ Match existing pattern
// Check 5 similar functions to see the pattern
grep -A 5 "async function" src/**/*.js | grep -A 3 "try"
```

## Common Pitfalls

### Pitfall 1: Ignoring Existing Utilities

```javascript
// ❌ Bad: Reimplementing what exists
function debounce(fn, delay) {
  // ... custom implementation
}

// Check first:
// $ grep -r "debounce" src/
// Found: src/utils/timing.ts already has debounce

// ✅ Good: Use existing
import { debounce } from '@/utils/timing';
```

### Pitfall 2: Inconsistent Patterns

```javascript
// Existing API calls in codebase:
// File: api/users.js
export const getUser = (id) => apiRequest(`/users/${id}`);
export const createUser = (data) => apiRequest('/users', { method: 'POST', body: data });

// ❌ Bad: Different pattern
export async function fetchOrder(id) {
  const response = await fetch(`/api/orders/${id}`);
  return response.json();
}

// ✅ Good: Match existing pattern
export const getOrder = (id) => apiRequest(`/orders/${id}`);
export const createOrder = (data) => apiRequest('/orders', { method: 'POST', body: data });
```

### Pitfall 3: Over-Engineering

```javascript
// Request: "Add a button to export CSV"

// ❌ Bad: Over-engineered
// Created files:
// components/ExportButton/index.tsx
// components/ExportButton/ExportButton.tsx
// components/ExportButton/ExportButton.styles.ts
// components/ExportButton/ExportButton.test.tsx
// components/ExportButton/types.ts
// hooks/useExport.ts
// utils/exportStrategies/csv.ts
// utils/exportStrategies/json.ts
// utils/exportStrategies/xml.ts

// ✅ Good: Match complexity to need
// components/ExportButton.tsx
export function ExportButton({ data }) {
  const handleExport = () => {
    const csv = convertToCSV(data);
    downloadFile(csv, 'export.csv');
  };
  
  return <button onClick={handleExport}>Export CSV</button>;
}
```

### Pitfall 4: Not Checking for Breaking Changes

```javascript
// Modifying existing function
// Before:
export function formatDate(date) {
  return date.toLocaleDateString();
}

// ❌ Bad: Changing return type breaks callers
export function formatDate(date) {
  return {
    short: date.toLocaleDateString(),
    long: date.toLocaleString(),
    iso: date.toISOString()
  };
}

// ✅ Good Option 1: Add new function
export function formatDate(date) {
  return date.toLocaleDateString();
}

export function formatDateExtended(date) {
  return {
    short: date.toLocaleDateString(),
    long: date.toLocaleString(),
    iso: date.toISOString()
  };
}

// ✅ Good Option 2: Maintain backward compatibility
export function formatDate(date, extended = false) {
  if (extended) {
    return {
      short: date.toLocaleDateString(),
      long: date.toLocaleString(),
      iso: date.toISOString()
    };
  }
  return date.toLocaleDateString();
}
```

### Pitfall 5: Mixing Concerns

```javascript
// ❌ Bad: Component doing too much
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    // API call in component
    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(setUser);
  }, [userId]);
  
  // Business logic in component
  const calculateAge = (birthDate) => {
    return new Date().getFullYear() - new Date(birthDate).getFullYear();
  };
  
  return (
    <div>
      <h1>{user?.name}</h1>
      <p>Age: {calculateAge(user?.birthDate)}</p>
    </div>
  );
}

// ✅ Good: Separation of concerns
// api/users.js
export const getUser = (id) => apiRequest(`/users/${id}`);

// utils/date.js
export const calculateAge = (birthDate) => {
  return new Date().getFullYear() - new Date(birthDate).getFullYear();
};

// hooks/useUser.js
export function useUser(userId) {
  return useQuery(['user', userId], () => getUser(userId));
}

// components/UserProfile.tsx
function UserProfile({ userId }) {
  const { data: user } = useUser(userId);
  
  return (
    <div>
      <h1>{user?.name}</h1>
      <p>Age: {calculateAge(user?.birthDate)}</p>
    </div>
  );
}

// Match the separation level that exists in the codebase
```

## Integration Checklist

Before submitting code, verify:

### ✅ Discovery
- [ ] Searched for existing similar functionality
- [ ] Checked common utility locations
- [ ] Reviewed existing implementations
- [ ] Found and followed established patterns

### ✅ Imports
- [ ] Using same import style as existing files
- [ ] Using path aliases if they exist (check tsconfig.json)
- [ ] Imports ordered consistently
- [ ] No relative imports where absolute are used

### ✅ Naming
- [ ] File names match existing convention
- [ ] Function names match existing convention
- [ ] Variable names match existing convention
- [ ] Boolean names use is/has/should/can/will

### ✅ Organization
- [ ] File in correct directory
- [ ] No duplicate functionality
- [ ] Appropriate level of abstraction
- [ ] Follows existing component structure

### ✅ Style
- [ ] Ran formatter (prettier/eslint)
- [ ] Consistent with existing code style
- [ ] Comments match existing style
- [ ] Error handling matches existing pattern

### ✅ Integration
- [ ] Works with existing code
- [ ] No breaking changes to existing APIs
- [ ] Backward compatible if modifying existing code
- [ ] Tests pass (if tests exist)

## Language-Specific Guides

### Python Best Practices

```python
# 1. Imports: Use absolute imports
from myapp.utils.validators import validate_email
# Not: from ..utils.validators import validate_email

# 2. Ensure __init__.py exists if using relative imports
myapp/
  __init__.py
  utils/
    __init__.py

# 3. Type hints (if used in codebase)
def get_user(user_id: int) -> dict:
    return {"id": user_id}

# 4. Docstrings (match existing style)
def get_user(user_id: int) -> dict:
    """
    Fetch user data by ID.
    
    Args:
        user_id: The ID of the user to fetch
        
    Returns:
        Dictionary containing user data
    """
    return {"id": user_id}

# 5. Check for existing utilities
# Black, isort, pylint configurations
ls .black .isort.cfg pylintrc pyproject.toml

# Run formatters
black .
isort .
```

### JavaScript/TypeScript Best Practices

```typescript
// 1. Check for path aliases (tsconfig.json)
import { Button } from '@/components/Button';
// Not: import { Button } from '../../../components/Button';

// 2. Type everything in TypeScript
interface User {
  id: string;
  name: string;
}

function getUser(id: string): Promise<User> {
  // ...
}

// 3. Use existing hooks/utilities
// Check: hooks/, utils/, lib/ directories

// 4. Follow component patterns
// Check if using function components or class components
// Check if using FC type or not
// Check props destructuring style

// 5. Run linter/formatter
npm run lint
npm run format
```

## Working with Legacy Code

### The Campground Rule

**"Leave the code better than you found it"**

```javascript
// Found legacy code:
function fetchUserData(id) {
  // No error handling
  var data = fetch('/api/users/' + id).then(r => r.json())
  return data
}

// ✅ Good: Minimal improvement
async function fetchUserData(id) {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) throw new Error('Failed to fetch');
    return await response.json();
  } catch (error) {
    console.error('Error fetching user:', error);
    throw error;
  }
}

// ❌ Bad: Complete rewrite (risky)
// Don't completely rewrite unless that's the task
```

### Safe Modifications

```javascript
// When touching legacy code:

// 1. Add tests first (if none exist)
describe('fetchUserData', () => {
  it('should fetch user by id', async () => {
    // Test existing behavior first
  });
});

// 2. Make smallest change possible
// Change only what's needed for your feature

// 3. Don't "fix" unrelated issues
// Create separate ticket for other improvements

// 4. Document your changes
// Add comments explaining why, not what
```

## Integration with Other Skills

**Combines well with:**
- **debugging-methodology** - Finding where patterns are established
- **critical-thinking** - Deciding when to match vs improve patterns
- **api-design** - Implementing APIs consistently
- **error-handling** - Following error handling patterns
- **circular-dependency-resolver** - Understanding import structures

**When both active:**
Use critical-thinking to decide if pattern should be followed or improved, then use implementation-best-practices for tactical execution.