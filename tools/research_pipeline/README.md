# Research Extraction Pipeline

Ontology-first extraction pipeline for converting research markdown files into structured behavioral intelligence assets.

## What it does

- Recursively ingests markdown research files.
- Splits files into semantic sections using markdown heading structure.
- Classifies each section by primary semantic role.
- Runs specialized extractors for variables, states, relationships, interventions, KPIs, temporal dynamics, evidence, and contradictions.
- Preserves provenance on every extracted object.
- Normalizes overlapping concepts without aggressively auto-merging uncertain matches.
- Builds a graph export for future knowledge graph and GraphRAG use.
- Writes a human review queue for low-confidence objects and uncertain merges.
- Generates embeddings-ready semantic chunks for future retrieval systems.

## Layout

- `scripts/run_pipeline.py`: CLI entrypoint.
- `src/research_extraction/`: extraction package.
- `output/`: generated artifacts.

## Usage

```powershell
python .\scripts\run_pipeline.py
```

That command now defaults to:
- research input: `D:\PolyNovea\PolyNovea\Docx\Company Docx\Module 3 - Optimisation\Module 3 research`
- output: `D:\PolyNovea\PolyNovea\Docx\Company Docx\Module 3 - Optimisation\Research Extraction Pipeline\output`

Override the paths only when you intentionally want a different source or destination.

## Optional LLM providers

The default pipeline remains deterministic and local (`--llm-provider none`).

Runner behavior: `scripts/run_pipeline.py` auto-loads `Research Extraction Pipeline/.env` at startup (without overriding env vars already set in the shell).

You can also configure provider credentials for later structured extraction upgrades:

- OpenAI:
  - Set env var: `OPENAI_API_KEY`
  - Use: `--llm-provider openai`
  - Optional: `--llm-model gpt-4.1-mini`
- NVIDIA:
  - Set env var: `NVIDIA_API_KEY`
  - Use: `--llm-provider nvidia`
  - Optional: `--llm-model deepseek-v4-pro`
  - Optional base URL override: `--llm-base-url https://integrate.api.nvidia.com/v1`

PowerShell example (NVIDIA):

```powershell
$env:NVIDIA_API_KEY = "your_new_key_here"
python .\scripts\run_pipeline.py `
  --research-dir "D:\PolyNovea\PolyNovea\Docx\Company Docx\Module 3 - Optimisation\Module 3 research" `
  --output-dir "D:\PolyNovea\PolyNovea\Docx\Company Docx\Module 3 - Optimisation\Research Extraction Pipeline\output" `
  --llm-provider nvidia `
  --llm-model deepseek-v4-pro
```

If `NVIDIA_API_KEY` is missing or the provider call fails, extraction automatically falls back to rule-based output.

## Optional embeddings for normalization

Embeddings-based similarity is optional and only used when `--enable-embeddings` is passed.

- Without `sentence-transformers` installed:
  - pipeline still runs normally
  - normalization uses lexical + alias matching only
- With `sentence-transformers` installed:
  - normalization additionally uses cosine similarity from the configured embedding model

PowerShell example (enable embeddings):

```powershell
python .\scripts\run_pipeline.py `
  --research-dir "D:\PolyNovea\PolyNovea\Docx\Company Docx\Module 3 - Optimisation\Module 3 research" `
  --output-dir "D:\PolyNovea\PolyNovea\Docx\Company Docx\Module 3 - Optimisation\Research Extraction Pipeline\output" `
  --llm-provider none `
  --enable-embeddings
```

## Review decisions and promotion

You can promote reviewed objects into a cleaner ontology artifact by passing `--review-decisions-file`.

Expected JSON format:

```json
{
  "decisions": [
    {
      "review_id": "review_xxx",
      "status": "approved"
    },
    {
      "review_id": "review_yyy",
      "status": "rejected"
    },
    {
      "review_id": "review_zzz",
      "status": "modified",
      "modified_object": {
        "confidence_score": 0.99
      }
    }
  ]
}
```

PowerShell example:

```powershell
python .\scripts\run_pipeline.py `
  --research-dir "D:\PolyNovea\PolyNovea\Docx\Company Docx\Module 3 - Optimisation\Module 3 research" `
  --output-dir "D:\PolyNovea\PolyNovea\Docx\Company Docx\Module 3 - Optimisation\Research Extraction Pipeline\output" `
  --llm-provider none `
  --review-decisions-file "D:\PolyNovea\PolyNovea\Docx\Company Docx\Module 3 - Optimisation\Research Extraction Pipeline\output\review_queue\review_decisions.json"
```

Outputs:
- `output/review_queue/review_queue.json`
- `output/review_queue/approved_ontology.json`
- `output/review_queue/promotion_summary.json`
