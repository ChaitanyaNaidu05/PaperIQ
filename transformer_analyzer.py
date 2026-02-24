import logging
import numpy as np
from typing import List, Tuple, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from transformers import AutoTokenizer, AutoModel
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not installed. Using fallback methods.")

MODEL_NAME = "all-MiniLM-L6-v2"
_model = None
_tokenizer = None


def get_transformer_model():
    global _model
    if _model is None and TRANSFORMERS_AVAILABLE:
        try:
            _model = SentenceTransformer(MODEL_NAME)
            logger.info(f"Loaded SentenceTransformer model: {MODEL_NAME}")
        except Exception as e:
            logger.error(f"Failed to load transformer model: {e}")
    return _model


def get_tokenizer():
    global _tokenizer
    if _tokenizer is None and TRANSFORMERS_AVAILABLE:
        try:
            _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        except Exception as e:
            logger.error(f"Failed to load tokenizer: {e}")
    return _tokenizer


def extract_keywords_transformer(text: str, top_n: int = 15) -> List[Tuple[str, float]]:
    if not TRANSFORMERS_AVAILABLE:
        return []
    
    model = get_transformer_model()
    if model is None:
        return []
    
    try:
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if len(sentences) < 2:
            return []
        
        sentence_embeddings = model.encode(sentences, convert_to_numpy=True, show_progress_bar=False)
        
        doc_embedding = np.mean(sentence_embeddings, axis=0)
        
        from sklearn.feature_extraction.text import CountVectorizer
        vectorizer = CountVectorizer(stop_words='english', ngram_range=(1, 2), max_features=500)
        
        words = text.split()
        candidate_words = [w for w in set(words) if len(w) > 3 and w.isalpha()]
        
        if len(candidate_words) < top_n:
            return []
        
        word_embeddings = model.encode(candidate_words, convert_to_numpy=True, show_progress_bar=False)
        
        similarities = []
        for i, word in enumerate(candidate_words):
            sim = np.dot(word_embeddings[i], doc_embedding) / (
                np.linalg.norm(word_embeddings[i]) * np.linalg.norm(doc_embedding)
            )
            similarities.append((word, float(sim)))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_n]
    
    except Exception as e:
        logger.error(f"Error in transformer keyword extraction: {e}")
        return []


def compute_semantic_similarity(text1: str, text2: str) -> float:
    if not TRANSFORMERS_AVAILABLE:
        return 0.0
    
    model = get_transformer_model()
    if model is None:
        return 0.0
    
    try:
        embeddings = model.encode([text1, text2], convert_to_numpy=True, show_progress_bar=False)
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        return float(similarity)
    except Exception as e:
        logger.error(f"Error computing semantic similarity: {e}")
        return 0.0


def extractive_summarize_transformer(text: str, num_sentences: int = None) -> str:
    if not TRANSFORMERS_AVAILABLE:
        return ""
    
    model = get_transformer_model()
    if model is None:
        return ""
    
    try:
        from textblob import TextBlob
        blob = TextBlob(text)
        sentences = list(blob.sentences)
        
        if not sentences:
            return ""
        
        total_sents = len(sentences)
        if num_sentences is None:
            if total_sents <= 5:
                num_sentences = min(2, total_sents)
            elif total_sents <= 15:
                num_sentences = 4
            else:
                num_sentences = 6
        num_sentences = min(num_sentences, total_sents)
        
        sentence_texts = [s.raw for s in sentences]
        
        if len(sentence_texts) < 2:
            return sentence_texts[0] if sentence_texts else ""
        
        embeddings = model.encode(sentence_texts, convert_to_numpy=True, show_progress_bar=False)
        
        doc_embedding = np.mean(embeddings, axis=0)
        
        scored = []
        for i, (sent_text, embedding) in enumerate(zip(sentence_texts, embeddings)):
            similarity = np.dot(embedding, doc_embedding) / (
                np.linalg.norm(embedding) * np.linalg.norm(doc_embedding)
            )
            
            if i < 2:
                similarity *= 1.3
            elif i >= total_sents - 2:
                similarity *= 1.15
            
            scored.append((float(similarity), i, sent_text))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        selected = scored[:num_sentences]
        selected.sort(key=lambda x: x[1])
        
        return " ".join(s[2] for s in selected)
    
    except Exception as e:
        logger.error(f"Error in transformer summarization: {e}")
        return ""


def classify_domain_transformer(text: str) -> Tuple[str, Dict[str, int]]:
    if not TRANSFORMERS_AVAILABLE:
        return "General", {}
    
    model = get_transformer_model()
    if model is None:
        return "General", {}
    
    domains = [
        "Computer Science",
        "Biology Medicine",
        "Physics Engineering",
        "Economics Finance",
        "Mathematics Statistics",
    ]
    
    try:
        domain_embeddings = model.encode(domains, convert_to_numpy=True, show_progress_bar=False)
        
        sample_text = text[:2000]
        text_embedding = model.encode([sample_text], convert_to_numpy=True, show_progress_bar=False)[0]
        
        similarities = []
        for i, domain in enumerate(domains):
            sim = np.dot(text_embedding, domain_embeddings[i]) / (
                np.linalg.norm(text_embedding) * np.linalg.norm(domain_embeddings[i])
            )
            similarities.append((domain, float(sim)))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        domain_scores = {d: int(s * 100) for d, s in similarities}
        
        best_domain = similarities[0][0]
        if similarities[0][1] < 0.3:
            return "General / Interdisciplinary", domain_scores
        
        return best_domain, domain_scores
    
    except Exception as e:
        logger.error(f"Error in domain classification: {e}")
        return "General", {}


def compare_documents(texts: List[str], labels: List[str]) -> Dict:
    if not TRANSFORMERS_AVAILABLE or len(texts) < 2:
        return {}
    
    model = get_transformer_model()
    if model is None:
        return {}
    
    try:
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        
        n = len(texts)
        similarity_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                elif i < j:
                    sim = np.dot(embeddings[i], embeddings[j]) / (
                        np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
                    )
                    similarity_matrix[i][j] = sim
                    similarity_matrix[j][i] = sim
        
        avg_similarity = np.mean([similarity_matrix[i][j] for i in range(n) for j in range(i+1, n)])
        
        centroid = np.mean(embeddings, axis=0)
        distances_to_centroid = []
        for i, emb in enumerate(embeddings):
            dist = np.linalg.norm(emb - centroid)
            distances_to_centroid.append((labels[i], float(dist)))
        
        distances_to_centroid.sort(key=lambda x: x[1])
        
        most_central = distances_to_centroid[0][0] if distances_to_centroid else None
        
        return {
            "similarity_matrix": similarity_matrix.tolist(),
            "labels": labels,
            "average_similarity": float(avg_similarity),
            "distances_to_centroid": distances_to_centroid,
            "most_central_document": most_central,
        }
    
    except Exception as e:
        logger.error(f"Error in document comparison: {e}")
        return {}


def get_semantic_clusters(texts: List[str], labels: List[str], n_clusters: int = 3) -> Dict:
    if not TRANSFORMERS_AVAILABLE or len(texts) < n_clusters:
        return {}
    
    model = get_transformer_model()
    if model is None:
        return {}
    
    try:
        from sklearn.cluster import KMeans
        
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        
        kmeans = KMeans(n_clusters=min(n_clusters, len(texts)), random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)
        
        clusters = {}
        for i, label in enumerate(labels):
            cluster_id = int(cluster_labels[i])
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(label)
        
        return {
            "clusters": clusters,
            "cluster_labels": cluster_labels.tolist(),
            "n_clusters": len(clusters),
        }
    
    except Exception as e:
        logger.error(f"Error in semantic clustering: {e}")
        return {}
