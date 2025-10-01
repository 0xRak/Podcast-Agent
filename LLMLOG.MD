# LLM Change Log

## 2025-10-01
- Decision: Do NOT integrate Anthropic Agent SDK now; overhead not justified for current needs.
- Rationale: Current pipeline works; agent adds complexity, cost, and testing burden. Value mainly for richer automation and resilience we don't urgently need.
- Action: Park as Phase 2 pilot (scoped to replacing `ClaudeAnalyzer` JSON extraction only) once we need more automation/retries.
- Review Triggers: (a) weekly batch failures/retries rise; (b) need unified extract→analyze→summarize orchestration; (c) desire for structured tool traces/observability.
- Next Checkpoint: Re-evaluate after next 2 weekly runs or upon first retry incident rate >5%.

### Roadmap Update
- Added "Phase 2.5: Agent SDK Automation Pilot" to `ROADMAP.md` with scope, success criteria, and triggers.
