# LLMWikiBuilder

A universal LLM-powered wiki builder. Point it at any folder, and it produces a structured, interlinked Markdown wiki — with LLM-generated summaries, cross-references, and Obsidian-compatible output.

Inspired by [Andrej Karpathy's LLM Wiki pattern](karpathy.md).

---

## How it works

```
Source folder  →  [extract text]  →  [LLM summarize]  →  Wiki (.md files)
                                           ↓
                                  [cross-reference pass]
                                           ↓
                                  index.md + log.md
```

Three layers (Karpathy's model):
1. **Raw sources** — your files, never modified
2. **Wiki** — LLM-generated `.md` files with summaries, entities, wikilinks
3. **Schema** — `CLAUDE.md` tells the LLM how to maintain the wiki

---

## Installation

```bash
pip install -e .
```

Requires Python 3.11+. Optional extras are installed on demand with a helpful error if missing (e.g. `pip install pdfplumber` for PDF support).

---

## Quick start

```bash
# 1. Scaffold a new project (interactive)
wiki-builder init --source ./my-docs --wiki ./wiki

# 2. Extract only — no LLM, no cost
wiki-builder ingest --no-llm

# 3. Full LLM run
export ANTHROPIC_API_KEY=sk-ant-...
wiki-builder ingest

# 4. Ask a question
wiki-builder query "What SQL queries touch the employee table?"

# 5. Health check
wiki-builder lint
```

---

## LLM backends

Set `llm.backend` in `wiki.yaml`:

| Backend | Config value | When to use |
|---------|-------------|-------------|
| **Claude API** | `claude-api` | Best quality, paid |
| **Ollama** (local) | `openai-compat` | Free, private, no internet |
| **LM Studio** (local) | `openai-compat` | Free, GUI-based |
| **OpenRouter** | `openai-compat` | Multi-provider gateway |
| **Groq** | `openai-compat` | Fast inference |
| **OpenAI** | `openai-compat` | GPT-4o, etc. |
| **Claude Code CLI** | `claude-code` | Uses your existing subscription |

### Examples

```yaml
# Claude API (default)
llm:
  backend: claude-api
  model: claude-sonnet-4-6
  api_key_env: ANTHROPIC_API_KEY

# Ollama — local, free, private
llm:
  backend: openai-compat
  base_url: "http://localhost:11434/v1"
  model: llama3.2
  api_key: "ollama"

# OpenRouter
llm:
  backend: openai-compat
  base_url: "https://openrouter.ai/api/v1"
  model: google/gemini-2.0-flash-001
  api_key_env: OPENROUTER_API_KEY

# Groq
llm:
  backend: openai-compat
  base_url: "https://api.groq.com/openai/v1"
  model: llama-3.3-70b-versatile
  api_key_env: GROQ_API_KEY

# Claude Code CLI (uses your installed claude binary)
llm:
  backend: claude-code
  model: claude-sonnet-4-6
```

---

## Configuration (wiki.yaml)

Full reference with defaults:

```yaml
project:
  name: "My Wiki"
  obsidian_vault: true

source:
  path: "./docs"             # Folder to index
  exclude_folders: []        # Folder names to skip entirely
  exclude_patterns:          # Filename glob patterns to skip
    - "~$*"
    - "Thumbs.db"
    - ".DS_Store"
  max_file_size_mb: 50

wiki:
  path: "./wiki"
  max_path_length: 240       # Windows MAX_PATH guard

llm:
  backend: "claude-api"
  model: "claude-sonnet-4-6"
  api_key_env: "ANTHROPIC_API_KEY"
  max_input_chars: 15000     # Chunk size for large files
  chunk_overlap_chars: 500
  cache: true                # Disk cache — no re-calls for unchanged files
  cost_guard:
    max_usd_per_run: 5.00
    warn_usd_per_run: 2.00

summarization:
  enabled: true
  max_summary_words: 150
  include_key_entities: true

cross_references:
  enabled: true
  min_confidence: 0.7
  max_links_per_article: 10

tagging:
  tag_taxonomy:              # LLM picks from this list only
    - sql
    - python
    - word
    - excel
    - pdf
    - documentation
    - ...

schema_file: "./CLAUDE.md"
```

---

## CLAUDE.md (wiki schema)

`wiki-builder init` generates a starter `CLAUDE.md`. It serves two purposes:
- **System prompt** for every LLM call — governs summary style, tag taxonomy, section structure
- **Human documentation** of wiki conventions

Edit it to tune the LLM's behavior for your domain. The LLM reads it on every run; changes take effect immediately on the next ingest.

---

## Supported file types

| Type | Extensions |
|------|-----------|
| Plain text / code | `.txt .md .py .sql .js .ts .csv .json .yaml .html .xml .bat .ps1 .sh` + more |
| Word | `.docx .dotx` |
| Excel | `.xlsx .xltx` |
| PDF | `.pdf` |
| PowerPoint | `.pptx` |
| Binary | Noted with size metadata, no text extraction |

---

## Wiki output format

Each article is an Obsidian-compatible `.md` file:

```markdown
---
source: /path/to/file.docx
file_type: Word Document
last_modified: 2025-11-14
wiki_updated: 2026-04-08
tags: [word, documentation]
---

[[index|Home]] > [[folder|Folder]] > **Title**

# Title

> [!info] Word Document · 142 KB · Modified 2025-11-14

## Summary
LLM-generated summary...

## Key Entities
- **System:** InforDB
- **Person:** Eric Johnson

## Content
```raw
Extracted text...
```

## Related
- [[related-page]] — reason for the link
```

---

## CLI reference

```
wiki-builder init   --source PATH --wiki PATH   Scaffold wiki.yaml + CLAUDE.md
wiki-builder ingest [OPTIONS]                   Process files, write wiki
  --incremental / --full                        Skip unchanged files (default: incremental)
  --no-llm                                      Extract only, no API calls
  --no-crossref                                 Skip cross-reference pass
  --dry-run                                     Show what would happen
  --verbose, -v                                 Print every file
  --llm-backend TEXT                            Override backend from config
wiki-builder query  QUESTION                    Ask a question against the wiki
  --save                                        Save answer as a new wiki page
wiki-builder lint   [--fix]                     Health check: orphans, broken links, stale
wiki-builder status                             Show wiki state summary
```

---

## Example configs

See [`example-configs/`](example-configs/) for ready-to-use setups:

- **`personal-notes/`** — Claude API, concise summaries, personal tag taxonomy
- **`research-papers/`** — Ollama (local/free), detailed paper summaries, academic tags

---

## Security notes

- **API keys**: Always use `api_key_env` to reference an environment variable. Never put real keys in `wiki.yaml` directly — if you do, do not commit that file.
- **Source content is sent to the LLM**: Documents you index will be sent to whatever backend you configure. Use a local backend (Ollama, LM Studio) for sensitive content.
- **Prompt injection**: Source documents could theoretically contain text designed to manipulate the LLM's output. The tool uses structured XML-style delimiters to reduce this risk, but no mitigation is foolproof. Review LLM-generated summaries for sensitive wikis.
- **`base_url`**: When using `openai-compat`, the `base_url` you configure receives all document content. Only point it at servers you trust.

---

## Incremental updates & caching

- **Extraction state**: `_wiki_state.json` tracks file hashes. Unchanged files are skipped on `--incremental` runs (default).
- **LLM cache**: `_wiki_llm_cache.json` caches LLM responses by content hash. Changing the model invalidates the cache per file. A full rebuild (`--full`) still won't re-call the API for files whose content hasn't changed.
- Both files are gitignored — they're machine-local caches.

---

## Requirements

```
anthropic>=0.40.0
openai>=1.30.0
click>=8.1
rich>=13.0
pyyaml>=6.0
python-docx>=1.1
openpyxl>=3.1
pdfplumber>=0.10
python-pptx>=0.6
jinja2>=3.1
```
