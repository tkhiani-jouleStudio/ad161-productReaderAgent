# Product Master Data Q&A Agent

AI agent enabling Sales Representatives to ask natural language questions about product master data from SAP S/4HANA Public Cloud Edition and receive instant, accurate answers.

## Business challenge

Sales Representatives spend excessive time (5+ minutes per query) manually looking up product information across SAP S/4HANA. This leads to delayed customer responses and inaccurate product information being shared. An AI agent should provide instant, natural language access to authoritative product master data.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Time per product query | 5 minutes | Under 30 seconds | — | Product Master Data Lookup | user |
| Reduction in incorrect product info shared | — | — | — | Product Information Accuracy | user |

## Key Milestones

1. **Agent responds to basic product queries** — Sales Rep asks "What is the description of product X?" and receives an accurate answer from S/4HANA
2. **Classification data accessible** — Agent answers queries about product categories, classes, and technical specifications
3. **Availability queries supported** — Agent answers stock and availability questions per plant/location
4. **Pricing procedure context provided** — Agent retrieves relevant pricing procedure information for a product
5. **Agent deployed and usable by Sales Reps** — Agent is live and accessible via the Joule Studio interface

## Business Architecture (RBA)

### End-to-End Process

Lead to Cash Standard B2B

### Process Hierarchy

```
Lead to Cash Standard B2B (E2E)
└── Plan to Optimize Marketing and Sales (Phase)
    └── Plan prices and promotions (BPS-359_002)
        └── Plan and define sales prices
```

### Summary

Sales Reps querying product master data maps to Lead to Cash (Standard B2B), specifically the sub-process for planning prices and promotions — where having accurate, instantly accessible product and pricing data directly supports effective sales execution.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Webhook API ORD ID | Gap? | Notes / assumptions |
|------------------------|------------------------|------------|-------------------|--------------------|--------------------|------|---------------------|
| Query product master data (descriptions, UoM, basic attributes) | SAP S/4HANA Cloud Public Edition | `sap.s4:apiResource:API_PRODUCT_SRV:v1` | — | — | — | No | No pre-built MCP; translation file to be generated |
| Query product classification and technical specs | SAP S/4HANA Cloud Public Edition | `sap.s4:apiResource:API_CLFN_PRODUCT_SRV:v1` | — | — | — | No | Covers classification data including custom characteristics |
| Query product availability per plant/location | SAP S/4HANA Cloud Public Edition | `sap.s4:apiResource:CE_API_PRODUCT_AVAILY_INFO_0001:v1` | — | — | — | No | Cloud-native availability info API |
| Query basic stock/availability info | SAP S/4HANA Cloud Public Edition | `sap.s4:apiResource:API_PRODUCT_AVAILY_INFO_BASIC:v1` | — | — | — | No | Simpler availability API as fallback |
| Query pricing procedures for a product | SAP S/4HANA Cloud Public Edition | `sap.s4:apiResource:API_SLSPRICINGPROCEDURE_SRV:v1` | — | — | — | No | Read-only pricing procedure data |
| Natural language understanding & response generation | Custom AI Agent | — | — | — | — | Yes | Requires custom Python agent with LLM reasoning |

### Key findings

- SAP S/4HANA Cloud Public Edition provides 5 relevant available APIs covering product master, classification, availability, and pricing procedures
- No pre-built MCP servers exist for any of these APIs — MCP translation files must be generated from the OData/API specs
- Pricing REST APIs (sap.aribas4, external) are unavailable in this landscape and must be excluded
- The natural language reasoning layer is a gap — addressed by building a custom Python AI agent
- The solution is fully covered by standard S/4HANA Public Cloud APIs with a custom agent layer on top
- No n8n workflow required; the agent directly calls S/4HANA APIs via generated MCP tools

## Recommendations

### AI Agent for Product Master Data Q&A

#### Executive Summary

Python AI agent with S/4HANA MCP tools for instant product data access

#### Recommended Solution

Build a pro-code Python AI agent (A2A protocol) that connects to SAP S/4HANA Cloud Public Edition via MCP tool calls generated from OData API specs. The agent handles natural language questions from Sales Representatives about product descriptions, classifications, availability, and pricing procedures — returning structured, accurate answers in seconds.

#### Recommended solution category

AI Agent

#### Intent fit
92%
