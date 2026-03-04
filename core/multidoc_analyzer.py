import logging
import math
from typing import List, Dict, Any
from core import transformer_analyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALL_METRICS = [
    "Composite", "Language", "Coherence", "Reasoning",
    "Readability", "Sophistication", "Citation Density",
    "Technical Depth", "Novelty Signal", "Structural Completeness",
    "Vocabulary Richness"
]


def _get_score(analysis: Dict, metric: str) -> float:
    return float(analysis.get("scores", {}).get(metric, 0))


def _get_stat(analysis: Dict, key: str) -> float:
    return float(analysis.get("stats", {}).get(key, 0))


def _delta_interpretation(delta: float) -> str:
    abs_d = abs(delta)
    direction = "higher" if delta > 0 else "lower"
    if abs_d < 2:
        return "on par"
    elif abs_d < 8:
        return f"slightly {direction}"
    elif abs_d < 20:
        return f"notably {direction}"
    else:
        return f"significantly {direction}"


def _keyword_overlap(kw_list_a: list, kw_list_b: list, text_a: str = "", text_b: str = "") -> Dict:
    set_a = set(
        k[0].lower() for k in kw_list_a
        if isinstance(k, (list, tuple)) and len(k) >= 1
    )
    set_b = set(
        k[0].lower() for k in kw_list_b
        if isinstance(k, (list, tuple)) and len(k) >= 1
    )
    
    shared = set_a & set_b
    unique_a = sorted(list(set_a - set_b))[:10]
    unique_b = sorted(list(set_b - set_a))[:10]
    
    semantic_sim = 0.0
    if text_a and text_b:
        semantic_sim = transformer_analyzer.compute_semantic_similarity(text_a, text_b)
    else:
        union = set_a | set_b
        semantic_sim = len(shared) / max(len(union), 1)

    overlap_pct = round(semantic_sim * 100, 1)
    
    return {
        "shared": sorted(shared),
        "unique_a": unique_a,
        "unique_b": unique_b,
        "overlap_percent": overlap_pct,
        "topic_similarity": "High" if overlap_pct > 60 else ("Moderate" if overlap_pct > 30 else "Low")
    }


def _compare_pair(a: Dict, b: Dict) -> Dict:
    name_a = a.get("filename", "Document A")
    name_b = b.get("filename", "Document B")

    metric_deltas = {}
    strengths_a = []
    strengths_b = []

    for metric in ALL_METRICS:
        score_a = _get_score(a, metric)
        score_b = _get_score(b, metric)
        delta = score_a - score_b
        leader = name_a if delta > 0 else (name_b if delta < 0 else "tied")
        metric_deltas[metric] = {
            "doc_a": round(score_a, 1),
            "doc_b": round(score_b, 1),
            "delta": round(abs(delta), 1),
            "leader": leader,
            "interpretation": _delta_interpretation(delta)
        }
        if delta > 5:
            strengths_a.append(f"Stronger {metric} ({score_a:.0f} vs {score_b:.0f})")
        elif delta < -5:
            strengths_b.append(f"Stronger {metric} ({score_b:.0f} vs {score_a:.0f})")

    stat_keys = {
        "word_count": "Length (words)",
        "sentence_count": "Sentence count",
        "avg_sentence_len": "Avg sentence length",
        "total_citations": "Citations",
        "citation_density_per_1k": "Citation density /1k"
    }
    stat_comparisons = {}
    for key, label in stat_keys.items():
        val_a = _get_stat(a, key)
        val_b = _get_stat(b, key)
        pct = round(((val_a - val_b) / max(val_b, 1)) * 100, 1) if val_b != 0 else 0.0
        stat_comparisons[key] = {
            "label": label,
            "doc_a": val_a,
            "doc_b": val_b,
            "pct_diff": pct,
            "leader": name_a if val_a > val_b else (name_b if val_b > val_a else "tied")
        }

    text_a = a.get("results_data", {}).get("full_text", "")
    text_b = b.get("results_data", {}).get("full_text", "")
    
    kw_analysis = _keyword_overlap(a.get("keywords", []), b.get("keywords", []), text_a, text_b)

    sections_a = set(a.get("structural_found", []))
    sections_b = set(b.get("structural_found", []))

    dom_a = a.get("domain", "Unknown")
    dom_b = b.get("domain", "Unknown")

    cross_components = {}
    if dom_a == dom_b and kw_analysis.get("overlap_percent", 0) > 20:
        sections_dict_a = {k.lower(): v for k, v in a.get("sections_data", {}).items() if isinstance(v, dict) and "content" in v}
        sections_dict_b = {k.lower(): v for k, v in b.get("sections_data", {}).items() if isinstance(v, dict) and "content" in v}
        
        shared_keys = set(sections_dict_a.keys()) & set(sections_dict_b.keys())
        target_sections = ["abstract", "introduction", "method", "results", "conclusion"]
        
        # Stop words for naive common-term extraction if NLTK/spacy isn't loaded
        stop_words = {"the", "and", "of", "to", "a", "in", "is", "for", "that", "this", "on", "with", "as", "by", "an", "are", "be", "was", "were", "it", "at", "from", "or", "which", "we"}
        
        import re
        for tgt in target_sections:
            matches = [k for k in shared_keys if tgt in k]
            if matches:
                key = matches[0]
                text_a_sec = sections_dict_a[key]["content"]
                text_b_sec = sections_dict_b[key]["content"]
                
                if len(text_a_sec) > 50 and len(text_b_sec) > 50:
                    sim_score = transformer_analyzer.compute_semantic_similarity(text_a_sec[:1500], text_b_sec[:1500])
                    
                    if sim_score >= 0.35:
                        words_a = set(w for w in re.findall(r'\b[a-z]{5,}\b', text_a_sec.lower()) if w not in stop_words)
                        words_b = set(w for w in re.findall(r'\b[a-z]{5,}\b', text_b_sec.lower()) if w not in stop_words)
                        shared_terms = sorted(list(words_a & words_b))[:8]
                        
                        cross_components[key.title()] = {
                            "similarity": round(sim_score * 100, 1),
                            "shared_terms": shared_terms
                        }

    return {
        "doc_a": name_a,
        "doc_b": name_b,
        "metric_deltas": metric_deltas,
        "stat_comparisons": stat_comparisons,
        "keyword_overlap": kw_analysis,
        "domain_a": dom_a,
        "domain_b": dom_b,
        "domain_agreement": dom_a == dom_b,
        "strengths_a": strengths_a,
        "strengths_b": strengths_b,
        "cross_components": cross_components,
        "section_coverage": {
            "shared": sorted(sections_a & sections_b),
            "only_in_a": sorted(sections_a - sections_b),
            "only_in_b": sorted(sections_b - sections_a)
        }
    }


def compare_multiple_documents(analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not analyses or len(analyses) < 2:
        return {"error": "Need at least 2 documents to compare"}

    metric_scores = {}
    for metric in ALL_METRICS:
        values = [
            {
                "index": i,
                "filename": a.get("filename", f"Document {i+1}"),
                "value": _get_score(a, metric)
            }
            for i, a in enumerate(analyses)
        ]
        values_sorted = sorted(values, key=lambda x: x["value"], reverse=True)
        avg = sum(v["value"] for v in values) / len(values)
        variance = sum((v["value"] - avg) ** 2 for v in values) / len(values)
        std = math.sqrt(variance)
        spread = values_sorted[0]["value"] - values_sorted[-1]["value"]
        metric_scores[metric] = {
            "ranked": values_sorted,
            "average": round(avg, 1),
            "std_dev": round(std, 1),
            "spread": round(spread, 1),
            "best": values_sorted[0],
            "worst": values_sorted[-1]
        }

    rankings = sorted(
        [
            {
                "index": i,
                "filename": a.get("filename", f"Document {i+1}"),
                "composite_score": _get_score(a, "Composite")
            }
            for i, a in enumerate(analyses)
        ],
        key=lambda x: x["composite_score"],
        reverse=True
    )

    pairwise = []
    for i in range(len(analyses)):
        for j in range(i + 1, len(analyses)):
            pairwise.append(_compare_pair(analyses[i], analyses[j]))

    domain_counts = {}
    for a in analyses:
        d = a.get("domain", "Unknown")
        domain_counts[d] = domain_counts.get(d, 0) + 1

    kw_sets = [
        set(k[0].lower() for k in a.get("keywords", [])
            if isinstance(k, (list, tuple)) and len(k) >= 1)
        for a in analyses
    ]
    universal_keywords = sorted(set.intersection(*kw_sets)) if kw_sets else []

    high_variance = [m for m, d in metric_scores.items() if d["spread"] > 20]
    consistent = [m for m, d in metric_scores.items() if d["spread"] < 5]

    insights = []
    for m in high_variance:
        data = metric_scores[m]
        insights.append(
            f"{data['best']['filename']} leads in {m} with {data['best']['value']:.0f} "
            f"vs {data['worst']['filename']} at {data['worst']['value']:.0f} "
            f"(a {data['spread']:.0f}-point spread)"
        )
    for m in consistent:
        data = metric_scores[m]
        insights.append(
            f"All documents score consistently on {m} "
            f"(avg {data['average']:.0f}, spread only {data['spread']:.0f} pts)"
        )

    return {
        "document_count": len(analyses),
        "rankings": rankings,
        "metric_scores": metric_scores,
        "pairwise": pairwise,
        "domain_distribution": domain_counts,
        "universal_keywords": universal_keywords,
        "high_variance_metrics": high_variance,
        "consistent_metrics": consistent,
        "insights": insights
    }


def generate_comparison_summary(comparison_data: Dict) -> str:
    if "error" in comparison_data:
        return comparison_data.get("error", "Comparison failed")

    rankings = comparison_data.get("rankings", [])
    if not rankings:
        return "Comparison complete."

    best = rankings[0]
    worst = rankings[-1]
    doc_count = comparison_data.get("document_count", 0)

    parts = [
        f"Compared {doc_count} documents.",
        f"Top performer: {best.get('filename', 'N/A')} "
        f"(composite score {best.get('composite_score', 0):.1f}/100)."
    ]

    if len(rankings) > 1:
        gap = best.get("composite_score", 0) - worst.get("composite_score", 0)
        parts.append(
            f"Score spread of {gap:.1f} points between strongest and weakest paper."
        )

    insights = comparison_data.get("insights", [])
    if insights:
        parts.append(f"Key finding: {insights[0]}")

    universal = comparison_data.get("universal_keywords", [])
    if universal:
        parts.append(f"Shared themes across all papers: {', '.join(universal[:5])}.")

    return " ".join(parts)
