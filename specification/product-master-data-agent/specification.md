# Specification: product-master-data-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [x] Read the project input (`product-requirements-document.md`, `intent.md`)
- [x] Bootstrap agent code in `assets/product-master-data-agent/` using instructions from the sap-agent-bootstrap section (invoke from inside `assets/product-master-data-agent/`, use copy commands — do NOT create files manually)
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

> Read [guidelines-agent-skills.md](../guidelines-agent-skills.md) before proceeding.

No runtime skills are required for this agent — the query patterns are straightforward lookups without complex multi-step workflows or large domain-specific knowledge bases.

---

## Project-Specific Tasks

### Agent Identity & System Prompt

- [ ] Set the agent name to `Product Master Data Agent`
- [ ] Set the agent description to: "Answers natural language questions from Sales Representatives about product master data including descriptions, classifications, availability, and pricing procedures using SAP S/4HANA data."
- [ ] Configure the system prompt in `app/agent.py` to instruct the agent to:
  - Answer questions about product descriptions, classifications, technical specs, availability per plant/location, and pricing procedures
  - Always use MCP tools to retrieve data — never fabricate or estimate product data
  - When no data is found, respond clearly with "I don't have that information" and suggest contacting a product expert
  - Keep responses concise and factual, suitable for use during customer conversations
  - Only answer questions within the scope of product master data (redirect out-of-scope questions)

### Product Master Data Query Tool (API_PRODUCT_SRV)

- [ ] Ensure the MCP server generated from `specification/product-master-data-agent/api-specs/API_PRODUCT_SRV.edmx` provides tools to:
  - List/read products by product ID
  - Read product descriptions and basic attributes (unit of measure, product type, base unit)
- [ ] Wire tool in `agent.py` via `get_mcp_tools()` — never import directly from SAP SDK

MCP API: sap.s4:apiResource:API_PRODUCT_SRV:v1
MCP tool scope: read-only
Resources in scope: A_Product, A_ProductDescription, A_ProductBasicText

### Product Classification Query Tool (API_CLFN_PRODUCT_SRV)

- [ ] Ensure the MCP server generated from `specification/product-master-data-agent/api-specs/API_CLFN_PRODUCT_SRV.edmx` provides tools to:
  - Read product classifications (class assignments)
  - Read product characteristic values (technical specifications)
- [ ] Wire tool in `agent.py` via `get_mcp_tools()`

MCP API: sap.s4:apiResource:API_CLFN_PRODUCT_SRV:v1
MCP tool scope: read-only
Resources in scope: A_ClfnProduct, A_ClfnProductClass, A_ClfnProductCharc

### Product Availability Query Tool (CE_API_PRODUCT_AVAILY_INFO_0001)

- [ ] Ensure the MCP server generated from `specification/product-master-data-agent/api-specs/CE_API_PRODUCT_AVAILY_INFO_0001.edmx` provides tools to:
  - Read product availability info per plant/storage location
- [ ] Wire tool in `agent.py` via `get_mcp_tools()`

MCP API: sap.s4:apiResource:CE_API_PRODUCT_AVAILY_INFO_0001:v1
MCP tool scope: read-only
Resources in scope: ProductAvailabilityInfo

### Basic Product Availability Query Tool (API_PRODUCT_AVAILY_INFO_BASIC)

- [ ] Ensure the MCP server generated from `specification/product-master-data-agent/api-specs/API_PRODUCT_AVAILY_INFO_BASIC.edmx` provides tools to:
  - Read basic stock and availability information as fallback
- [ ] Wire tool in `agent.py` via `get_mcp_tools()`

MCP API: sap.s4:apiResource:API_PRODUCT_AVAILY_INFO_BASIC:v1
MCP tool scope: read-only
Resources in scope: A_ProductAvailabilityInfo

### Pricing Procedure Query Tool (API_SLSPRICINGPROCEDURE_SRV)

- [ ] Ensure the MCP server generated from `specification/product-master-data-agent/api-specs/API_SLSPRICINGPROCEDURE_SRV.edmx` provides tools to:
  - Read sales pricing procedures
  - Read pricing procedure steps and conditions
- [ ] Wire tool in `agent.py` via `get_mcp_tools()`

MCP API: sap.s4:apiResource:API_SLSPRICINGPROCEDURE_SRV:v1
MCP tool scope: read-only
Resources in scope: A_SlsPricingProcedure, A_SlsPricingProcedureStep

### Guardrails

- [ ] Implement guardrail: agent only performs read-only operations — no create, update, or delete MCP tool calls
- [ ] Implement guardrail: if an API returns an error, relay the error message clearly without fabricating alternative data
- [ ] Implement prompt injection detection (included in bootstrap — verify it is active)
- [ ] Implement guardrail: if a question is outside the product master data scope, politely redirect the user

---

## Business Instrumentation

- [ ] Implement structured logging and OpenTelemetry spans for each milestone:
  - **M1** — basic product query: `M1.achieved: basic product query resolved successfully from API_PRODUCT_SRV` / `M1.missed: basic product query did not return data from API_PRODUCT_SRV`
  - **M2** — classification query: `M2.achieved: product classification query resolved from API_CLFN_PRODUCT_SRV` / `M2.missed: product classification query failed or returned no data`
  - **M3** — availability query: `M3.achieved: product availability query resolved from availability API` / `M3.missed: product availability query did not return usable data`
  - **M4** — pricing procedure query: `M4.achieved: pricing procedure query resolved from API_SLSPRICINGPROCEDURE_SRV` / `M4.missed: pricing procedure query returned no relevant data`
  - **M5** — end-to-end: `M5.achieved: agent live and first end-to-end user query successfully completed` / `M5.missed: agent deployment or first user query failed`
- [ ] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`
- [ ] Extract business logic from `stream()` into a plain async helper to avoid `GeneratorExit` context errors

---

## MCP Tool Integration

> Read [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) for complete MCP integration patterns.

- [x] Verify `specification/product-master-data-agent/api-specs/` contains all 5 downloaded EDMX spec files:
  - `API_PRODUCT_SRV.edmx`
  - `API_CLFN_PRODUCT_SRV.edmx`
  - `CE_API_PRODUCT_AVAILY_INFO_0001.edmx`
  - `API_PRODUCT_AVAILY_INFO_BASIC.edmx`
  - `API_SLSPRICINGPROCEDURE_SRV.edmx`
- [x] Invoke `mcp-translation-file` skill for each of the 5 EDMX files to generate MCP translation files (4 successful; API_PRODUCT_AVAILY_INFO_BASIC skipped — covered by CE availability API)
- [x] Invoke `setup-solution` to create `solution.yaml` and `asset.yaml` files, and register the generated MCP server assets
- [x] Wire MCP tool loading in `agent.py` using `get_mcp_tools()` from the `mcp_tools` module
- [x] Add all MCP server dependencies to `asset.yaml` under `requires` using the generated ORD IDs
- [x] Generate `mcp-mock.json` using the `mcp-mock-config` skill after MCP translation files are complete

---

## Testing

> See [guidelines-agent-python.md](../guidelines-agent-python.md) for Python testing setup and patterns.

- [ ] `conftest.py` only sets `IBD_TESTING=true`
- [ ] Write unit tests in `assets/product-master-data-agent/tests/`:
  - One test per MCP tool (product query, classification query, availability query, basic availability query, pricing procedure query)
  - Test that agent returns clear "I don't have that information" when APIs return no data
  - Test prompt injection detection
- [ ] Write one integration test executing end-to-end agent flow with mocked LLM responses and mocked MCP tools
- [ ] Run `pytest` from `assets/product-master-data-agent/` (no args) — if coverage < 70%, add tests
- [ ] Run `pytest` again from `assets/product-master-data-agent/` (no args) to generate final `test_report.json`
- [ ] Verify `test_report.json` exists in `assets/product-master-data-agent/`
