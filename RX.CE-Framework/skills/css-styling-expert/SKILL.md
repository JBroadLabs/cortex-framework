---
name: css-styling-expert
description: Expert CSS styling guidance covering modern layouts (Flexbox, Grid), responsive design, animations, performance, theming, and best practices. Use when designing layouts, styling components, creating responsive designs, debugging CSS issues, optimizing performance, or building design systems.
---

# CSS Styling Expert

Comprehensive framework for modern CSS development, from layouts to animations to performance optimization.

## When to Use

Apply this skill when:
- Designing page layouts (Flexbox, Grid)
- Styling components and interfaces
- Creating responsive designs
- Implementing animations and transitions
- Building design systems
- Debugging CSS issues (specificity, layout bugs)
- Optimizing CSS performance
- Choosing CSS methodologies (BEM, CSS Modules, Tailwind)
- Implementing theming (light/dark mode)

## Core Principles

### 1. Mobile-First, Progressive Enhancement
- Design for smallest screen first
- Add complexity for larger screens
- Ensure core functionality without CSS

### 2. Component-Thinking
- Build reusable, composable components
- Encapsulate styles
- Avoid global namespace pollution

### 3. Performance Matters
- Minimize repaints and reflows
- Optimize selectors
- Lazy-load non-critical CSS

### 4. Maintainability Over Cleverness
- Clear naming conventions
- Consistent patterns
- Self-documenting code

## Modern Layout Techniques

### Flexbox (One-Dimensional Layout)

**Best for:**
- Navigation bars
- Card layouts
- Centered content
- Evenly spaced items
- Vertical centering

**Basic patterns:**

```css
/* Horizontal center */
.container {
  display: flex;
  justify-content: center;
}

/* Vertical center */
.container {
  display: flex;
  align-items: center;
}

/* Center both directions */
.container {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Space between items */
.container {
  display: flex;
  justify-content: space-between;
}

/* Equal spacing around items */
.container {
  display: flex;
  gap: 1rem;  /* Modern approach, better than margins */
}

/* Vertical stack */
.container {
  display: flex;
  flex-direction: column;
}

/* Wrap items */
.container {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

/* Responsive flex item */
.item {
  flex: 1;  /* Grow and shrink, basis 0 */
  flex: 0 0 200px;  /* Don't grow/shrink, fixed 200px */
  flex: 1 1 200px;  /* Grow/shrink, base 200px */
}
```

**Common flexbox patterns:**

```css
/* Sticky footer */
body {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex: 1;  /* Fills available space */
}

/* Navigation with logo left, menu right */
nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Card with button at bottom */
.card {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.card-content {
  flex: 1;
}

.card-button {
  margin-top: auto;  /* Pushes to bottom */
}

/* Equal-height columns */
.columns {
  display: flex;
  gap: 2rem;
}

.column {
  flex: 1;
}
```

### CSS Grid (Two-Dimensional Layout)

**Best for:**
- Page layouts
- Complex grids
- Overlapping content
- Magazine-style layouts
- Dashboard layouts

**Basic patterns:**

```css
/* Simple grid */
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

/* Fixed + flexible columns */
.grid {
  display: grid;
  grid-template-columns: 250px 1fr;  /* Sidebar + main */
  gap: 2rem;
}

/* Responsive grid (auto-fit) */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

/* Named areas (semantic layout) */
.page {
  display: grid;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
  grid-template-columns: 250px 1fr;
  gap: 1rem;
}

.header { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main { grid-area: main; }
.footer { grid-area: footer; }

/* Spanning items */
.grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
}

.item-wide {
  grid-column: span 2;  /* Takes 2 columns */
}

.item-tall {
  grid-row: span 2;  /* Takes 2 rows */
}

/* Dense packing */
.grid {
  display: grid;
  grid-auto-flow: dense;  /* Fills gaps */
}
```

**Common grid patterns:**

```css
/* Holy Grail Layout */
.layout {
  display: grid;
  grid-template-areas:
    "header header header"
    "left main right"
    "footer footer footer";
  grid-template-columns: 200px 1fr 200px;
  grid-template-rows: auto 1fr auto;
  min-height: 100vh;
}

/* Dashboard with varied sizes */
.dashboard {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: 200px;
  gap: 1rem;
}

.widget-large {
  grid-column: span 2;
  grid-row: span 2;
}

/* Masonry-like (not true masonry) */
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  grid-auto-rows: 20px;
  gap: 1rem;
}

.gallery-item {
  grid-row: span var(--span);  /* Set dynamically */
}

/* Centered content with max-width */
.container {
  display: grid;
  grid-template-columns: 
    [full-start] minmax(1rem, 1fr)
    [content-start] minmax(0, 1200px) [content-end]
    minmax(1rem, 1fr) [full-end];
}

.content {
  grid-column: content;
}

.full-bleed {
  grid-column: full;
}
```

### Flexbox vs Grid Decision Matrix

| Use Case | Flexbox | Grid |
|----------|---------|------|
| One-dimensional layout | ✅ | ⚠️ Overkill |
| Two-dimensional layout | ⚠️ Complex | ✅ |
| Content-first sizing | ✅ | ⚠️ |
| Layout-first sizing | ⚠️ | ✅ |
| Dynamic wrapping | ✅ | ⚠️ |
| Overlapping elements | ❌ | ✅ |
| Alignment | ✅ | ✅ |

**Can use both:**
```css
/* Grid for page, Flexbox for navigation */
.page {
  display: grid;
  grid-template-columns: 250px 1fr;
}

.nav {
  display: flex;
  justify-content: space-between;
}
```

## Responsive Design

### Mobile-First Approach

```css
/* Base styles (mobile) */
.container {
  padding: 1rem;
  font-size: 16px;
}

/* Tablet and up */
@media (min-width: 768px) {
  .container {
    padding: 2rem;
    font-size: 18px;
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .container {
    padding: 3rem;
    max-width: 1200px;
    margin: 0 auto;
  }
}

/* Large desktop */
@media (min-width: 1440px) {
  .container {
    max-width: 1400px;
  }
}
```

### Common Breakpoints

```css
/* Mobile: < 640px (default) */

/* Tablet */
@media (min-width: 640px) { }

/* Laptop */
@media (min-width: 1024px) { }

/* Desktop */
@media (min-width: 1280px) { }

/* Large */
@media (min-width: 1536px) { }
```

### Container Queries (Modern)

```css
/* Style based on container size, not viewport */
.card-container {
  container-type: inline-size;
}

@container (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 1fr 2fr;
  }
}
```

### Responsive Typography

```css
/* Fluid typography */
.heading {
  font-size: clamp(1.5rem, 5vw, 3rem);
  /* min: 1.5rem, preferred: 5vw, max: 3rem */
}

/* Line length control */
.content {
  max-width: 65ch;  /* ~65 characters wide */
}
```

### Responsive Images

```css
/* Always responsive */
img {
  max-width: 100%;
  height: auto;
}

/* Aspect ratio (modern) */
img {
  aspect-ratio: 16 / 9;
  object-fit: cover;
}

/* Background images */
.hero {
  background-image: url('mobile.jpg');
}

@media (min-width: 768px) {
  .hero {
    background-image: url('desktop.jpg');
  }
}
```

## CSS Architecture & Methodologies

### BEM (Block Element Modifier)

```css
/* Block: Standalone component */
.card { }

/* Element: Part of block */
.card__header { }
.card__body { }
.card__footer { }

/* Modifier: Variation of block or element */
.card--featured { }
.card__header--large { }
```

**Example:**
```html
<div class="card card--featured">
  <header class="card__header card__header--large">Title</header>
  <div class="card__body">Content</div>
  <footer class="card__footer">Footer</footer>
</div>
```

```css
.card {
  border: 1px solid #ddd;
  border-radius: 8px;
}

.card--featured {
  border-color: #007bff;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.card__header {
  padding: 1rem;
  background: #f8f9fa;
}

.card__header--large {
  padding: 2rem;
  font-size: 1.5rem;
}
```

### CSS Modules (Scoped CSS)

```css
/* Button.module.css */
.button {
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

.primary {
  background: #007bff;
  color: white;
}

.secondary {
  background: #6c757d;
  color: white;
}
```

```javascript
import styles from './Button.module.css';

<button className={styles.button + ' ' + styles.primary}>
  Click me
</button>
```

### Utility-First (Tailwind-style)

```html
<!-- Inline utility classes -->
<div class="flex items-center justify-between p-4 bg-white rounded-lg shadow-md">
  <h2 class="text-xl font-bold text-gray-900">Title</h2>
  <button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
    Action
  </button>
</div>
```

**When to use each:**
- **BEM:** Traditional projects, clear component boundaries
- **CSS Modules:** React/Vue apps, automatic scoping
- **Utility-First:** Rapid prototyping, consistent design system

## Colors & Theming

### CSS Custom Properties (Variables)

```css
:root {
  /* Colors */
  --color-primary: #007bff;
  --color-secondary: #6c757d;
  --color-success: #28a745;
  --color-danger: #dc3545;
  
  /* Grays */
  --color-gray-50: #f8f9fa;
  --color-gray-100: #e9ecef;
  --color-gray-900: #212529;
  
  /* Spacing */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 2rem;
  --space-xl: 4rem;
  
  /* Typography */
  --font-family-sans: system-ui, -apple-system, sans-serif;
  --font-family-mono: 'Courier New', monospace;
  
  /* Sizes */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
  
  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-base: 300ms ease;
}

/* Usage */
.button {
  padding: var(--space-sm) var(--space-md);
  background: var(--color-primary);
  box-shadow: var(--shadow-md);
  transition: all var(--transition-base);
}
```

### Dark Mode

```css
:root {
  --bg-primary: white;
  --text-primary: #000;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #1a1a1a;
    --text-primary: #fff;
  }
}

/* Or manual toggle */
[data-theme="dark"] {
  --bg-primary: #1a1a1a;
  --text-primary: #fff;
}

body {
  background: var(--bg-primary);
  color: var(--text-primary);
}
```

### Color Schemes

```css
/* Semantic colors */
:root {
  --color-text: #1a1a1a;
  --color-text-light: #6c757d;
  --color-bg: white;
  --color-bg-secondary: #f8f9fa;
  --color-border: #dee2e6;
  
  --color-success: #28a745;
  --color-warning: #ffc107;
  --color-error: #dc3545;
  --color-info: #17a2b8;
}

/* Accessible contrast */
.button-primary {
  background: var(--color-primary);
  color: white;  /* Ensure 4.5:1 contrast ratio */
}
```

## Typography

### Font Stacks

```css
:root {
  /* System font stack (fastest) */
  --font-sans: system-ui, -apple-system, BlinkMacSystemFont, 
               'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 
               sans-serif;
  
  /* Serif */
  --font-serif: Georgia, Cambria, 'Times New Roman', serif;
  
  /* Monospace */
  --font-mono: 'SF Mono', Monaco, 'Cascadia Code', 'Courier New', monospace;
}

body {
  font-family: var(--font-sans);
}
```

### Type Scale

```css
:root {
  /* Modular scale (1.25 ratio) */
  --text-xs: 0.64rem;   /* 10.24px */
  --text-sm: 0.8rem;    /* 12.8px */
  --text-base: 1rem;    /* 16px */
  --text-lg: 1.25rem;   /* 20px */
  --text-xl: 1.563rem;  /* 25px */
  --text-2xl: 1.953rem; /* 31.25px */
  --text-3xl: 2.441rem; /* 39px */
  --text-4xl: 3.052rem; /* 48.83px */
}

h1 { font-size: var(--text-4xl); }
h2 { font-size: var(--text-3xl); }
h3 { font-size: var(--text-2xl); }
```

### Readability

```css
/* Optimal line length */
.content {
  max-width: 65ch;  /* ~65 characters */
}

/* Line height */
body {
  line-height: 1.5;  /* Body text */
}

h1, h2, h3 {
  line-height: 1.2;  /* Headings tighter */
}

/* Letter spacing */
.uppercase {
  text-transform: uppercase;
  letter-spacing: 0.05em;  /* Improve readability */
}
```

## Animations & Transitions

### Transitions (Hover Effects)

```css
.button {
  background: #007bff;
  transition: background 200ms ease;
}

.button:hover {
  background: #0056b3;
}

/* Multiple properties */
.card {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: 
    transform 200ms ease,
    box-shadow 200ms ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.15);
}

/* Transition all (use sparingly) */
.element {
  transition: all 300ms ease;
}
```

### Keyframe Animations

```css
/* Fade in */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.element {
  animation: fadeIn 300ms ease;
}

/* Slide in */
@keyframes slideIn {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Bounce */
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.button {
  animation: bounce 500ms ease infinite;
}

/* Spin (loading) */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spinner {
  animation: spin 1s linear infinite;
}
```

### Performance Best Practices

```css
/* ✅ Use transform and opacity (GPU-accelerated) */
.element {
  transform: translateX(100px);
  opacity: 0.5;
}

/* ❌ Avoid animating these (triggers layout) */
.element {
  width: 200px;  /* Causes reflow */
  left: 100px;   /* Causes reflow */
  margin: 20px;  /* Causes reflow */
}

/* Use will-change for complex animations */
.element {
  will-change: transform, opacity;
}

/* Remove after animation */
.element.animated {
  will-change: auto;
}
```

### Animation Patterns

```css
/* Stagger children */
.list-item {
  animation: fadeIn 300ms ease;
  animation-fill-mode: both;
}

.list-item:nth-child(1) { animation-delay: 0ms; }
.list-item:nth-child(2) { animation-delay: 100ms; }
.list-item:nth-child(3) { animation-delay: 200ms; }

/* Loading skeleton */
@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}

.skeleton {
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 1000px 100%;
  animation: shimmer 2s infinite;
}

/* Pulse (notification badge) */
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(255, 0, 0, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 0, 0, 0);
  }
}

.badge {
  animation: pulse 2s infinite;
}
```

## Common Component Patterns

### Buttons

```css
.button {
  /* Reset */
  border: none;
  background: none;
  font: inherit;
  cursor: pointer;
  
  /* Styles */
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  transition: all 200ms ease;
}

.button-primary {
  background: var(--color-primary);
  color: white;
}

.button-primary:hover {
  background: var(--color-primary-dark);
}

.button-primary:active {
  transform: scale(0.98);
}

.button-primary:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.button-secondary {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

### Cards

```css
.card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  overflow: hidden;
  transition: box-shadow 200ms ease;
}

.card:hover {
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.card-header {
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
  font-weight: 600;
}

.card-body {
  padding: 1rem;
}

.card-footer {
  padding: 1rem;
  background: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border);
}
```

### Forms

```css
.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
  color: var(--color-text);
}

.form-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font: inherit;
  transition: border-color 200ms ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.form-input:invalid {
  border-color: var(--color-error);
}

.form-error {
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: var(--color-error);
}
```

### Modals

```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 0.5rem;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px rgba(0,0,0,0.1);
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid var(--color-border);
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}
```

## CSS Debugging

### Common Issues

**Specificity problems:**
```css
/* ❌ Low specificity */
.button { color: blue; }

/* ✅ Increase specificity (avoid !important) */
.card .button { color: blue; }

/* ⚠️ Last resort */
.button { color: blue !important; }
```

**Box model issues:**
```css
/* ❌ Width + padding can overflow */
.box {
  width: 100%;
  padding: 1rem;
}

/* ✅ Use border-box */
* {
  box-sizing: border-box;
}

.box {
  width: 100%;
  padding: 1rem;  /* Padding included in width */
}
```

**Z-index stacking:**
```css
/* Create stacking context */
.parent {
  position: relative;
  z-index: 1;
}

.child {
  position: absolute;
  z-index: 999;  /* Only compares within parent context */
}
```

### Debugging Tools

```css
/* Visualize all elements */
* {
  outline: 1px solid red;
}

/* Check specificity */
/* Use browser DevTools: Inspect > Computed > Filter */

/* Identify layout issues */
body * {
  background: rgba(255,0,0,0.1);
}
```

## Performance Optimization

### Critical CSS

```html
<!-- Inline critical CSS -->
<style>
  /* Above-the-fold styles */
  body { margin: 0; font-family: sans-serif; }
  .header { background: #007bff; }
</style>

<!-- Load rest async -->
<link rel="stylesheet" href="styles.css" media="print" onload="this.media='all'">
```

### Minimize Reflows

```css
/* ❌ Triggers reflow for each property */
element.style.width = '100px';
element.style.height = '100px';
element.style.padding = '10px';

/* ✅ Batch changes */
element.style.cssText = 'width: 100px; height: 100px; padding: 10px;';

/* ✅ Or use classes */
element.classList.add('resized');
```

### Font Loading

```css
/* Control font loading */
@font-face {
  font-family: 'CustomFont';
  src: url('font.woff2') format('woff2');
  font-display: swap;  /* Show fallback immediately */
}
```

## Accessibility

### Focus Styles

```css
/* ❌ Never remove focus */
*:focus {
  outline: none;  /* Don't do this */
}

/* ✅ Style focus */
button:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

### Color Contrast

```css
/* Ensure 4.5:1 contrast ratio for normal text */
/* 3:1 for large text (18pt+ or 14pt+ bold) */

.text {
  color: #333;  /* vs white background = 12.6:1 ✅ */
}

.button {
  background: #007bff;
  color: white;  /* 4.5:1 ✅ */
}
```

### Screen Reader Only

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0,0,0,0);
  white-space: nowrap;
  border: 0;
}
```

## Best Practices Checklist

### Layout
- [ ] Used mobile-first approach?
- [ ] Chosen appropriate layout (Flexbox vs Grid)?
- [ ] Responsive at all breakpoints?
- [ ] Tested on real devices?

### Performance
- [ ] Minimized repaints/reflows?
- [ ] Used transform/opacity for animations?
- [ ] Optimized selectors?
- [ ] Lazy-loaded non-critical CSS?

### Maintainability
- [ ] Consistent naming convention?
- [ ] Used CSS variables for theme?
- [ ] Avoided !important (except utility classes)?
- [ ] Documented complex selectors?

### Accessibility
- [ ] Focus styles visible?
- [ ] Color contrast sufficient (4.5:1)?
- [ ] No information conveyed by color alone?
- [ ] Tested with keyboard navigation?

## Integration with Other Skills

**Combines well with:**
- **api-design** - Style API documentation/dashboards
- **critical-thinking** - Evaluate CSS architecture decisions
- **debugging-methodology** - Debug CSS issues systematically

**When both active:**
Use critical thinking for architecture decisions, then apply specific patterns from this skill.