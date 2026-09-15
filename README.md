# NLtoSQL-Ollama

LLM-powered natural language to SQL query system for a CNC manufacturing database. Runs locally via Ollama (Qwen2.5-Coder) — no external API required.

## Tech Stack

- Python
- [Ollama](https://ollama.com) + Qwen2.5-Coder:7b
- SQLite

## Overview

This project translates natural language questions into executable SQL queries against a CNC manufacturing database (machines, production, downtime, and maintenance records). It was built as a from-scratch exploration of Text-to-SQL systems, using a local open-weight LLM instead of a paid API.

Ask a question like:

> "Which machine had the most downtime in the last 30 days?"

...and the system converts it to SQL, runs it against the database, and returns the answer — with no SQL knowledge required from the user.

## Features

- **Fully local inference** — runs on Qwen2.5-Coder:7b via Ollama, no API key or internet connection required after setup
- **Schema-aware prompting** — the database schema is read directly from SQLite and injected into the prompt automatically
- **Execution-guided self-correction** — if a generated query fails to execute, the error message is fed back to the model, which retries (up to 3 attempts)
- **Unanswerable question detection** — the model is instructed to return a fixed sentinel value when a question cannot be answered from the given schema, instead of guessing
- **Zero-shot and few-shot prompting support** — both strategies are implemented and were compared experimentally (see [Experiment Report](docs/experiment-report.md))
- **Safety guard on execution** — only `SELECT` statements are allowed to run; destructive keywords (`DROP`, `DELETE`, `UPDATE`, etc.) are blocked before execution

## How It Works

```
User question
     │
     ▼
Schema read from SQLite ──► Prompt built (schema + question + rules)
     │
     ▼
LLM generates SQL (Ollama / Qwen2.5-Coder)
     │
     ▼
SQL cleaned (strip markdown/formatting)
     │
     ▼
Safety check (SELECT-only) ──► Execute against SQLite
     │
     ├── Success ──► Return result
     │
     └── Error ──► Send error + previous SQL back to LLM ──► Retry (up to 3x)
```

## Database Schema

A small SQLite database (`cnc.db`) simulating a CNC manufacturing floor:

| Table | Columns |
|---|---|
| `machines` | machine_id, machine_name, model |
| `production` | production_id, machine_id, part_name, quantity, production_time |
| `downtime` | downtime_id, machine_id, reason, duration, date |
| `maintenance` | maintenance_id, machine_id, maintenance_type, date |

## Setup

1. **Install Ollama** from [ollama.com/download](https://ollama.com/download)

2. **Pull the model**
   ```bash
   ollama pull qwen2.5-coder:7b
   ```

3. **Clone the repo and set up a virtual environment**
   ```bash
   git clone https://github.com/ebubekirdogan/NLtoSQL-Ollama.git
   cd NLtoSQL-Ollama
   python -m venv venv
   venv\Scripts\Activate   # Windows
   ```

4. **Install dependencies**
   ```bash
   pip install ollama
   ```

5. **Create the database** (already included as `cnc.db`, but can be regenerated)
   ```bash
   python create_db.py
   python seed_db.py
   ```

## Usage

Run the interactive CLI:

```bash
python main.py
```

Then type a question in natural language (Turkish or English):

```
Soru: Which machine had the most downtime in the last 30 days?

(Üretilen SQL - 1. denemede)
SELECT machine_id, SUM(duration) AS total_duration
FROM downtime
WHERE date >= DATE('now', '-30 days')
GROUP BY machine_id
ORDER BY total_duration DESC
LIMIT 1;

machine_id | total_duration
-----------|---------------
M04        | 275.0
```

## Project Structure

| File | Purpose |
|---|---|
| `create_db.py` | Creates the SQLite schema |
| `seed_db.py` | Populates the database with sample data |
| `schema_utils.py` | Reads the schema from SQLite and converts it to prompt text |
| `sql_generator.py` | Builds prompts (zero-shot and few-shot) and calls the LLM |
| `db_executor.py` | Executes SQL safely (SELECT-only) and returns results |
| `pipeline.py` | Orchestrates the full flow, including the self-correction loop |
| `main.py` | Interactive CLI entry point |
| `test_questions.py` | Fixed test set (14 questions) with reference SQL, used for evaluation |
| `run_experiment.py` | Runs the test set through both prompting strategies and logs results |
| `experiment_results.csv` | Raw results from the prompting strategy experiment |
| `docs/experiment-report.md` | Full write-up of the experiment (methodology, results, findings) |

## Known Limitations

- The model occasionally omits `GROUP BY` when aggregating totals (e.g. "most downtime overall" vs. "longest single downtime event"), producing a query that executes successfully but answers a slightly different question.
- The unanswerable-question fallback is not fully reliable — the model sometimes generates a plausible but unrelated query instead of recognizing that the requested data doesn't exist in the schema.

See [docs/experiment-report.md](docs/experiment-report.md) for a detailed discussion of these findings.

## Background

This project was built alongside a research phase covering LLM fundamentals, Text-to-SQL techniques, prompt engineering, schema linking, and self-correction strategies.
