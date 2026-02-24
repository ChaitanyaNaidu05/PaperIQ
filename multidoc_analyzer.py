import logging
import json
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compare_multiple_documents(analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not analyses or len(analyses) < 2:
        return {"error": "Need at least 2 documents to compare"}
    
    comparison = {
        "document_count": len(analyses),
        "metrics_comparison": [],
        "rankings": {},
        "similarity_matrix": [],
        "summary": {}
    }
    
    metric_names = [
        "Composite", "Language", "Coherence", "Reasoning", 
        "Readability", "Sophistication", "Citation Density",
        "Technical Depth", "Novelty Signal", "Structural Completeness",
        "Vocabulary Richness"
    ]
    
    for metric in metric_names:
        metric_values = []
        for i, analysis in enumerate(analyses):
            scores = analysis.get("scores", {})
            value = scores.get(metric, 0)
            metric_values.append({
                "index": i,
                "filename": analysis.get("filename", f"Document {i+1}"),
                "value": value
            })
        
        metric_values.sort(key=lambda x: x["value"], reverse=True)
        comparison["metrics_comparison"].append({
            "metric": metric,
            "values": metric_values,
            "best": metric_values[0] if metric_values else None,
            "average": sum(v["value"] for v in metric_values) / len(metric_values) if metric_values else 0
        })
    
    total_scores = []
    for i, analysis in enumerate(analyses):
        composite = analysis.get("scores", {}).get("Composite", 0)
        total_scores.append({
            "index": i,
            "filename": analysis.get("filename", f"Document {i+1}"),
            "composite_score": composite
        })
    
    total_scores.sort(key=lambda x: x["composite_score"], reverse=True)
    comparison["rankings"]["by_composite_score"] = total_scores
    
    stats_comparison = {}
    stat_names = [
        "word_count", "sentence_count", "avg_sentence_len", 
        "total_citations", "citation_density_per_1k"
    ]
    
    for stat in stat_names:
        stat_values = []
        for i, analysis in enumerate(analyses):
            stats = analysis.get("stats", {})
            value = stats.get(stat, 0)
            stat_values.append({
                "index": i,
                "filename": analysis.get("filename", f"Document {i+1}"),
                "value": value
            })
        stats_comparison[stat] = stat_values
    
    comparison["stats_comparison"] = stats_comparison
    
    domain_counts = {}
    for analysis in analyses:
        domain = analysis.get("domain", "Unknown")
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    comparison["domain_distribution"] = domain_counts
    
    best_in_category = {}
    for metric in metric_names:
        best_doc = None
        best_value = -1
        for i, analysis in enumerate(analyses):
            value = analysis.get("scores", {}).get(metric, 0)
            if value > best_value:
                best_value = value
                best_doc = analysis.get("filename", f"Document {i+1}")
        best_in_category[metric] = {"document": best_doc, "score": best_value}
    
    comparison["best_in_category"] = best_in_category
    
    avg_scores = {}
    for metric in metric_names:
        values = [a.get("scores", {}).get(metric, 0) for a in analyses]
        avg_scores[metric] = sum(values) / len(values) if values else 0
    comparison["average_scores"] = avg_scores
    
    return comparison


def build_comparison_chart_data(comparison_data: Dict) -> Dict:
    if "error" in comparison_data:
        return {}
    
    metrics = ["Composite", "Language", "Coherence", "Reasoning", 
               "Readability", "Technical Depth", "Novelty Signal"]
    
    documents = comparison_data.get("rankings", {}).get("by_composite_score", [])
    doc_names = [d["filename"][:20] for d in documents]
    
    chart_data = {
        "labels": doc_names,
        "datasets": []
    }
    
    for metric in metrics:
        metric_data = comparison_data.get("metrics_comparison", [])
        values = []
        for md in metric_data:
            if md.get("metric") == metric:
                sorted_values = sorted(md.get("values", []), key=lambda x: x["index"])
                values = [v["value"] for v in sorted_values]
                break
        
        chart_data["datasets"].append({
            "label": metric,
            "data": values
        })
    
    return chart_data


def generate_comparison_summary(comparison_data: Dict) -> str:
    if "error" in comparison_data:
        return comparison_data.get("error", "Comparison failed")
    
    doc_count = comparison_data.get("document_count", 0)
    best_overall = comparison_data.get("rankings", {}).get("by_composite_score", [{}])[0]
    
    summary_parts = [
        f"Compared {doc_count} documents. ",
        f"Best overall: {best_overall.get('filename', 'N/A')} "
        f"(Composite: {best_overall.get('composite_score', 0):.1f})."
    ]
    
    best_in_cat = comparison_data.get("best_in_category", {})
    
    if "Technical Depth" in best_in_cat:
        tech_best = best_in_cat["Technical Depth"]
        summary_parts.append(
            f" Highest technical depth: {tech_best.get('document', 'N/A')} "
            f"({tech_best.get('score', 0):.1f})."
        )
    
    if "Novelty Signal" in best_in_cat:
        novelty_best = best_in_cat["Novelty Signal"]
        summary_parts.append(
            f" Highest novelty: {novelty_best.get('document', 'N/A')} "
            f"({novelty_best.get('score', 0):.1f})."
        )
    
    avg_scores = comparison_data.get("average_scores", {})
    if "Composite" in avg_scores:
        summary_parts.append(
            f" Average composite score: {avg_scores['Composite']:.1f}."
        )
    
    return " ".join(summary_parts)
