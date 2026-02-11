# PaperIQ Project Explanation

## 1. Project Overview
PaperIQ is an offline-capable, secure research paper analysis tool built with Python and Streamlit. It allows users to upload PDF research papers, automatically detects document structure (sections like Abstract, Methodology, Results), extracts keywords, and maintains a secure, private history of all analyses.

## 2. Key Features
- **Offline & Private**: Runs locally with no cloud dependencies.
- **Secure Authentication**: Built-in Signup and Login system with password encryption.
- **Dynamic Analysis**: Automatically identifies sections and keywords from unstructured PDF text.
- **History Tracking**: Saves every analysis so users can revisit past papers without re-uploading.
- **Interactive Dashboard**: Clean, modern UI for viewing reports.

## 3. Technical Architecture (Modular Design)

The project is structured into **6 key modules** to ensure maintainability and separation of concerns:

### 📄 `paper_iq_app.py` (The Controller)
- **Role**: The main entry point.
- **Function**: Manages the "Page Routing" (switching between Login, Signup, and Dashboard).
- **Logic**: Connects the User Interface (UI) with the backend logic.

### 🗄️ `database.py` (The Storage)
- **Role**: Manages the SQLite database (`paperiq.db`).
- **Function**:
  - Creates tables for `Users` and `AnalysisHistory`.
  - Handles saving new users and retrieving login details.
  - Saves analysis reports and retrieves user history.
- **Why SQLite?**: It's serverless, needs no configuration, and is perfect for offline apps.

### 🔐 `auth.py` (The Security)
- **Role**: Handles user capability.
- **Function**:
  - `hash_password()`: Converts plain passwords into secure hashes using SHA-256 + Salt.
  - `verify_password()`: Checks if the entered password matches the stored hash.
- **Security Note**: We never store actual passwords, only their cryptographic footprints.

### 📝 `pdf_processor.py` (The Extractor)
- **Role**: Handles raw file processing.
- **Function**: Uses `pdfplumber` to read PDF files and extract raw text strings, cleaning up whitespace and formatting issues.

### 🧠 `text_analyzer.py` (The Brain)
- **Role**: Intelligent text analysis.
- **Function**:
  - `detect_section_headers()`: Uses Regex and logic to find "Introduction", "Methods", etc.
  - `identify_sections_dynamic()`: Splits the text based on found headers.
  - `extract_keywords()`: Finds the most relevant topics in each section.

### 🎨 `styles.py` (The Look)
- **Role**: UI Customization.
- **Function**: Contains all CSS styles to make the app look modern and professional, keeping the main code clean.

## 4. User Flow

1. **Start**: User opens app.
2. **Auth**:
   - If new, user goes to **Signup** -> Creates account (saved to DB).
   - If existing, user goes to **Login** -> Auth checks DB -> Access granted.
3. **Dashboard**:
   - **Sidebar**: Shows "New Analysis" button and list of past papers.
   - **Main Area**: Upload PDF.
4. **Processing**:
   - App extracts text -> Identifies Sections -> Saves to History.
5. **Result**: User explores the structured summary and keywords.

## 5. How to Run
```bash
# 1. Activate virtual environment (if used)
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run paper_iq_app.py
```
