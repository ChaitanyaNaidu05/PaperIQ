# PaperIQ - Lightweight (Serverless-Ready) Task List

## Global Rules
- Python only.
- No comments, no emojis in code.
- LIGHTWEIGHT ONLY: External dependencies must not exceed ~200MB total. No PyTorch, No Transformers.
- Use Scikit-learn, NLTK, and Regex for all intelligence.
- All stages must pass validation 100%.

---

## STAGE 1 — Optimization & Core Fixes

### 1.1 Fix Multi-Paper Comparison Visuals (White Boxes)
- Ensure all CSS badges and cards have explicit `color: #xxxxxx !important` to prevent invisible text in Streamlit dark mode.
- DONE: CSS updated in styles.py.

### 1.2 Gut Transformer Dependencies & Implement Lightweight Semantic Engine
- Remove `transformers`, `sentence-transformers`, `torch` from `requirements.txt`.
- Rewrite `core/transformer_analyzer.py` (or replace it) to use `TfidfVectorizer` from Scikit-learn for semantic similarity and keyword extraction.
- Implement an optimized "Semantic Score" based on Jaccard/Cosine similarity of TF-IDF vectors.
- Verify: Analysis runs in < 2 seconds on a CPU-only environment.

### 1.3 Harden PDF/DOCX Parsing
- Ensure `core/pdf_processor.py` is robust without OCR. Add meaningful error messages if a PDF is purely image-based.
- Implement better multi-column text reconstruction in `pdf_processor.py`.
- Verify: Papers with 2-column layouts parse correctly.

### 1.4 Persistent Storage & History
- Store uploaded papers in `research_papers/`.
- Ensure `paperiq.db` is correctly updated with relative file paths.
- Add a "Cleanup" script to remove old papers/DB entries to stay within storage limits (Optional).

---

---

## STAGE 2 — Advanced Heuristic Analysis (DONE)

### 2.1 Structured Reference Parser
- DONE: Regex-based bibliography parser in core/reference_parser.py.
- DONE: Identifies Author, Title, Year without using a model.

### 2.2 Paper & Methodology Classification
- DONE: Keyword-based classification implemented.

### 2.3 Comprehensive Section Extraction
- DONE: Enhanced section detection and element counting (Figures/Tables/Equations).

### 2.4 Conclusion-to-Abstract Alignment
- DONE: Jaccard similarity check between Abstract and Conclusion.

---

## STAGE 3 — Features & Export (DONE)

### 3.1 Batch Processing
- DONE: Asynchronous processing ready in core/async_processor.py.

### 3.2 Trend Dashboard
- DONE: Cross-paper analytics implemented in main.py.

### 3.3 Export Tools
- DONE: JSON and CSV export logic implemented.

---

## STAGE 4 — Smart Comparison & arXiv Integration (DONE)

### 4.1 Keyword Overlap & Shared Themes
- DONE: TF-IDF semantic overlap and Unique Concepts detection.

### 4.4 Seamless arXiv Integration
- DONE: One-click "Analyze & Save" for arXiv papers.
