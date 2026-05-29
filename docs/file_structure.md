# Module 3 — File Structure Reference

> Last updated: 2026-05-29  
> 28 research md files in `backend/research/` (flat, snake_case).  
> Pipeline scripts live in `tools/research_pipeline/` — output lands in `backend/research_pipeline/output/`.

```
D:\PolyNovea\PolyNovea\Docx\Company Docx\Module 3 - Optimisation\
│
├── backend\                     # FastAPI backend and static data assets
│   ├── main.py                  # Backend API entrypoint
│   ├── database.py              # DB connection layer & settings
│   ├── models.py                # SQLAlchemy models / Schemas
│   ├── requirements.txt         # Backend Python dependencies
│   ├── .env                     # M3 env vars — M3_DATABASE_URL → polynovea_m3 on Azure PG
│   │
│   ├── routers\                 # API Router controllers
│   │   ├── kpi.py
│   │   ├── session_brief.py     # Has TODO placeholders for Council wiring (Phase 6)
│   │   └── show.py              # Has TODO placeholders for Council wiring (Phase 6)
│   │
│   ├── research\                # Flattened research assets (28 snake_case md files)
│   │   └── *.md                 # All consolidated research documents — DO NOT nest subfolders
│   │
│   └── research_pipeline\       # Generated database outputs (read by backend at runtime)
│       └── output\
│           ├── canonical_knowledge_store.json
│           ├── ontology_graph.json
│           ├── ontology_graph.graphml
│           ├── rag_chunks.json
│           ├── rag_chunks.jsonl
│           ├── run_summary.json
│           ├── review_queue.json
│           ├── approved_ontology.json
│           ├── variables.json
│           ├── behavioral_states.json
│           ├── causal_relationships.json
│           ├── interventions.json
│           ├── kpis.json
│           ├── temporal_dynamics.json
│           ├── evidence_registry.json
│           ├── contradictions.json
│           ├── validation_report.json
│           ├── coverage_report.json
│           ├── graph_health.json
│           └── review_queue\    # Human review workflow artifacts
│
├── dashboard\                   # React + Vite + TypeScript Dashboard
│   ├── index.html
│   ├── package.json             # Vite, Zustand, React, TypeScript
│   ├── vite.config.ts
│   ├── dist\                    # Compiled production build
│   └── src\
│       ├── main.tsx
│       ├── App.tsx
│       ├── types\               # TypeScript definitions
│       ├── store\               # Zustand — sessionStore.ts
│       ├── styles\              # tokens.css, globals.css
│       ├── hooks\               # Timers, table state, KPI RAG calculators
│       └── components\
│           ├── setup\           # SessionSetup, VenueInput, TableStepper
│           ├── logger\          # FloorLogger, DoorFlow, TablesTab, EnvironmentTab
│           ├── monitor\         # KPIMonitor, ZoneTabBar, KPICard, SignalRow
│           └── shared\          # Header, InactiveBanner, Badge, ToastRack, SegmentedControl
│
├── tools\                       # Dev scripts — NOT served by backend
│   └── research_pipeline\       # Extraction pipeline source code
│       ├── README.md            # Runner guide and config docs
│       ├── requirements.txt     # Pipeline dependencies (separate from backend)
│       ├── .env                 # LLM API keys for extraction
│       ├── scripts\             # run_pipeline.py, build_review, etc.
│       ├── tests\               # Pipeline validation test suites
│       └── src\
│           └── research_extraction\   # Inner extraction package
│
├── db\                          # SQL schemas and seeds
│   ├── m3_schema.sql            # M3 operational schema — APPLIED to Azure PG
│   ├── m3_m2_feed_tables.sql    # Feed tables for M2 RDS — NOT YET run
│   ├── create_db.py             # One-time: created polynovea_m3 database
│   └── run_schema.py            # One-time: applied m3_schema.sql
│
├── docs\                        # Architecture docs and session archives
│   ├── file_structure.md        # THIS FILE
│   ├── m3_todo.md               # Master todo list
│   ├── module_3_refined_architecture.md
│   ├── module_3_db_plan.md
│   ├── behavioral_pipeline_refactor_brief.md
│   └── session_retrospective_2026_05_28.json
│
├── keys\
│   └── polynovea-m3-key.pem     # SSH key for Azure VM (polynovea-m3-api)
│
├── show-engineering\            # SE recommendations logic and config rules
│
└── Research Extraction Pipeline\  # Empty — kept as path placeholder only
```

## Key Separation Rules

| Concern | Location |
|---------|----------|
| Pipeline **source code** | `tools/research_pipeline/` |
| Pipeline **output** (runtime assets) | `backend/research_pipeline/output/` |
| Research **documents** | `backend/research/` (flat, never nest) |
| SE research documents | `backend/research_se/` (flat — to be created) |
| SE pipeline output | `backend/research_pipeline/output_se/` (to be created) |
| DB schemas | `db/` (root level, not inside backend) |
| SSH keys | `keys/` (root level, never commit) |

## Infrastructure Quick-Reference

| Resource | Value |
|----------|-------|
| Azure PostgreSQL | polynovea-m3.postgres.database.azure.com, port 5432, DB: polynovea_m3 |
| Azure VM | polynovea-m3-api, 20.219.216.138, Ubuntu 22.04, user: subrojitroy |
| SSH key | keys/polynovea-m3-key.pem |
| M2 RDS | M2 AWS RDS — access via M2 EC2 SSH or whitelist dev IP |
| M3_DATABASE_URL | In backend/.env → points to polynovea_m3 |
