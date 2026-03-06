# PaperIQ - Intelligent Document Analysis Platform

PaperIQ is a comprehensive, Streamlit-based web application designed to help researchers, students, and professionals analyze, compare, and extract deep insights from academic papers and documents. It leverages Natural Language Processing (NLP) and Machine Learning techniques to provide structural analysis, writing quality assessment, citation analysis, and much more.

## Key Features

- **Deep Text Analysis**: Evaluates readability, coherence, reasoning strength, writing clarity, and vocabulary richness.
- **Advanced Intelligence Metrics**:
  - **Quality & Acceptance Prediction**: Estimates the quality score and likely acceptance percentile.
  - **Ethics & Rigor**: Checks for ethical compliance and statistical rigor.
  - **Reproducibility**: Evaluates if the research contains enough details (methods, code, data) to be reproduced.
- **Structural Analysis**: Detects missing sections (Abstract, Introduction, Methods, Results, Conclusion) and novelty indicators (e.g., "we propose").
- **Entity & Trend Extraction**: Automatically extracts mentioned methods, software, datasets, and institutions. Identifies emerging trends and future research directions.
- **Plagiarism Detection**: Analyzes the document for self-similarity, paraphrasing, and potential plagiarism.
- **Document Comparison**: Compare multiple documents side-by-side to understand their differences and similarities.
- **arXiv Integration**: Directly fetch and analyze papers from the arXiv repository.
- **Rich Visualizations**: Interactive radar charts, sentiment gauges, and statistics dashboards using Plotly.
- **Export Options**: Export analysis reports in PDF, JSON, CSV, LaTeX, or DOCX formats.
- **User Authentication & History**: Secure login/signup system. Saves your analysis history so you can pick up where you left off.

## Tech Stack

- **Frontend / App Framework**: [Streamlit](https://streamlit.io/)
- **Data Visualization**: [Plotly](https://plotly.com/)
- **NLP & Text Processing**: NLTK, TextBlob
- **Data Science/ML**: Pandas, NumPy, Scikit-learn
- **Document Parsing**: pdfplumber, python-docx
- **Authentication**: bcrypt
- **Database**: SQLite (built-in)

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd PaperIQ
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   *Note: Depending on your exact environment and NLTK usage, you may need to download NLTK data (e.g., `nltk.download('punkt')`, `nltk.download('stopwords')`). The application will typically handle this or prompt you if missing.*

4. **Run the application:**
   ```bash
   streamlit run app/main.py
   ```

5. **Access the application:**
   Open your browser and navigate to `http://localhost:8501`.

## Docker Support

PaperIQ also includes a `Dockerfile` and `docker-compose.yml` for easy containerized deployment.

```bash
docker-compose up --build
```

## Project Structure

- `app/`: Contains the main Streamlit application logic (`main.py`) and UI styling (`styles.py`).
- `core/`: Houses the core logic for database integration, authentication, pdf parsing, text analysis, multidoc analysis, and arXiv fetching.
- `data/`: Directory for storing local SQLite database and user data.
- `requirements.txt`: Python package dependencies.

## Usage Guide
1. **Sign Up / Login**: Create an account to start using the platform and keep a history of your analyses.
2. **Dashboard**: From the sidebar, select "New Analysis" to upload a document, or view your previous uploads.
3. **Analyze**: Once a document is processed, navigate through the tabs (Radar & Scores, Statistics, Structure, Advanced Analysis, Entities, etc.) to review the findings.
4. **Compare**: Use the "Compare Documents" tool in the sidebar to benchmark multiple papers against each other.
