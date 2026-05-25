<div align="center">

# 🧠 Eagle - Agentic Vision Surveillance System

### *Moving from Object Detection to Intent Inference*

[![GSSoC 2026](https://img.shields.io/badge/GSSoC-2026-orange?style=for-the-badge&logo=github)](https://gssoc.girlscript.tech)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=for-the-badge)](CONTRIBUTING.md)

<br/>

**Traditional CV detects → Eagle *understands*.**

Traditional systems say `"Person detected"`.  
Eagle says `"A person is loitering near the restricted exit and repeatedly looking at the keypad."` 
<img width="870" height="784" alt="Untitled-2026-03-21-1849" src="https://github.com/user-attachments/assets/05b97159-f28f-4587-8c37-e849238cc6f2" />
***
Eagle — Real-Time Semantic Surveillance (v1.1)

Eagle combines detection, tracking, short-term memory and multimodal reasoning to produce explainable, temporal alerts (e.g. "Suspicious — repeated keypad interaction"). This README is focused on the new Phase 4 reasoning components added in v1.1 and developer workflows.

Contents

- What’s new in v1.1
- Quick start (dev)
- Running reasoning (mock vs Ollama)
- Tests & CI
- Files of interest
- Contributing & license

---

## What’s new (v1.1)

- Phase 4 reasoning pipeline: `services/reasoning` (VLM captioners, grounding, LLM reasoner, dedup, pipeline orchestration).
- Unit test suite for reasoning: `tests/test_reasoning.py` (mocks for VLM/LLM, fakeredis for Redis). 40 tests included.
- GitHub Actions workflow: `.github/workflows/phase4-tests.yml` to run reasoning tests with Redis.

---

## Quick start (development)

1. Create and activate a virtualenv

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

2. Install reasoning dev requirements (fast, mock-friendly)

```bash
pip install -r services/reasoning/requirements.txt
```

3. Run reasoning tests (mocked, no GPU or external APIs)

```bash
VLM_PROVIDER=mock LLM_PROVIDER=mock pytest tests/test_reasoning.py -q
```

Expect ~40 tests passing in a couple of seconds.

---

## Running the Reasoning Pipeline

Quick smoke with mocks (no external services):

```bash
export VLM_PROVIDER=mock
export LLM_PROVIDER=mock
python -c "from services.reasoning.pipeline import ReasoningPipeline; import numpy as np; p=ReasoningPipeline(); print('Pipeline ready')"
```

With local Ollama (LLaVA-Next) — optional, for higher-quality captions

1. Install and run Ollama following their docs.
2. Pull models you need:

```bash
ollama pull llava:latest
ollama pull mixtral:latest
ollama serve &
```

3. Run pipeline with Ollama providers:

```bash
export VLM_PROVIDER=ollama
export LLM_PROVIDER=ollama
python -c "from services.reasoning.pipeline import ReasoningPipeline; import numpy as np; p=ReasoningPipeline(); print('Pipeline ready')"
```

Notes: Ollama-based runs require `httpx` and a running Ollama server. For CI and most development we use `mock` providers to keep runs deterministic and fast.

---

## Tests & CI

- Local tests: `pytest tests/test_reasoning.py` (mocks + fakeredis). Keep tests offline-friendly.
- CI: `.github/workflows/phase4-tests.yml` runs reasoning tests on pushes affecting reasoning code and schemas. The workflow starts a Redis service and uses `VLM_PROVIDER=mock` to avoid external model calls.

If you add new tests that rely on heavy external models, please also add a mocked variant to keep CI fast and reliable.

---

## Files of interest

- `services/reasoning/` — `vlm.py`, `llm.py`, `prompts.py`, `pipeline.py`, `dedup.py`, `formatters.py`
- `libs/schemas/reasoning.py` — Pydantic models for reasoning outputs
- `services/memory/ring_buffer.py` — MemoryStore used by tests/pipeline
- `tests/test_reasoning.py` — reasoning unit tests
- `.github/workflows/phase4-tests.yml` — CI workflow for Phase 4 tests

---

## Contributing

See `CONTRIBUTING.md`. Quick tips:

- Run reasoning tests before opening a PR: `pytest tests/test_reasoning.py -q`
- Use `VLM_PROVIDER=mock` and `LLM_PROVIDER=mock` for fast local iterations.

---

## License

This repository is released under the MIT License. See `LICENSE` for details.

