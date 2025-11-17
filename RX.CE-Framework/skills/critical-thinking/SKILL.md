---
name: critical-thinking
description: Enhances decision-making quality across all tasks through structured analysis, assumption testing, and bias detection. Use when making important decisions, evaluating options, planning approaches, or when reasoning needs to be more rigorous and well-considered.
---

# Critical Thinking

Systematic framework for enhancing decision quality through structured reasoning, assumption testing, and cognitive bias detection.

## When to Use

Apply this skill for:
- **Important decisions** with significant impact
- **Complex problems** with multiple variables
- **Strategic planning** and approach design
- **Trade-off analysis** between options
- **Risk assessment** and mitigation
- **Evaluating claims** or proposed solutions
- **Challenging assumptions** in existing plans
- **Detecting reasoning flaws** in arguments

## Core Principles

1. **Question Assumptions** - Make implicit beliefs explicit and test them
2. **Seek Disconfirming Evidence** - Actively look for reasons you might be wrong
3. **Consider Alternatives** - Generate multiple options before deciding
4. **Examine Trade-offs** - No solution is perfect; understand the costs
5. **Think Long-term** - Consider second and third-order effects
6. **Acknowledge Uncertainty** - Be honest about what you don't know

## Critical Thinking Framework

### Stage 1: Problem Definition (Clarity)

**Before solving, ensure you understand the real problem.**

Questions to ask:
- What problem are we actually trying to solve?
- Is this the root problem or just a symptom?
- Who defines this as a problem and why?
- What would "solved" look like?
- What constraints are real vs. self-imposed?

**Five Whys Technique:**
```
Problem: The build is failing
Why? → Tests are timing out
Why? → Database queries are slow
Why? → Missing indexes
Why? → Schema evolved but indexes weren't updated
Why? → No process for index maintenance
Real Problem: Missing database change management process
```

**Reframe the problem:**
- Original: "How do we make the dashboard load faster?"
- Reframed: "How do we give users the information they need more effectively?"
  (Maybe they don't need the dashboard at all - maybe alerts would be better)

### Stage 2: Assumption Identification (Awareness)

**List all assumptions, then test them.**

Types of assumptions:
1. **Factual assumptions** - "X is true"
2. **Value assumptions** - "Y is important"
3. **Causal assumptions** - "A causes B"
4. **Constraint assumptions** - "We can't do Z"

**Assumption Testing Template:**
```
ASSUMPTION: [State it clearly]
TYPE: [Factual/Value/Causal/Constraint]
EVIDENCE FOR: [What supports this?]
EVIDENCE AGAINST: [What contradicts this?]
TEST: [How could we verify?]
RISK IF WRONG: [What happens if this is false?]
VERDICT: [Strong/Moderate/Weak/Invalid]
```

**Common Hidden Assumptions:**
- "Users want more features" (Maybe they want simpler, not more)
- "Faster is always better" (Maybe consistency matters more)
- "This worked before, so it will work again" (Context may have changed)
- "Everyone understands what I mean" (Jargon and context differ)
- "We don't have time to do it properly" (Rush now = fix later = more time total)

### Stage 3: Alternative Generation (Options)

**Generate multiple approaches before committing to one.**

**Brainstorming Rules:**
1. Quantity over quality initially
2. No criticism during generation
3. Build on others' ideas
4. Encourage wild ideas
5. Combine and improve ideas

**Forced Alternative Techniques:**

**Inversion:** What if we did the opposite?
- Problem: "How do we add this feature?"
- Inversion: "How do we remove features?" 
- Insight: Maybe simplification is better than addition

**Constraints Removal:** What if [constraint] didn't exist?
- "What if we had unlimited time?"
- "What if cost didn't matter?"
- "What if we had no existing codebase?"
- Then ask: Can we approximate any of these scenarios?

**Perspective Shift:** How would [someone else] approach this?
- How would Amazon solve this?
- How would a startup solve this?
- How would this work in [different industry]?
- What would a security expert prioritize?

**Minimum Requirement:**
Generate at least 3 distinctly different approaches before evaluating any of them.

### Stage 4: Trade-off Analysis (Reality)

**Every decision involves trade-offs. Make them explicit.**

**Trade-off Matrix Template:**

| Criteria | Weight | Option A | Option B | Option C |
|----------|--------|----------|----------|----------|
| Speed to market | 20% | 8 | 4 | 6 |
| Maintainability | 30% | 5 | 9 | 7 |
| Cost | 15% | 6 | 7 | 9 |
| Risk | 20% | 7 | 8 | 5 |
| User experience | 15% | 9 | 6 | 8 |
| **Weighted Score** | | 6.85 | 7.15 | 6.80 |

**Key Questions:**
- What are we optimizing for?
- What are we willing to sacrifice?
- What's the "cost" of each benefit?
- Are there deal-breakers that override scores?

**Common Trade-offs:**
- Speed vs. Quality
- Flexibility vs. Simplicity
- Power vs. Usability
- Innovation vs. Stability
- Short-term vs. Long-term
- Cost vs. Performance

**Warning Signs of Poor Trade-off Analysis:**
- "We can have it all" (No, you can't)
- "There's no downside" (There always is)
- "This is obviously better" (Nothing is obvious)

### Stage 5: Second-Order Thinking (Consequences)

**Think beyond immediate effects to downstream consequences.**

**First-order thinking:** "This solution fixes the problem."
**Second-order thinking:** "This solution fixes the problem, which means..., which leads to..., which eventually..."

**Example:**
```
Decision: Add caching to improve performance

First-order: Pages load faster ✓
Second-order: 
  → Cache invalidation becomes critical
  → Stale data issues emerge
  → Debugging becomes harder (is it cache or real issue?)
  → Cache warming needed on deployment
  → Memory usage increases
  → New failure mode introduced
  
Is it still worth it? Maybe yes, maybe no - but now we know what we're signing up for.
```

**Questions for Second-Order Thinking:**
- And then what?
- What does this enable/prevent next?
- What new problems does this solution create?
- How will people respond to this change?
- What happens when this scales 10x?
- What are the unintended consequences?

**Time Horizons:**
- Immediate (today)
- Short-term (weeks)
- Medium-term (months)
- Long-term (years)

Consider effects at each horizon.

### Stage 6: Bias Detection (Awareness)

**Common cognitive biases that distort decision-making:**

#### Confirmation Bias
**What:** Seeking information that confirms existing beliefs
**Antidote:** Actively seek disconfirming evidence. Ask "What would prove me wrong?"

#### Anchoring Bias  
**What:** Over-relying on first piece of information
**Antidote:** Consider multiple starting points. Ask "What if we started from scratch?"

#### Sunk Cost Fallacy
**What:** Continuing because of past investment
**Antidote:** Focus on future value only. Ask "If starting today, would we choose this?"

#### Availability Bias
**What:** Overweighting easily recalled examples
**Antidote:** Look at data, not anecdotes. Ask "Is this representative?"

#### Groupthink
**What:** Conforming to group consensus
**Antidote:** Assign a devil's advocate. Encourage dissent.

#### Optimism Bias
**What:** Underestimating time/difficulty
**Antidote:** Reference class forecasting. Ask "How long did similar projects take?"

#### Planning Fallacy
**What:** Assuming things will go as planned
**Antidote:** Pre-mortem analysis. Ask "Why might this fail?"

**Bias Check Questions:**
- Am I only seeing what I want to see?
- Am I being influenced by recent events?
- Am I too attached to this idea?
- Am I underestimating the difficulty?
- Am I conforming to group opinion?
- What would an outsider see that I'm missing?

### Stage 7: Pre-Mortem Analysis (Risk)

**Imagine the decision has failed. Work backward to understand why.**

**Pre-Mortem Process:**

1. **Set the scene:** "It's [timeframe] from now. Our approach has completely failed."

2. **Generate failure reasons:** Everyone writes down why it failed (no discussion yet)

3. **Categorize failures:**
   - Technical failures
   - Organizational failures
   - External factors
   - Assumption failures
   - Execution failures

4. **Assess likelihood:** Which failure modes are most plausible?

5. **Design mitigations:** How can we prevent or detect each failure early?

**Example:**
```
Decision: Migrate to microservices

Pre-Mortem: "It's 18 months later. The migration has been a disaster."

Why it failed:
- Services are too fine-grained, overwhelming complexity
- Network latency between services kills performance
- Distributed debugging is nightmare
- Team lacks expertise in distributed systems
- Data consistency issues between services
- Deployment orchestration too complex
- Costs exploded due to service overhead

Mitigations:
- Start with 3-5 services, not 50
- Measure latency before committing
- Invest in observability infrastructure first
- Train team or hire expertise early
- Design for eventual consistency from start
- Use managed orchestration (K8s as service)
- Model cost before building
```

### Stage 8: Decision Documentation (Accountability)

**Record decisions to enable learning and accountability.**

**Decision Log Template:**
```markdown
# Decision: [Title]

**Date:** YYYY-MM-DD
**Context:** [What situation prompted this decision?]
**Decision:** [What did we decide?]
**Rationale:** [Why did we choose this?]

## Options Considered
1. Option A: [Brief description] - Rejected because [reason]
2. Option B: [Brief description] - Rejected because [reason]  
3. Option C: [Brief description] - **SELECTED**

## Key Assumptions
- Assumption 1: [What we're assuming is true]
- Assumption 2: [What we're assuming is true]
- If these prove false, we should reconsider

## Trade-offs Accepted
- We're optimizing for [X] at the expense of [Y]
- We're accepting [risk] because [reason]

## Success Criteria
- [How we'll know this was right in 3 months]
- [How we'll know this was right in 6 months]
- [How we'll know this was right in 12 months]

## Monitoring & Review
- Review date: [When to check if this is working]
- Kill criteria: [What would make us reverse this decision?]

## Dissenting Opinions
- [Name] believes [X] because [Y]
- This view was considered but [reason for not choosing it]
```

## Critical Thinking Checklist

Before finalizing any important decision:

### Problem Definition
- [ ] Have we clearly stated the problem?
- [ ] Have we distinguished symptoms from root causes?
- [ ] Have we considered reframing the problem?

### Assumptions
- [ ] Have we listed our key assumptions?
- [ ] Have we tested our assumptions?
- [ ] Have we identified which assumptions are critical?

### Alternatives
- [ ] Have we generated at least 3 different approaches?
- [ ] Have we considered doing nothing?
- [ ] Have we tried inverting the problem?

### Trade-offs
- [ ] Have we made trade-offs explicit?
- [ ] Have we weighted different criteria?
- [ ] Are we clear on what we're sacrificing?

### Consequences
- [ ] Have we thought through second-order effects?
- [ ] Have we considered different time horizons?
- [ ] Have we identified new problems this creates?

### Biases
- [ ] Have we sought disconfirming evidence?
- [ ] Are we too anchored on one idea?
- [ ] Are we falling for sunk cost fallacy?

### Risks
- [ ] Have we done a pre-mortem?
- [ ] Have we identified failure modes?
- [ ] Have we designed mitigations?

### Documentation
- [ ] Have we recorded the decision?
- [ ] Have we noted dissenting views?
- [ ] Have we set review criteria?

## Example Applications

### Example 1: Technology Choice

**Poor Decision Process:**
"Let's use React because it's popular and I know it."

**Critical Thinking Applied:**

**Problem Definition:**
- Root problem: Need interactive UI with real-time updates
- Reframe: What capabilities do we need, not what technology?

**Assumptions:**
- Assumption: "React is industry standard" 
- Test: Is it standard for our specific use case (small team, internal tool)?
- Verdict: Weak - React is common but maybe overkill for internal tool

**Alternatives:**
1. React - Full framework, large ecosystem
2. Vue - Simpler, gentler learning curve  
3. Vanilla JS + Alpine - Minimal, fast
4. Server-side with HTMX - No heavy client framework

**Trade-offs:**
- React: Power + Ecosystem vs. Complexity + Bundle Size
- HTMX: Simplicity + Speed vs. Limited interactivity
- Choosing: Vue (balanced for team skill level and requirements)

**Second-Order:**
- Vue choice means smaller ecosystem, but team learns faster
- Less battle-tested than React, but lower maintenance burden
- Hiring might be slightly harder, but retention easier (less overwhelming)

**Decision:** Vue, with clear documentation of reasoning

### Example 2: Feature Prioritization

**Poor Decision Process:**
"Customer asked for it, so we should build it."

**Critical Thinking Applied:**

**Problem Definition:**
- Stated: Customer wants feature X
- Root: What problem are they trying to solve?
- Reframe: Can we solve their problem without feature X?

**Assumptions:**
- Assumption: "Customer knows what they need"
- Test: Do they have expertise in UX? Have they tried alternatives?
- Verdict: Moderate - They know their pain but maybe not best solution

**Alternatives:**
1. Build feature as requested
2. Build simpler version addressing core need
3. Point them to existing feature they're not using
4. Defer until more customers request it

**Trade-offs:**
- Build now: Happy customer vs. Complexity + Maintenance
- Defer: Focus on core vs. Risk losing customer
- Choosing: Build simple version (80% benefit, 20% complexity)

**Pre-Mortem:**
"Six months later, this feature is rarely used."
- Why? Because it didn't actually solve their workflow problem
- Mitigation: Build prototype first, validate with multiple customers

**Decision:** Build prototype, validate with 3 customers, then decide

### Example 3: Architectural Decision

**Poor Decision Process:**
"Microservices are modern, let's use them."

**Critical Thinking Applied:**

**Problem Definition:**
- Stated: Need to scale system
- Root: What specifically needs to scale? Traffic? Team? Features?
- Reframe: What's actually constraining us today?

**Assumptions:**
- Assumption: "Monolith can't scale"
- Test: Have we optimized current architecture? What's actual bottleneck?
- Verdict: Weak - Most monoliths can scale further than we think

**Alternatives:**
1. Full microservices
2. Modular monolith with clear boundaries
3. Monolith + extract high-load services only
4. Optimize current monolith first

**Trade-offs:**
- Microservices: Team independence vs. Operational complexity
- Monolith: Simplicity vs. Potential coordination bottlenecks
- Choosing: Modular monolith + extract critical services

**Second-Order:**
- Modular monolith enables later extraction if needed
- Team learns service boundaries before committing to distribution
- Can defer operational complexity until we need it

**Pre-Mortem:**
"Two years later, we're stuck in monolith hell."
- Why? Because we never enforced module boundaries
- Mitigation: Architectural tests to enforce boundaries, regular architecture reviews

**Decision:** Modular monolith with enforced boundaries, documented extraction paths

## Guidelines for Application

**When to go deep:**
- High-impact decisions (architectural, strategic)
- Irreversible decisions (hard to undo)
- Expensive decisions (time, money, opportunity cost)
- Decisions under uncertainty
- Controversial decisions (disagreement in team)

**When to go fast:**
- Low-impact decisions (easily reversed)
- Time-sensitive decisions (delay costs more than wrong choice)
- Well-understood domains (lots of precedent)
- Already have strong consensus

**Balancing speed and rigor:**
- Not every decision deserves 2 hours of analysis
- Use lightweight versions for smaller decisions
- Save full framework for important choices
- Build decision-making "muscle memory" over time

## Integration with Other Skills

**Combines well with:**
- **debugging-methodology** - Apply critical thinking to diagnose root causes
- **architecture-review** - Use framework to evaluate architecture decisions
- **refactoring-patterns** - Think critically about when/what to refactor
- **test-strategy** - Apply to test design and coverage decisions

**When multiple skills active:**
This skill enhances the reasoning within other skills. It doesn't replace domain expertise, it improves how you apply that expertise.

## Common Pitfalls

## Working with AI Coding Assistants - Common Pitfalls

### 1. Defensive Over-Engineering

**Problem:** When asked "did you check X/Y?", AI adds redundant validation checks, leading to bloated code with repetitive logic.

**Why it happens:**
- AI interprets question as "you probably missed this"
- Adds check without verifying if it exists
- Compounds with each clarification question

**Solution:**
```javascript
// ❌ Bad: After being asked "did you check if user exists?"
async function getUser(id) {
  if (!id) throw new Error('ID required');
  if (typeof id !== 'string') throw new Error('ID must be string');

  const user = await db.findUser(id);

  if (!user) throw new Error('User not found');
  if (!user.active) throw new Error('User not active');
  if (!user.verified) throw new Error('User not verified');
  // ... 10 more redundant checks

  return user;
}

// ✅ Good: Review existing checks first, add only what's missing
async function getUser(id) {
  if (!id) throw new Error('ID required');

  const user = await db.findUser(id);
  if (!user) throw new Error('User not found');

  return user;
}
```

**Best practices:**
- Before adding checks, search for existing validation
- Consolidate redundant checks into a single validator
- Ask yourself: "Is this check actually necessary?"
- Review the full function after adding checks

### 2. Ignoring Existing Functionality

**Problem:** AI recreates functionality that already exists in the codebase, often because it's not in the exact format expected.

**Why it happens:**
- Similar functionality named differently
- Existing code in different location
- Pattern doesn't match AI's expectation
- Incomplete codebase context

**Solution:**
```javascript
// ❌ Bad: Creating new validation when one exists
// Existing in utils/validators.js:
export function validateEmail(email) { /* ... */ }

// AI creates in users.js:
function checkEmailValid(email) {
  // Duplicate validation logic
}

// ✅ Good: Discover and use existing
import { validateEmail } from './utils/validators';

function createUser(email) {
  validateEmail(email); // Use existing
  // ...
}
```

**Best practices:**
- Search codebase for similar functionality first: `grep -r "validateEmail"`
- Check common utility locations: `utils/`, `helpers/`, `lib/`
- Ask: "Does functionality like this exist?"
- Review existing modules before creating new ones
- Read tests to see what's already available

### 3. Import Convention Violations

**Problem:** AI uses import style inconsistent with codebase conventions.

**Language-specific examples:**

**Python:**
```python
# ❌ Bad: Relative imports without __init__.py
from ..utils import helper  # Fails without __init__.py in each folder

# ✅ Good: Absolute imports
from app.utils import helper

# Or ensure __init__.py exists in every folder:
app/
  __init__.py
  utils/
    __init__.py
    helper.py
```

**JavaScript/TypeScript:**
```javascript
// ❌ Bad: Inconsistent with codebase using path aliases
import { helper } from '../../../utils/helper';

// ✅ Good: Match existing pattern
import { helper } from '@/utils/helper';
```

**Best practices:**
- Check 2-3 existing files for import patterns before writing code
- Look for path aliases in tsconfig.json/jsconfig.json
- For Python: verify __init__.py exists OR use absolute imports
- Match the convention, don't mix styles within a file or module

### 4. Knowledge Cutoff Issues

**Problem:** AI "corrects" dates to its knowledge cutoff (January 2025) or uses outdated information.

**Examples:**
```javascript
// AI might change:
const apiVersion = '2025-10-22';
// To:
const apiVersion = '2025-01-15'; // "Corrected to most recent"

// Or suggest outdated packages:
npm install react@17.0.0  // When 18.x is current
```

**Best practices:**
- Explicitly state current date in prompts: "Today is October 22, 2025"
- Verify version numbers independently using package registries
- Don't trust AI for "most recent" without verification
- Be explicit: "Use the exact date/version provided, don't update it"

### 5. Over-Eager Abstraction

**Problem:** AI creates abstractions and patterns that are overly complex for the use case.

**Example:**
```javascript
// ❌ Bad: Asked to add one button, AI creates entire design system
// components/Button/index.tsx
// components/Button/styles.tsx
// components/Button/types.tsx
// components/Button/Button.test.tsx
// components/Button/Button.stories.tsx
// hooks/useButton.ts
// contexts/ButtonContext.tsx

// ✅ Good: Match codebase complexity level
// components/Button.tsx  // Single file for now
```

**Best practices:**
- Match existing complexity level in the codebase
- Start simple, refactor when actually needed
- Don't create infrastructure for one use case
- Follow YAGNI (You Aren't Gonna Need It)

### 6. Context Drift in Long Sessions

**Problem:** AI forgets earlier context in long conversations, leading to inconsistencies.

**Example:**
```
[Early in conversation]
You: "Use PostgreSQL for the database"
AI: Creates PostgreSQL schema

[30 messages later]
AI: Suggests MongoDB query syntax
```

**Best practices:**
- Remind AI of key decisions periodically
- Keep critical info in system files (README, docs, config)
- For long sessions, start fresh with context summary
- Use persistent documentation over conversation memory

### 7. Cargo Cult Programming

**Problem:** AI includes boilerplate/patterns without understanding if they're needed.

**Example:**
```javascript
// ❌ Bad: Unnecessary patterns for simple case
class SimpleCache {
  constructor(
    private readonly logger: ILogger,
    private readonly metrics: IMetrics,
    private readonly config: IConfig
  ) {}

  // For a 10-line cache class that just stores key-value pairs
}

// ✅ Good: Simple when appropriate
class SimpleCache {
  private cache = new Map();

  get(key) { return this.cache.get(key); }
  set(key, val) { this.cache.set(key, val); }
}
```

**Best practices:**
- Question every abstraction: "Do we actually need this?"
- Remove unused parameters/interfaces
- Prefer simple over "enterprise patterns"
- Add complexity only when requirements demand it

## Prompting Strategies to Avoid These Pitfalls

**Instead of defensive prompting:**
❌ "Did you check if the user exists?"
✅ "Review the existing validation logic and identify any gaps"

**Instead of vague requests:**
❌ "Add error handling"
✅ "Add try-catch for network errors, follow the pattern in api/users.js"

**For codebase integration:**
✅ "First, search for existing authentication logic before creating new"
✅ "Follow the import pattern used in other files in this directory"
✅ "Match the error handling style in the existing codebase"

**For preventing duplication:**
✅ "Check if this functionality exists elsewhere in the codebase first"
✅ "Search for similar utilities in the utils/ directory"
✅ "Review existing API clients before creating a new one"

**For maintaining conventions:**
✅ "Use the same import style as the rest of the codebase"
✅ "Follow the naming conventions established in similar files"
✅ "Match the code organization pattern used in this directory"

## Meta: Critical Thinking About Critical Thinking

**Beware of:**
- **Analysis paralysis** - Overthinking to the point of inaction
- **Process worship** - Following steps without understanding why
- **False rigor** - Looking systematic without actually being systematic
- **Cynicism** - Rejecting everything under guise of "critical thinking"

**Remember:**
- Critical thinking is a tool, not a religion
- Sometimes "good enough" beats "perfect"
- Intuition + experience have value too
- The goal is better decisions, not more analysis

**This skill works best when:**
- Combined with domain expertise
- Applied proportionally to decision importance  
- Used to enhance, not replace, judgment
- Practiced regularly to build instinct