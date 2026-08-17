# TCC Partner Intelligence Platform — POC Design Brief

**Owner scope:** LLM Agent design, Multi-Agent Orchestrator, Context Layer
**Client:** The Channel Company (TCC) — B2B partner intelligence chatbot for their technology-supplier customers
**Status:** POC scoping, pre-implementation

---

## 1. Project Context

TCC wants an AI chatbot that lets its customers ask natural-language questions about partner
growth, GTM strategy, market prioritization, and event optimization — answered by querying
across TCC's existing data estate: Snowflake, Salesforce, Omeda (CDP), and public/external
enrichment sources. MCP tool connectors for these sources are already built by another
workstream. This brief covers the orchestration and context layer that sits on top of them.

Reference architecture (already agreed, see `TCC-RFP-Arc-Draft_1.png`):
`Data Sources → MCP & Tools Gateway → Context Layer (Context / RAG-Vector Store / Semantic
Cache) → Multi-Agent Orchestrator → Frontier LLM Router → API/App Layer`

---

## 2. POC Scope (deliberately narrow)

### Agents — 2 of the eventual 4
- **Partner Growth Agent** — "which partners are likely to grow / should we recruit / should
  get investment" — pulls Snowflake curated views + Salesforce.
- **Market/GTM Agent** — "which regions/technologies are gaining momentum" — pulls Snowflake +
  external enrichment.
- *Deferred to phase 2:* Event Agent, Messaging Agent (depend on messier Omeda/CDP behavioral
  data).

### Data sources — 2 of the eventual 4+
- **Snowflake** — cleanest, most demo-safe (curated semantic views).
- **Salesforce** — CRM data (partner classification, revenue).
- **Stubbed/mocked for the demo:** Omeda/CDP, Public/External enrichment. State explicitly in
  the proposal: "integration-ready, POC-scoped out."

### Orchestrator pattern — Supervisor/router
1. Orchestrator classifies intent from the user's question → routes to Partner Growth Agent,
   Market/GTM Agent, or both.
2. Sub-agent calls its MCP tools, gets structured data back.
3. Orchestrator (or the sub-agent) synthesizes a natural-language answer with cited numbers.

This mirrors the Analyzer → Executor split from the Angular migration agent design — same
supervisor/worker shape, different domain.

### Context layer scope
- **Context Layer:** conversation memory, last N turns only — no cross-session persistence yet.
- **RAG / Vector Store:** small — partner profile + capability docs, enough to answer
  "which partners resemble top performers."
- **Semantic Cache:** include even at POC stage — cheap to build, visually strong in a demo
  (repeat query costs $0 the second time).
- **MCP & Tools Gateway:** already built; this layer just wires calls into it.

### Demo script — 3 questions spanning sources
1. "Which partners are most likely to grow?" → Snowflake + Salesforce, single-agent.
2. "Which technologies are gaining momentum in [region]?" → Snowflake, single-agent.
3. "Which partners should I recruit, and which regions should I prioritize for them?" → both
   agents — forces the orchestrator to route to two agents and merge results. This is the
   question that proves multi-agent value.

### Explicitly out of scope for POC
- Omeda/CDP and public enrichment integration
- Event Agent, Messaging Agent
- Auth/governance, monitoring/observability (owned by TCC's existing layers per the diagram)
- Multi-turn complex reasoning beyond the 3 demo questions

---

## 3. Open Design Questions (to resolve during implementation)

- Orchestrator routing: rule-based intent classification vs. LLM-based classification for the
  first pass?
- Where does synthesis happen — orchestrator level, or does each sub-agent return its own
  final-form answer that the orchestrator just concatenates?
- Semantic cache key strategy: raw query string, normalized query, or embedding similarity
  threshold?
- Context Layer memory format: raw turn history vs. running summary?

---

## 4. Repo Context

See `README.md` and the existing MCP client setup for Snowflake + data generator already in
this repo. Claude Code should treat this brief as the target design to implement against —
build incrementally: intent classifier → single agent (Partner Growth) working end-to-end →
second agent (Market/GTM) → orchestrator merge logic → semantic cache.