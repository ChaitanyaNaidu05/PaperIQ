import logging
import numpy as np
import re
from typing import List, Tuple, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TRANSFORMERS_AVAILABLE = True


def get_transformer_model():
    return None


def get_tokenizer():
    return None


def extract_keywords_transformer(text: str, top_n: int = 15) -> List[Tuple[str, float]]:
    try:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=1000)
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]
        
        keywords = []
        for i, score in enumerate(scores):
            if score > 0:
                keywords.append((feature_names[i], float(score)))
                
        keywords.sort(key=lambda x: x[1], reverse=True)
        return keywords[:top_n]
    except Exception as e:
        logger.error(f"Error in TF-IDF keyword extraction: {e}")
        return []


def compute_semantic_similarity(text1: str, text2: str) -> float:
    try:
        if not text1.strip() or not text2.strip():
            return 0.0
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf = vectorizer.fit_transform([text1, text2])
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])
        return float(sim[0][0])
    except Exception as e:
        logger.error(f"Error computing TF-IDF similarity: {e}")
        return 0.0


def extractive_summarize_transformer(text: str, num_sentences: int = None) -> str:
    try:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if not sentences:
            return ""
            
        if num_sentences is None:
            num_sentences = min(5, max(2, len(sentences) // 10))
            
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(sentences)
        
        doc_vector = np.asarray(tfidf_matrix.mean(axis=0))
        
        scores = []
        for i, sent_vec in enumerate(tfidf_matrix):
            sim = cosine_similarity(sent_vec, doc_vector)[0][0]
            scores.append((sim, i, sentences[i]))
            
        scores.sort(key=lambda x: x[0], reverse=True)
        top_sentences = sorted(scores[:num_sentences], key=lambda x: x[1])
        
        return " ".join([s[2] for s in top_sentences])
    except Exception as e:
        logger.error(f"Error in TF-IDF summarization: {e}")
        return ""


def classify_domain_transformer(text: str) -> Tuple[str, Dict[str, int]]:
    domain_keywords = {
        "Computer Science": ["algorithm", "software", "network", "data", "computing", "programming", "artificial intelligence", "machine learning", "neural", "compiler", "database"],
        "Biology / Medicine": ["cell", "protein", "gene", "disease", "clinical", "patient", "dna", "medical", "health", "biological", "molecular"],
        "Physics / Engineering": ["matter", "energy", "quantum", "mechanical", "electrical", "force", "fluid", "material", "structural", "wave", "thermodynamics"],
        "Economics / Finance": ["market", "economic", "financial", "investment", "capital", "trade", "policy", "currency", "revenue", "fiscal", "inflation"],
        "Mathematics / Statistics": ["theorem", "proof", "statistical", "probability", "matrix", "equation", "calculus", "regression", "variable", "random", "discrete"]
    }
    
    text_lower = text.lower()
    scores = {}
    
    for domain, keywords in domain_keywords.items():
        score = 0
        for kw in keywords:
            score += text_lower.count(kw)
        scores[domain] = score
        
    total = sum(scores.values()) or 1
    normalized_scores = {d: int((s / total) * 100) for d, s in scores.items()}
    
    best_domain = max(scores, key=scores.get)
    if scores[best_domain] == 0:
        return "General", {d: 0 for d in domain_keywords}
        
    return best_domain, normalized_scores


def compare_documents(texts: List[str], labels: List[str]) -> Dict:
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(texts)
        sim_matrix = cosine_similarity(tfidf_matrix)
        
        return {
            "similarity_matrix": sim_matrix.tolist(),
            "labels": labels,
            "average_similarity": float(np.mean(sim_matrix[np.triu_indices(len(texts), k=1)])),
            "most_central_document": labels[np.argmax(np.mean(sim_matrix, axis=1))]
        }
    except Exception as e:
        logger.error(f"Error in TF-IDF document comparison: {e}")
        return {}


def get_semantic_clusters(texts: List[str], labels: List[str], n_clusters: int = 3) -> Dict:
    try:
        from sklearn.cluster import KMeans
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        n_clusters = min(n_clusters, len(texts))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=5)
        cluster_labels = kmeans.fit_predict(tfidf_matrix)
        
        clusters = {}
        for i, cluster_id in enumerate(cluster_labels):
            cid = int(cluster_id)
            if cid not in clusters:
                clusters[cid] = []
            clusters[cid].append(labels[i])
            
        return {
            "clusters": clusters,
            "cluster_labels": cluster_labels.tolist()
        }
    except Exception as e:
        logger.error(f"Error in TF-IDF clustering: {e}")
        return {}
