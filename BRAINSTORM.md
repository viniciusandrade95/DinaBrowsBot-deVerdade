# Architecture Review for Modular "Lego" Bot

## Observed issues and risks
- **Tight coupling between concerns:** Routing, intent logic, rule responses, and model invocation live in shared modules (e.g., `bot/core.py`, `bot/router.py`), making it harder to swap implementations per tenant or feature flag.
- **Limited plugin boundaries:** Rule-based handlers and model prompts are intertwined with tenant configuration rather than exposed as discrete capability modules (tone, safety, commerce flows, FAQ, small talk), which limits composability.
- **State store is in-memory only:** Session data is transient and not abstracted behind a persistence interface, so scaling or running multiple instances would lose context and invite race conditions.
- **Error handling and observability gaps:** Errors from WhatsApp and model calls are logged minimally; there is no structured telemetry, tracing, or retry policy, making troubleshooting and SLO enforcement difficult.
- **Safety and policy controls are implicit:** Content safety, PII handling, and rate limiting are not first-class modules; enforcement depends on prompt wording and scattered guards.
- **Testing surface is small:** There are few automated tests for routing, rule handlers, or safety guards, leaving regressions likely when rearranging modules.
- **Configuration drift risk:** Tenant configuration is mutable in memory without schema validation or migration strategy, making consistency hard as features grow.

## Improvement ideas for a modular, Lego-style bot
- **Define clear capability interfaces:** Introduce pluggable modules for tone, safety, routing, commerce flows, and integrations. Each module exposes a small interface (e.g., `respond(message, context)` or `guard(message)`), enabling composition and swapping.
- **Capability registry and pipeline:** Build a registry that wires modules into a request pipeline: ingress → safety gates → intent classification → capability selection → response assembly → egress. Keep each stage isolated with typed contracts.
- **Config-driven assembly:** Use declarative config (YAML/JSON) to map tenants to modules and policies. Validate configs against a schema and support versioned migrations to avoid drift.
- **State provider abstraction:** Define a persistence interface (e.g., `StateStore`) with implementations for in-memory, Redis, or database backends. Inject the store so scaling horizontally keeps context.
- **Safety and compliance layer:** Add dedicated modules for content filtering, PII redaction, rate limiting, and audit logging, enforced early in the pipeline and before external calls.
- **Prompt and tone packs:** Package prompt templates and tone rules as swappable bundles per tenant, separate from business logic, so experiments don’t ripple through core code.
- **Capability-level observability:** Emit structured events (timings, errors, model call metadata, user journey markers) per module. Standardize error types and retries for external services.
- **Testing harness:** Provide contract tests for each module and end-to-end scenarios for the pipeline to ensure new modules don’t break existing flows.
- **Experimentation hooks:** Support feature flags at the module boundary (e.g., alternate intent classifiers or model sizes) with guardrails and rollback paths.
- **Integration adapters:** Wrap external services (LLM provider, WhatsApp API) behind adapter interfaces so that swapping providers doesn’t affect core logic.

## Does the modular approach make sense?
Yes—the current code already centralizes routing but keeps concerns intertwined. Carving the system into small, single-purpose modules with defined contracts will make it easier to recombine capabilities like tone, safety, and channel adapters as independent Lego pieces while reducing coupling and regression risk.
