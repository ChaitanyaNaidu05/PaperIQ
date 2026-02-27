FROM python:3.11-slim

WORKDIR /app

ENV NLTK_DATA=/usr/local/nltk_data

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /usr/local/nltk_data
RUN python -c "import nltk; [nltk.download(p, download_dir='/usr/local/nltk_data') for p in ['punkt', 'punkt_tab', 'averaged_perceptron_tagger', 'stopwords', 'wordnet']]"

RUN python -m textblob.download_corpora

RUN mkdir -p /app/data

# Render provides $PORT at runtime, so we use it here.
CMD streamlit run app/main.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
