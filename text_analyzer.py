import re
import math
import numpy as np
import heapq
import nltk
import datetime
from collections import Counter
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import plotly.graph_objects as go
from fpdf import FPDF

for _corpus in ('punkt', 'punkt_tab', 'averaged_perceptron_tagger', 'stopwords'):
    nltk.download(_corpus, quiet=True)

from nltk.corpus import stopwords

STOP_WORDS = set(stopwords.words('english'))

CANONICAL_SECTIONS = [
    "Abstract", "Introduction", "Literature Review", "Related Work",
    "Methodology", "Methods", "Experiment", "Results",
    "Discussion", "Conclusion", "References"
]

DOMAIN_KEYWORDS = {
    "Computer Science": [
        "algorithm", "neural", "network", "machine learning", "deep learning",
        "dataset", "transformer", "convolutional", "gpu", "training",
        "inference", "classification", "regression", "software", "compiler",
        "api", "database", "optimization", "benchmark", "backpropagation"
    ],
    "Biology / Medicine": [
        "protein", "gene", "cell", "dna", "rna", "enzyme", "clinical",
        "patient", "therapy", "diagnosis", "pathology", "mutation",
        "genome", "biomarker", "antibody", "tissue", "organism", "species"
    ],
    "Physics": [
        "quantum", "entropy", "particle", "photon", "wave", "field",
        "energy", "mass", "velocity", "momentum", "thermodynamic",
        "relativity", "boson", "fermion", "tensor", "hamiltonian"
    ],
    "Economics / Finance": [
        "market", "gdp", "inflation", "fiscal", "monetary", "equilibrium",
        "demand", "supply", "trade", "portfolio", "regression", "econometric",
        "interest rate", "capital", "welfare", "utility"
    ],
    "Mathematics / Statistics": [
        "theorem", "proof", "lemma", "hypothesis", "variance", "distribution",
        "integral", "derivative", "convergence", "matrix", "eigenvalue",
        "stochastic", "probability", "bayesian", "estimator"
    ],
}

def extract_sections(text):
    """Extract sections with improved boundary detection."""
    lines = text.split('\n')
    sections = {}
    current_header = "Introduction / Preamble"
    current_content = []

    common_headers_lower = {h.lower() for h in CANONICAL_SECTIONS}
    common_headers_lower.update([
        "background", "framework", "approach", "implementation",
        "evaluation", "future work", "acknowledgments", "appendix"
    ])

    for line in lines:
        line = line.strip()
        if not line:
            continue
        is_header = False

        if re.match(r'^\d+(\.\d+)*\.?\s+[A-Za-z]', line) and len(line) < 80:
            is_header = True

        elif line.isupper() and 3 < len(line) < 50:
            is_header = True

        elif line.lower().rstrip(':') in common_headers_lower:
            is_header = True

        elif re.match(r'^[IVXLC]+\.?\s+[A-Za-z]', line) and len(line) < 60:
            is_header = True

        if is_header:
            if current_content:
                sections[current_header] = "\n".join(current_content)
            current_header = line
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        sections[current_header] = "\n".join(current_content)

    return sections

def _count_syllables(word):
    """Estimate syllable count using vowel groups."""
    word = word.lower().rstrip('e')
    vowels = re.findall(r'[aeiouy]+', word)
    count = len(vowels)
    return max(1, count)

def calculate_readability(text):
    """Flesch Reading Ease with proper syllable counting."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences)
    words = text.split()
    word_count = len(words)
    if sentence_count == 0 or word_count == 0:
        return 0
    total_syllables = sum(_count_syllables(w) for w in words)
    score = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (total_syllables / word_count)
    return max(0, min(100, round(score, 2)))

def calculate_citation_density(text):
    """Count citation patterns per 1000 words."""
    word_count = len(text.split())
    if word_count == 0:
        return 0.0, 0

    bracket_cites = len(re.findall(r'\[\d+(?:[,;\s]+\d+)*\]', text))
    author_cites = len(re.findall(r'\([A-Z][a-z]+(?:\s+(?:and|&)\s+[A-Z][a-z]+)*,?\s*\d{4}\)', text))
    etal_cites = len(re.findall(r'et\s+al\.', text, re.IGNORECASE))
    total_cites = bracket_cites + author_cites + etal_cites
    density = round((total_cites / word_count) * 1000, 2)
    return density, total_cites

def calculate_technical_depth(text, words):
    """Score technical depth based on long domain words and math tokens."""
    word_count = len(words)
    if word_count == 0:
        return 0.0

    domain_words = [w for w in words if len(w) > 8 and w.lower() not in STOP_WORDS]
    domain_ratio = len(domain_words) / word_count

    math_tokens = len(re.findall(r'[=∑∏∫α-ωΑ-Ω±≈≠≤≥∞√∂∇⊕⊗∈∉⊂⊃∀∃]', text))
    formula_patterns = len(re.findall(r'\b\w+\s*[=<>≈]\s*\w+', text))
    math_signal = min(1.0, (math_tokens + formula_patterns) / max(1, word_count) * 50)

    score = min(100, (domain_ratio * 200) + (math_signal * 40) + 15)
    return round(score, 2)

def calculate_novelty_signal(text):
    """Detect phrases indicating novel contributions."""
    novelty_phrases = [
        r'\bwe propose\b', r'\bwe introduce\b', r'\bnovel\b', r'\bfirst\b',
        r'\boutperforms?\b', r'\bstate[- ]of[- ]the[- ]art\b', r'\bnew approach\b',
        r'\bour method\b', r'\bcontribution\b', r'\bunprecedented\b',
        r'\bsuperior\b', r'\bimproved?\b', r'\badvance[sd]?\b',
        r'\bbreakthrough\b', r'\binnovative\b', r'\bour framework\b'
    ]
    text_lower = text.lower()
    total_matches = sum(len(re.findall(p, text_lower)) for p in novelty_phrases)
    word_count = len(text.split())
    if word_count == 0:
        return 0.0, total_matches
    density = (total_matches / word_count) * 1000
    score = min(100, density * 12 + 10)
    return round(score, 2), total_matches

def calculate_structural_completeness(sections):
    """Check which canonical sections are present."""
    found = []
    missing = []
    section_names_lower = [s.lower() for s in sections.keys()]

    for canonical in CANONICAL_SECTIONS:
        canonical_lower = canonical.lower()
        matched = any(canonical_lower in sn for sn in section_names_lower)
        if matched:
            found.append(canonical)
        else:
            missing.append(canonical)

    score = round((len(found) / len(CANONICAL_SECTIONS)) * 100, 2)
    return score, found, missing

def calculate_vocabulary_richness(words):
    """Type-Token Ratio and Hapax Legomena ratio."""
    if not words:
        return 0.0, 0.0
    lower_words = [w.lower() for w in words if w.lower() not in STOP_WORDS and len(w) > 2]
    if not lower_words:
        return 0.0, 0.0
    total = len(lower_words)
    unique = len(set(lower_words))
    ttr = unique / total

    freq = Counter(lower_words)
    hapax = sum(1 for count in freq.values() if count == 1)
    hapax_ratio = hapax / total

    score = min(100, (ttr * 60 + hapax_ratio * 40) * 100)
    return round(score, 2), round(ttr, 4)

def classify_sentence_complexity(sentences):
    """Bucket sentences into simple/medium/complex by word count."""
    simple = 0
    medium = 0
    complex_count = 0
    for s in sentences:
        wc = len(s.words)
        if wc <= 12:
            simple += 1
        elif wc <= 25:
            medium += 1
        else:
            complex_count += 1
    total = simple + medium + complex_count
    if total == 0:
        return {"simple": 0, "medium": 0, "complex": 0,
                "simple_pct": 0, "medium_pct": 0, "complex_pct": 0}
    return {
        "simple": simple, "medium": medium, "complex": complex_count,
        "simple_pct": round(simple / total * 100, 1),
        "medium_pct": round(medium / total * 100, 1),
        "complex_pct": round(complex_count / total * 100, 1),
    }

def detect_domain(text):
    """Heuristic domain classification using keyword banks."""
    text_lower = text.lower()
    domain_scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(text_lower.count(kw) for kw in keywords)
        domain_scores[domain] = score
    best = max(domain_scores, key=domain_scores.get)
    if domain_scores[best] < 3:
        return "General / Interdisciplinary", domain_scores
    return best, domain_scores


def detect_domain_enhanced(text):
    """Enhanced domain classification using transformers if available."""
    try:
        import transformer_analyzer
        if transformer_analyzer.TRANSFORMERS_AVAILABLE:
            domain, scores = transformer_analyzer.classify_domain_transformer(text)
            if domain != "General":
                return domain, scores
    except Exception:
        pass
    return detect_domain(text)

def extract_keywords_tfidf(text, top_n=15):
    """Extract top keywords using TF-IDF on sentence-level documents."""
    sentences = re.split(r'[.!?]\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    if len(sentences) < 2:
        return []
    try:
        vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.85
        )
        tfidf_matrix = vectorizer.fit_transform(sentences)
        feature_names = vectorizer.get_feature_names_out()
        avg_scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
        top_indices = avg_scores.argsort()[-top_n:][::-1]
        keywords = [(feature_names[i], round(avg_scores[i], 4)) for i in top_indices]
        return keywords
    except Exception:
        return []


def extract_keywords_enhanced(text, top_n=15):
    """Extract keywords using transformers if available, fallback to TF-IDF."""
    try:
        import transformer_analyzer
        if transformer_analyzer.TRANSFORMERS_AVAILABLE:
            keywords = transformer_analyzer.extract_keywords_transformer(text, top_n)
            if keywords:
                return keywords
    except Exception:
        pass
    return extract_keywords_tfidf(text, top_n)

def extractive_summarize(text, num_sentences=None):
    """
    Improved extractive summarization with:
    - Stop-word filtered TF-IDF scoring
    - Positional bias (first and last sentences boosted)
    - Cosine similarity deduplication
    - Adaptive sentence count based on text length
    """
    blob = TextBlob(text)
    sentences = blob.sentences
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

    content_words = [w.lower() for w in re.findall(r'\b[a-z]{3,}\b', text.lower())
                     if w.lower() not in STOP_WORDS]
    if not content_words:
        return sentences[0].raw

    freq = Counter(content_words)
    max_freq = max(freq.values())
    for w in freq:
        freq[w] = freq[w] / max_freq

    scored = []
    for i, sentence in enumerate(sentences):
        words_in_sent = [w.lower() for w in sentence.words if w.lower() not in STOP_WORDS]
        word_score = sum(freq.get(w, 0) for w in words_in_sent)

        if len(words_in_sent) > 0:
            word_score /= len(words_in_sent)

        if i < 2:
            word_score *= 1.3
        elif i >= total_sents - 2:
            word_score *= 1.15

        scored.append((word_score, i, sentence.raw))

    candidates = heapq.nlargest(num_sentences * 2, scored, key=lambda x: x[0])

    selected = []
    for score, idx, raw in candidates:
        if len(selected) >= num_sentences:
            break

        is_duplicate = False
        for _, _, existing_raw in selected:
            similarity = _sentence_similarity(raw, existing_raw)
            if similarity > 0.6:
                is_duplicate = True
                break
        if not is_duplicate:
            selected.append((score, idx, raw))

    selected.sort(key=lambda x: x[1])
    return " ".join(s[2] for s in selected)


def extractive_summarize_enhanced(text, num_sentences=None):
    """Enhanced summarization using transformers if available, fallback to TF-IDF."""
    try:
        import transformer_analyzer
        if transformer_analyzer.TRANSFORMERS_AVAILABLE:
            summary = transformer_analyzer.extractive_summarize_transformer(text, num_sentences)
            if summary:
                return summary
    except Exception:
        pass
    return extractive_summarize(text, num_sentences)

def _sentence_similarity(s1, s2):
    """Quick cosine similarity between two sentences based on word overlap."""
    words1 = set(w.lower() for w in s1.split() if w.lower() not in STOP_WORDS)
    words2 = set(w.lower() for w in s2.split() if w.lower() not in STOP_WORDS)
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union)

def analyze_full_document(text):
    """Comprehensive analysis with original + new metrics."""
    blob = TextBlob(text)
    sentences = blob.sentences
    words = blob.words
    word_count = len(words)
    sentence_count = len(sentences)
    if sentence_count == 0:
        return None

    avg_sentence_len = np.mean([len(s.words) for s in sentences])
    avg_word_len = np.mean([len(w) for w in words])
    sentiment = blob.sentiment.polarity

    language_score = min(100, (avg_sentence_len * 1.5) + (avg_word_len * 5) + (50 + sentiment * 20))
    language_score = round(max(0, language_score), 2)

    transitions = ["however", "therefore", "thus", "consequently", "furthermore",
                    "meanwhile", "moreover", "nevertheless", "additionally", "subsequently"]
    transition_count = sum(text.lower().count(t) for t in transitions)
    coherence_score = round(min(100, (transition_count * 3.5) + (sentence_count * 0.08) + 35), 2)

    reasoning_keywords = ["because", "since", "implies", "due to", "as a result",
                          "evidence", "suggests", "indicates", "demonstrates", "shows that"]
    reasoning_count = sum(text.lower().count(k) for k in reasoning_keywords)
    reasoning_score = round(min(100, (reasoning_count * 5) + 25), 2)

    complex_words = [w for w in words if len(w) > 6]
    sophistication_score = round(min(100, (len(complex_words) / word_count) * 300) if word_count else 0, 2)

    readability_score = calculate_readability(text)

    sections = extract_sections(text)
    citation_density, total_citations = calculate_citation_density(text)
    citation_score = round(min(100, citation_density * 8 + 10), 2)

    technical_depth_score = calculate_technical_depth(text, words)
    novelty_score, novelty_matches = calculate_novelty_signal(text)
    structural_score, found_sections, missing_sections = calculate_structural_completeness(sections)
    vocab_score, ttr = calculate_vocabulary_richness(words)
    sentence_complexity = classify_sentence_complexity(sentences)
    domain, domain_scores = detect_domain_enhanced(text)
    keywords = extract_keywords_enhanced(text)

    document_summary = extractive_summarize_enhanced(text)

    final_score = round(
        (language_score * 0.15) +
        (coherence_score * 0.12) +
        (reasoning_score * 0.12) +
        (sophistication_score * 0.10) +
        (readability_score * 0.10) +
        (citation_score * 0.10) +
        (technical_depth_score * 0.08) +
        (novelty_score * 0.08) +
        (structural_score * 0.08) +
        (vocab_score * 0.07)
    , 2)

    scores = {
        "Language": float(language_score),
        "Coherence": float(coherence_score),
        "Reasoning": float(reasoning_score),
        "Sophistication": float(sophistication_score),
        "Readability": float(readability_score),
        "Citation Density": float(citation_score),
        "Technical Depth": float(technical_depth_score),
        "Novelty Signal": float(novelty_score),
        "Structural Completeness": float(structural_score),
        "Vocabulary Richness": float(vocab_score),
        "Composite": float(final_score),
    }

    stats = {
        "word_count": int(word_count),
        "sentence_count": int(sentence_count),
        "avg_sentence_len": float(round(avg_sentence_len, 2)),
        "avg_word_len": float(round(avg_word_len, 2)),
        "complex_word_ratio": float(round(len(complex_words) / word_count, 2)) if word_count > 0 else 0.0,
        "total_citations": int(total_citations),
        "citation_density_per_1k": float(citation_density),
        "type_token_ratio": float(ttr),
        "novelty_phrases_found": int(novelty_matches),
        "transition_words_found": int(transition_count),
        "reasoning_indicators": int(reasoning_count),
    }

    return {
        "scores": scores,
        "stats": stats,
        "sentiment": float(round(sentiment, 2)),
        "issues": [s.raw for s in sentences if len(s.words) > 30],
        "document_summary": document_summary,
        "sentence_complexity": {
            "simple": int(sentence_complexity["simple"]),
            "medium": int(sentence_complexity["medium"]),
            "complex": int(sentence_complexity["complex"]),
            "simple_pct": float(sentence_complexity["simple_pct"]),
            "medium_pct": float(sentence_complexity["medium_pct"]),
            "complex_pct": float(sentence_complexity["complex_pct"]),
        },
        "domain": domain,
        "domain_scores": {k: int(v) for k, v in domain_scores.items()},
        "keywords": [(str(kw), float(score)) for kw, score in keywords],
        "structural_found": found_sections,
        "structural_missing": missing_sections,
        "entities": extract_entities_for_analysis(text),
        "advanced": extract_advanced_analysis(text, sections, scores, stats),
    }


def extract_entities_for_analysis(text: str) -> dict:
    try:
        import ner_extractor
        entity_data = ner_extractor.analyze_entities_full(text)
        return {
            "summary": entity_data.get("entities", {}),
            "authors": entity_data.get("authors", []),
            "research_questions": entity_data.get("research_questions", []),
            "contributions": entity_data.get("contributions", []),
            "counts": entity_data.get("entity_counts", {}),
        }
    except Exception as e:
        return {
            "summary": {},
            "authors": [],
            "research_questions": [],
            "contributions": [],
            "counts": {},
        }


def extract_advanced_analysis(text: str, sections: dict, scores: dict, stats: dict) -> dict:
    try:
        import advanced_ml
        advanced_data = advanced_ml.run_advanced_analysis(text, sections, scores, stats)
        return advanced_data
    except Exception as e:
        return {
            "quality_prediction": {},
            "acceptance_probability": {},
            "writing_quality": {},
            "reproducibility": {},
            "ethical_compliance": {},
            "statistical_rigor": {},
        }


def analyze_section(text, section_name):
    if not text or len(text.strip()) < 50:
        return {
            "section": section_name,
            "word_count": 0,
            "score": 0,
            "has_research_question": False,
            "has_methodology": False,
            "has_results": False,
            "clarity_score": 0,
        }

    blob = TextBlob(text)
    sentences = blob.sentences
    words = blob.words
    word_count = len(words)
    sentence_count = len(sentences)

    if sentence_count == 0 or word_count == 0:
        return {
            "section": section_name,
            "word_count": 0,
            "score": 0,
            "has_research_question": False,
            "has_methodology": False,
            "has_results": False,
            "clarity_score": 0,
        }

    avg_sentence_len = len(words) / sentence_count
    complex_words = [w for w in words if len(w) > 6]
    complex_ratio = len(complex_words) / word_count if word_count > 0 else 0

    readability = calculate_readability(text)

    transitions = ["however", "therefore", "thus", "consequently", "furthermore",
                   "meanwhile", "moreover", "nevertheless", "additionally", "subsequently"]
    transition_count = sum(text.lower().count(t) for t in transitions)

    section_lower = section_name.lower()
    has_research_question = any(q in text.lower() for q in ["research question", "hypothesis", 
                                "we investigate", "we examine", "this study asks"])
    has_methodology = any(m in text.lower() for m in ["method", "approach", "algorithm", 
                           "procedure", "dataset", "experiment", "implementation"])
    has_results = any(r in text.lower() for r in ["result", "performance", "accuracy", 
                       "achieved", "outperforms", "experimental", "evaluation"])

    section_score = 0
    if "abstract" in section_lower:
        section_score = min(100, readability * 0.4 + (transition_count * 2) + 
                           (10 if has_research_question else 0) + 30)
    elif "introduction" in section_lower:
        section_score = min(100, readability * 0.3 + (transition_count * 2) + 
                           (20 if has_research_question else 0) + 25)
    elif "method" in section_lower or "approach" in section_lower:
        section_score = min(100, readability * 0.3 + (transition_count * 2) + 
                           (25 if has_methodology else 0) + 25)
    elif "result" in section_lower or "experiment" in section_lower:
        section_score = min(100, readability * 0.3 + (transition_count * 2) + 
                           (25 if has_results else 0) + 25)
    elif "conclusion" in section_lower:
        section_score = min(100, readability * 0.4 + (transition_count * 2) + 
                           (15 if has_research_question else 0) + 25)
    else:
        section_score = min(100, readability * 0.4 + (transition_count * 2) + 30)

    clarity_score = max(0, min(100, 100 - (complex_ratio * 100) + (readability * 0.3)))

    return {
        "section": section_name,
        "word_count": int(word_count),
        "sentence_count": int(sentence_count),
        "avg_sentence_length": float(round(avg_sentence_len, 2)),
        "readability": float(round(readability, 2)),
        "score": float(round(section_score, 2)),
        "clarity_score": float(round(clarity_score, 2)),
        "has_research_question": has_research_question,
        "has_methodology": has_methodology,
        "has_results": has_results,
        "complex_word_ratio": float(round(complex_ratio, 4)),
    }


def analyze_sections_full(sections):
    section_scores = []
    for section_name, content in sections.items():
        if isinstance(content, dict):
            content = content.get("content", "")
        score_data = analyze_section(content, section_name)
        section_scores.append(score_data)
    return section_scores


def build_radar_chart(scores):
    """10-axis radar chart for all metrics."""
    categories = [k for k in scores if k != "Composite"]
    values = [scores[c] for c in categories]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(99,110,250,0.25)',
        line=dict(color='#636EFA', width=2),
        name='Scores'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10)),
            angularaxis=dict(tickfont=dict(size=11))
        ),
        showlegend=False,
        margin=dict(l=60, r=60, t=40, b=40),
        height=450,
    )
    return fig

def build_bar_chart(stats):
    """Horizontal bar chart for document stats."""
    display_stats = {
        "Word Count": stats["word_count"],
        "Sentence Count": stats["sentence_count"],
        "Avg Sentence Length": stats["avg_sentence_len"],
        "Avg Word Length": stats["avg_word_len"],
        "Total Citations": stats.get("total_citations", 0),
        "Transition Words": stats.get("transition_words_found", 0),
        "Reasoning Indicators": stats.get("reasoning_indicators", 0),
    }
    labels = list(display_stats.keys())
    values = list(display_stats.values())
    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692']
    fig = go.Figure([go.Bar(
        y=labels, x=values,
        orientation='h',
        marker_color=colors[:len(labels)],
        text=[str(v) for v in values],
        textposition='auto'
    )])
    fig.update_layout(
        xaxis_title="Value",
        margin=dict(l=10, r=20, t=20, b=30),
        height=350,
    )
    return fig

def build_sentiment_gauge(sentiment_score):
    color = '#2ecc71' if sentiment_score >= 0 else '#e74c3c'
    fig = go.Figure(go.Indicator(
        mode='gauge+number+delta',
        value=round(sentiment_score, 3),
        delta={'reference': 0, 'increasing': {'color': '#2ecc71'}, 'decreasing': {'color': '#e74c3c'}},
        title={'text': 'Sentiment Polarity', 'font': {'size': 16}},
        gauge={
            'axis': {'range': [-1, 1], 'tickwidth': 1},
            'bar': {'color': color},
            'steps': [
                {'range': [-1, -0.33], 'color': '#fadbd8'},
                {'range': [-0.33, 0.33], 'color': '#fef9e7'},
                {'range': [0.33, 1], 'color': '#d5f5e3'},
            ],
            'threshold': {'line': {'color': 'black', 'width': 3}, 'thickness': 0.75, 'value': sentiment_score}
        }
    ))
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def build_complexity_pie(sentence_complexity):
    """Pie chart showing sentence complexity distribution."""
    labels = ['Simple (≤12 words)', 'Medium (13-25 words)', 'Complex (>25 words)']
    values = [sentence_complexity['simple'], sentence_complexity['medium'], sentence_complexity['complex']]
    colors = ['#2ecc71', '#f39c12', '#e74c3c']
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        textinfo='percent+value',
        textfont=dict(size=13),
        hole=0.4,
    ))
    fig.update_layout(
        height=320,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5, font=dict(size=11))
    )
    return fig

def build_domain_bar(domain_scores):
    """Horizontal bar chart of domain keyword matches."""
    domains = list(domain_scores.keys())
    scores = list(domain_scores.values())
    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']
    fig = go.Figure(go.Bar(
        y=domains, x=scores,
        orientation='h',
        marker_color=colors[:len(domains)],
        text=[str(s) for s in scores],
        textposition='auto'
    ))
    fig.update_layout(
        xaxis_title="Keyword Matches",
        height=280,
        margin=dict(l=10, r=20, t=20, b=30),
    )
    return fig

def create_pdf_report(filename, data, section_scores=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(30, 58, 138)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 15, txt="PaperIQ Analysis Report", ln=1, align='C', fill=1)
    pdf.ln(5)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 11)
    safe_filename = filename.encode('latin-1', errors='ignore').decode('latin-1')
    pdf.cell(0, 8, txt=f"File: {safe_filename}", ln=1, align='C')
    pdf.cell(0, 6, txt=f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=1, align='C')
    pdf.ln(8)

    pdf.set_fill_color(239, 246, 255)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 12, txt="Overall Assessment", ln=1, fill=1)
    pdf.ln(3)
    
    composite = data['scores'].get('Composite', 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, txt=f"Composite Score: {composite}/100", ln=1)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Metric Scores:", ln=1)
    pdf.ln(2)
    
    pdf.set_font("Arial", '', 10)
    for key, val in data['scores'].items():
        if key != "Composite":
            bar_width = (val / 100) * 140
            pdf.cell(60, 6, txt=f"  {key}:", border=0)
            pdf.set_fill_color(99, 110, 250)
            pdf.cell(bar_width, 6, txt="", border=0, fill=1)
            pdf.cell(0, 6, txt=f" {val}/100", border=0, ln=1)
    pdf.ln(5)

    domain = data.get('domain', 'N/A')
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, txt=f"Detected Domain: {domain}", ln=1)
    pdf.ln(5)

    pdf.set_fill_color(239, 246, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Document Statistics", ln=1, fill=1)
    pdf.ln(3)
    
    pdf.set_font("Arial", '', 10)
    stats = data.get('stats', {})
    stat_items = [
        ("Word Count", stats.get("word_count", 0)),
        ("Sentence Count", stats.get("sentence_count", 0)),
        ("Avg Sentence Length", f"{stats.get('avg_sentence_len', 0)} words"),
        ("Avg Word Length", f"{stats.get('avg_word_len', 0)} chars"),
        ("Total Citations", stats.get("total_citations", 0)),
        ("Citation Density", f"{stats.get('citation_density_per_1k', 0)} / 1k"),
        ("Type-Token Ratio", f"{stats.get('type_token_ratio', 0):.4f}"),
        ("Complex Word Ratio", f"{stats.get('complex_word_ratio', 0):.0%}"),
    ]
    for i in range(0, len(stat_items), 2):
        label1, val1 = stat_items[i]
        pdf.cell(95, 6, txt=f"  {label1}: {val1}", border=0)
        if i + 1 < len(stat_items):
            label2, val2 = stat_items[i + 1]
            pdf.cell(0, 6, txt=f"{label2}: {val2}", border=0, ln=1)
        else:
            pdf.ln(6)
    pdf.ln(5)

    keywords = data.get('keywords', [])
    if keywords:
        pdf.set_fill_color(239, 246, 255)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, txt="Top Keywords", ln=1, fill=1)
        pdf.ln(3)
        pdf.set_font("Arial", '', 10)
        keyword_text = ", ".join([kw[0] for kw in keywords[:15]])
        pdf.multi_cell(0, 6, txt=f"  {keyword_text}")
        pdf.ln(5)

    summary = data.get('document_summary', '')
    if summary:
        pdf.set_fill_color(239, 246, 255)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, txt="Document Summary", ln=1, fill=1)
        pdf.ln(3)
        pdf.set_font("Arial", '', 10)
        safe_summary = summary.encode('latin-1', errors='replace').decode('latin-1')
        pdf.multi_cell(0, 6, txt=f"  {safe_summary}")
        pdf.ln(5)

    if section_scores:
        pdf.set_fill_color(239, 246, 255)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, txt="Section-wise Analysis", ln=1, fill=1)
        pdf.ln(3)
        pdf.set_font("Arial", '', 10)
        for sec in section_scores:
            sec_name = sec.get("section", "Unknown")
            sec_score = sec.get("score", 0)
            sec_words = sec.get("word_count", 0)
            sec_clarity = sec.get("clarity_score", 0)
            pdf.cell(0, 6, txt=f"  {sec_name}: Score={sec_score:.1f}, Words={sec_words}, Clarity={sec_clarity:.1f}", ln=1)
        pdf.ln(5)

    found = data.get('structural_found', [])
    missing = data.get('structural_missing', [])
    pdf.set_fill_color(239, 246, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Structure Analysis", ln=1, fill=1)
    pdf.ln(3)
    pdf.set_font("Arial", '', 10)
    if found:
        pdf.cell(0, 6, txt=f"  Found: {', '.join(found)}", ln=1)
    if missing:
        pdf.set_text_color(220, 38, 38)
        pdf.cell(0, 6, txt=f"  Missing: {', '.join(missing)}", ln=1)
        pdf.set_text_color(0, 0, 0)

    sentiment = data.get('sentiment', 0)
    pdf.ln(3)
    pdf.cell(0, 6, txt=f"  Sentiment Polarity: {sentiment:.2f}", ln=1)
    
    sentence_complexity = data.get('sentence_complexity', {})
    if sentence_complexity:
        pdf.cell(0, 6, txt=f"  Sentence Complexity: Simple={sentence_complexity.get('simple_pct', 0):.1f}%, "
                          f"Medium={sentence_complexity.get('medium_pct', 0):.1f}%, "
                          f"Complex={sentence_complexity.get('complex_pct', 0):.1f}%", ln=1)

    issues = data.get('issues', [])
    if issues:
        pdf.ln(5)
        pdf.set_fill_color(254, 226, 226)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, txt="Areas for Improvement", ln=1, fill=1)
        pdf.ln(3)
        pdf.set_font("Arial", '', 10)
        pdf.set_text_color(185, 28, 28)
        pdf.multi_cell(0, 6, txt=f"  {len(issues)} sentences exceed 30 words. Consider simplifying for better readability.")
        pdf.set_text_color(0, 0, 0)

    return pdf.output(dest='S').encode('utf-8', errors='ignore')
