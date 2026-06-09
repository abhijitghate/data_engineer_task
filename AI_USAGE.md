# AI Coding Assistance Disclosure

This assignment requires transparency about AI tool usage during development.

## Instructions
Please complete the sections below honestly. Using AI tools is **acceptable and expected**. We want to understand **how** you used them.


## 1. AI Tools Used
Codex (in VSCode)


## 2. Components Assisted
Check which parts received AI assistance:

- [ ] Data extraction logic (Excel parsing, MASTER sheet)
- [x] Data modeling design (ERD, table schemas, SCD Type 2)
- [x] ETL pipeline implementation
- [x] Data validation framework
- [x] API endpoint development (FastAPI)
- [x] Docker/Docker Compose configuration
- [ ] SQL queries and migrations
- [x] Testing (unit/integration tests)
- [x] Documentation (README, comments)
- [ ] Debugging specific issues
- [ ] Other: JSON logging with parameters


## 3. Detailed Description
For each major component, describe how AI assisted.

#### Data modeling design (ERD, table schemas, SCD Type 2)
- AI support was used to validate modeling choices, especially deciding which attributes belong in slowly changing dimensions (SCD Type 2) versus fact tables.
- Codex helped scaffold SQLAlchemy models and Pydantic schemas, including the larger ingestion schema and metric status fields.
- AI was also used to review schema consistency across parser output, validation models, ORM models, and SQL DDL, reducing key/field mismatch risk.
    
#### ETL pipeline implementation
- Codex was used extensively for pipeline code review and implementation cleanup.
- AI-assisted changes included checksum-based idempotency (`file_checksum`) and clearer ETL stage handoff (parse -> validate -> transform -> load).
- It also helped define a transformer contract for natural-key payloads and insert-ready payloads, improving separation of concerns between transformation and persistence.


#### Data validation framework
- AI suggested explicit status handling for time-series metrics (`numeric`, `no_data`, `locked`, `missing`, `invalid`) rather than relying on nullable numeric values alone.
- Codex helped implement validator logic to normalize mixed raw values into typed metric/value-status pairs.
- Additional validation updates included checksum generation from source files and constrained numeric validation for `industry_weight` to align with database rules.

#### API endpoint development (FastAPI)
- AI assistance was used to scaffold a read-focused FastAPI application structure with routers, dependency wiring, service layer, repository layer, and response schemas.
- Initial endpoint patterns were drafted manually, then expanded with Codex to cover company, snapshot, and upload read endpoints consistently.
- Codex also helped refactor repository queries from raw SQL strings to SQLAlchemy Core `select()` expressions while preserving endpoint behavior.

#### Docker/Docker Compose configuration
- AI provided support in refining container startup sequencing and dependency handling (for example, `depends_on` behavior and service orchestration review).
- Configuration guidance was used as a baseline and then adjusted manually to match local runtime behavior.


#### Testing (unit/integration tests)
- Codex recommended including integration testing against database-backed flows in addition to unit-level checks.
- AI support was used to propose and scaffold test coverage for endpoint/service behavior and data pipeline validation paths.
- Syntax and structural verification (`py_compile`) was used iteratively after major changes as a lightweight guard during development.

#### Documentation (README, comments)
- AI assistance was used to improve documentation quality and consistency in `README.md` and `AI_USAGE.md`.
- Since raw chat history exports/screenshots were not available in the repository, the interaction timeline was reconstructed from commit history and current session context.
- The reconstructed log is documented at `docs/ai-logs/reconstructed_interaction_log_2026-06-09.md`.

## 4. Chat History / Logs
Attach or link to chat history logs showing AI interactions.

**Format:** PDF, Markdown, screenshots, or text files
**Location:** [Provide links or attach files here]

**Location:**
- Reconstructed interaction log (based on commit history + session context):
  - `docs/ai-logs/reconstructed_interaction_log_2026-06-09.md`

**Availability note:**
- Raw full chat transcripts/screenshots are not currently stored in this repository.
- The linked reconstructed log provides a dated timeline with commit-level evidence and session-level summary.

**Note:** You may redact personal information but maintain enough context to show the AI interaction.


## 5. Self-Assessment
Reflect on your AI usage:

**What did AI do well?**

- Maitaining code quality to a higher standard
- Accelerate development process to a supersonic speed
- Vaible suggestions that improved the implementation quality significantly
- Code review and production readiness
- Granular data type checks

**What did you need to correct or override?**
- Invasive code changes by assuming/ infering some information
- Pushing its own approach in design

**What did you implement entirely on your own?**
- SQL DDL
- Structure of pipline
- IngestionSchema
- Excel parsing logic and parser implementation


**How did AI tools improve your development process?**
- Speed: 10x acceleration whilst maintaining code quality
- Covered blind spots and experice gaps
- Helped in lacking domain knowledge

**Were there any limitations or challenges with AI assistance?**
For the current scope, there were very fewer challenges. 
- Since it was a small scale (although, production ready) task, the financial cost of tools such as AI will come into the plat at some point or the other.
- Suggestions by AI were capable of causing feature creeps.
- It creates an illusion of reaching to completion but keeps pushing forwar. One would never feel that they have fully finished a task if they were to rely on AI reviews/ assistance. 


## 6. Recommendations
Based on your experience, what advice would you give to others using AI tools for data engineering tasks?

It is an extremely powerful tool, but one needs to have clear and solid imagination of what they actually want to implement.


Thank you for your transparency!
