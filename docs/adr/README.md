# Architecture Decision Records (ADR)

This directory contains Architecture Decision Records (ADRs) following the [MADR format](https://adr.github.io/madr/).

## What is an ADR?

An Architecture Decision Record (ADR) is a document that captures an important architectural decision made along with its context and consequences.

## ADR Index

| Number | Title | Status | Date |
|--------|-------|--------|------|
| [0001](0001-depend-on-optimizer-framework.md) | Depend on MCP Optimizer Framework | Accepted | 2024-11-20 |
| [0002](0002-sentry-api-wrapper-pattern.md) | Use Direct API Wrapper Pattern | Accepted | 2024-11-21 |

## ADR Process

### When to Write an ADR

Write an ADR when you make a significant architectural decision that:
- Affects system structure or design
- Has long-term implications
- Involves trade-offs between alternatives
- Needs to be communicated to the team
- Should be remembered and understood later

### ADR Template

Use the [MADR template](https://adr.github.io/madr/):

```markdown
# [Number]. [Title]

Date: YYYY-MM-DD

## Status

[Proposed | Accepted | Deprecated | Superseded]

## Context

What is the issue we're trying to solve?

## Decision

What did we decide to do?

## Consequences

What are the trade-offs and implications?

### Positive
- Benefit 1
- Benefit 2

### Negative
- Drawback 1
- Drawback 2

### Neutral
- Consideration 1
- Consideration 2
```

### Creating a New ADR

1. Copy the template above
2. Assign next sequential number
3. Write clear, concise title
4. Fill in all sections
5. Discuss with team
6. Update status to "Accepted" when finalized
7. Add to index above

## ADR Statuses

- **Proposed**: Decision is being considered
- **Accepted**: Decision has been made and implemented
- **Deprecated**: Decision no longer applies but kept for historical context
- **Superseded**: Replaced by a newer ADR (link to replacement)

## Further Reading

- [Architecture Decision Records](https://adr.github.io/)
- [MADR Format](https://adr.github.io/madr/)
- [When to Write an ADR](https://github.com/joelparkerhenderson/architecture-decision-record#when-should-we-write-an-adr)
