FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True); nltk.download('stopwords', quiet=True)"

RUN python -c "from textblob import TextBlob; TextBlob('test').download_corpora()"

RUN mkdir -p /app/data

# Render provides $PORT at runtime, so we use it here.
CMD streamlit run app/main.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
