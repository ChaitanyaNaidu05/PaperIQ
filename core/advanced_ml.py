import logging
import re
import math
from typing import Dict, List, Tuple, Any
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import numpy as np
    from transformer_analyzer import get_transformer_model, TRANSFORMERS_AVAILABLE
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available for advanced ML features")


ARXIV_CATEGORIES = {
    "Computer Science - AI": ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.NE"],
    "Computer Science - Systems": ["cs.OS", "cs.DC", "cs.CR", "cs.NI"],
    "Computer Science - Theory": ["cs.DS", "cs.CC", "cs.LO", "cs.CG"],
    "Computer Science - Software": ["cs.SE", "cs.PL", "cs.DL"],
    "Physics": ["physics", "cond-mat", "hep-ph", "hep-th", "quant-ph"],
    "Mathematics": ["math", "math.ST", "math.PR", "math.FA"],
    "Statistics": ["stat", "stat.ML", "stat.TH", "stat.AP"],
    "Electrical Engineering": ["eess", "eess.SP", "eess.AS", "eess.IV"],
    "Quantitative Biology": ["q-bio", "q-bio.BM", "q-bio.GN", "q-bio.PE"],
    "Quantitative Finance": ["q-fin", "q-fin.EC", "q-fin.TR", "q-fin.ST"],
    "Economics": ["econ", "econ.GN", "econ.EM", "econ.TH"],
}


def compute_advanced_domain_score(text: str, domain: str) -> float:
    domain_keywords = {
        "Computer Science": [
            "algorithm", "neural network", "machine learning", "deep learning",
            "dataset", "transformer", "convolutional", "gpu", "training",
            "inference", "classification", "regression", "software", "compiler",
            "api", "database", "optimization", "benchmark", "backpropagation",
            "architecture", "model", "prediction", "feature", "embedding"
        ],
        "Biology / Medicine": [
            "protein", "gene", "cell", "dna", "rna", "enzyme", "clinical",
            "patient", "therapy", "diagnosis", "pathology", "mutation",
            "genome", "biomarker", "antibody", "tissue", "organism", "species",
            "expression", "sequencing", "pathway", "receptor"
        ],
        "Physics": [
            "quantum", "entropy", "particle", "photon", "wave", "field",
            "energy", "mass", "velocity", "momentum", "thermodynamic",
            "relativity", "boson", "fermion", "tensor", "hamiltonian",
            "lagrangian", "symmetry", "interaction", "coupling"
        ],
        "Economics / Finance": [
            "market", "gdp", "inflation", "fiscal", "monetary", "equilibrium",
            "demand", "supply", "trade", "portfolio", "regression", "econometric",
            "interest rate", "capital", "welfare", "utility", "price", "cost"
        ],
        "Mathematics / Statistics": [
            "theorem", "proof", "lemma", "hypothesis", "variance", "distribution",
            "integral", "derivative", "convergence", "matrix", "eigenvalue",
            "stochastic", "probability", "bayesian", "estimator", "function"
        ],
    }

    text_lower = text.lower()
    keywords = domain_keywords.get(domain, [])

    match_count = sum(text_lower.count(kw) for kw in keywords)
    word_count = len(text.split())

    if word_count == 0:
        return 0.0

    keyword_density = (match_count / word_count) * 100
    score = min(100, keyword_density * 15 + match_count * 2)

    return round(score, 2)


def predict_paper_quality(scores: Dict[str, float], stats: Dict[str, Any]) -> Dict:
    metric_weights = {
        "Technical Depth": 0.18,
        "Novelty Signal": 0.15,
        "Structural Completeness": 0.15,
        "Coherence": 0.12,
        "Language": 0.10,
        "Reasoning": 0.10,
        "Vocabulary Richness": 0.08,
        "Citation Density": 0.07,
        "Readability": 0.05,
    }

    weighted_score = 0
    for metric, weight in metric_weights.items():
        metric_value = scores.get(metric, 0)
        weighted_score += metric_value * weight

    word_count = stats.get("word_count", 0)
    length_bonus = min(10, max(0, (word_count - 3000) / 500))

    citation_density = stats.get("citation_density_per_1k", 0)
    citation_bonus = min(5, citation_density * 0.5) if 5 <= citation_density <= 20 else 0

    final_quality = min(100, weighted_score + length_bonus + citation_bonus)

    quality_grade = "A+" if final_quality >= 90 else \
                    "A" if final_quality >= 85 else \
                    "A-" if final_quality >= 80 else \
                    "B+" if final_quality >= 75 else \
                    "B" if final_quality >= 70 else \
                    "B-" if final_quality >= 65 else \
                    "C+" if final_quality >= 60 else \
                    "C" if final_quality >= 50 else "D"

    percentile_estimate = min(99, max(1, int(final_quality * 0.9)))

    return {
        "quality_score": round(final_quality, 2),
        "grade": quality_grade,
        "percentile_estimate": percentile_estimate,
        "strengths": _identify_strengths(scores, stats),
        "weaknesses": _identify_weaknesses(scores, stats),
        "recommendations": _generate_recommendations(scores, stats),
    }


def _identify_strengths(scores: Dict[str, float], stats: Dict[str, Any]) -> List[str]:
    strengths = []

    if scores.get("Technical Depth", 0) >= 75:
        strengths.append("Strong technical depth with domain-specific terminology")

    if scores.get("Novelty Signal", 0) >= 70:
        strengths.append("Clear contribution and novelty indicators")

    if scores.get("Structural Completeness", 0) >= 80:
        strengths.append("Well-structured with all standard sections")

    if scores.get("Coherence", 0) >= 75:
        strengths.append("Good logical flow and transitions")

    citation_density = stats.get("citation_density_per_1k", 0)
    if 8 <= citation_density <= 25:
        strengths.append("Appropriate citation density")

    if stats.get("type_token_ratio", 0) >= 0.4:
        strengths.append("Rich and diverse vocabulary")

    return strengths if strengths else ["Adequate overall quality"]


def _identify_weaknesses(scores: Dict[str, float], stats: Dict[str, Any]) -> List[str]:
    weaknesses = []

    if scores.get("Technical Depth", 0) < 50:
        weaknesses.append("Limited technical depth")

    if scores.get("Novelty Signal", 0) < 40:
        weaknesses.append("Weak novelty indicators")

    if scores.get("Structural Completeness", 0) < 60:
        weaknesses.append("Missing key structural sections")

    if scores.get("Coherence", 0) < 50:
        weaknesses.append("Poor logical flow")

    citation_density = stats.get("citation_density_per_1k", 0)
    if citation_density < 3:
        weaknesses.append("Insufficient citations")
    elif citation_density > 30:
        weaknesses.append("Over-citation detected")

    complex_ratio = stats.get("complex_word_ratio", 0)
    if complex_ratio > 0.4:
        weaknesses.append("Excessive complex sentences")

    return weaknesses if weaknesses else ["No major weaknesses identified"]


def _generate_recommendations(scores: Dict[str, float], stats: Dict[str, Any]) -> List[str]:
    recommendations = []

    if scores.get("Technical Depth", 0) < 60:
        recommendations.append("Include more domain-specific terminology and technical details")

    if scores.get("Novelty Signal", 0) < 50:
        recommendations.append("Clearly state contributions using phrases like 'we propose' or 'our method'")

    if scores.get("Structural Completeness", 0) < 70:
        recommendations.append("Ensure all standard sections (Abstract, Introduction, Methods, Results, Conclusion) are present")

    if scores.get("Coherence", 0) < 60:
        recommendations.append("Add more transition words (however, therefore, furthermore) to improve flow")

    if scores.get("Readability", 0) < 50:
        recommendations.append("Simplify sentence structure for better readability")

    citation_density = stats.get("citation_density_per_1k", 0)
    if citation_density < 5:
        recommendations.append("Add more relevant citations to support claims")

    issues_count = len(stats.get("issues", []))
    if issues_count > 10:
        recommendations.append(f"Reduce sentence length - {issues_count} sentences exceed recommended length")

    return recommendations if recommendations else ["Continue maintaining current quality standards"]


def estimate_acceptance_probability(quality_data: Dict, domain: str) -> Dict:
    quality_score = quality_data.get("quality_score", 50)
    grade = quality_data.get("grade", "C")

    venue_tiers = {
        "top": {"base_rate": 0.08, "name": "Top-tier (Nature, Science, top conferences)"},
        "high": {"base_rate": 0.15, "name": "High-tier (Q1 journals, major conferences)"},
        "medium": {"base_rate": 0.35, "name": "Medium-tier (Q2-Q3 journals)"},
        "standard": {"base_rate": 0.55, "name": "Standard venues"},
    }

    grade_multiplier = {
        "A+": 2.5, "A": 2.2, "A-": 1.9,
        "B+": 1.6, "B": 1.3, "B-": 1.0,
        "C+": 0.7, "C": 0.5, "D": 0.3
    }

    multiplier = grade_multiplier.get(grade, 1.0)

    predictions = {}
    for tier, data in venue_tiers.items():
        base = data["base_rate"]
        adjusted = min(0.95, base * multiplier + (quality_score - 50) / 200)
        predictions[tier] = {
            "venue_type": data["name"],
            "probability": round(adjusted * 100, 1)
        }

    return {
        "predictions": predictions,
        "best_fit": max(predictions.keys(), key=lambda k: predictions[k]["probability"]),
        "confidence": "high" if quality_score >= 75 else "medium" if quality_score >= 50 else "low"
    }


def analyze_writing_quality(text: str, scores: Dict) -> Dict:
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    words = text.split()
    word_count = len(words)

    avg_sentence_length = word_count / len(sentences) if sentences else 0

    passive_patterns = [
        r'\b(is|are|was|were|be|been|being)\s+\w+ed\b',
        r'\b(by\s+\w+)\b',
        r'\b(was\s+found|were\s+observed|is\s+proposed|are\s+presented)\b'
    ]

    passive_count = 0
    for pattern in passive_patterns:
        passive_count += len(re.findall(pattern, text, re.IGNORECASE))

    passive_ratio = passive_count / len(sentences) if sentences else 0

    hedging_words = ['may', 'might', 'could', 'possibly', 'potentially',
                     'suggests', 'indicates', 'appears', 'seems']
    hedging_count = sum(text.lower().count(h) for h in hedging_words)

    clarity_issues = []

    if avg_sentence_length > 30:
        clarity_issues.append({
            "type": "long_sentences",
            "message": f"Average sentence length ({avg_sentence_length:.1f} words) exceeds recommended 25 words",
            "severity": "medium"
        })

    if passive_ratio > 0.3:
        clarity_issues.append({
            "type": "passive_voice",
            "message": f"High passive voice usage ({passive_ratio*100:.1f}%). Consider active voice.",
            "severity": "low"
        })

    if hedging_count > len(sentences) * 0.4:
        clarity_issues.append({
            "type": "excessive_hedging",
            "message": "Excessive hedging language. Be more direct in claims.",
            "severity": "medium"
        })

    readability = scores.get("Readability", 50)
    if readability < 40:
        clarity_issues.append({
            "type": "low_readability",
            "message": "Low readability score. Simplify vocabulary and sentence structure.",
            "severity": "high"
        })

    suggestions = []
    if avg_sentence_length > 25:
        suggestions.append("Break long sentences into shorter ones")
    if passive_ratio > 0.2:
        suggestions.append("Replace passive constructions with active voice")
    if readability < 50:
        suggestions.append("Use simpler words where possible")
    if hedging_count > len(sentences) * 0.3:
        suggestions.append("Reduce hedging language for stronger claims")

    return {
        "avg_sentence_length": round(avg_sentence_length, 1),
        "passive_voice_ratio": round(passive_ratio, 2),
        "hedging_count": hedging_count,
        "clarity_score": max(0, 100 - len(clarity_issues) * 15 - (avg_sentence_length - 20)),
        "issues": clarity_issues,
        "suggestions": suggestions
    }


def compute_reproducibility_score(text: str, sections: Dict) -> Dict:
    text_lower = text.lower()

    code_availability = any(pattern in text_lower for pattern in [
        "code available", "source code", "github", "gitlab",
        "code repository", "open source", "code can be found"
    ])

    data_availability = any(pattern in text_lower for pattern in [
        "data available", "dataset available", "data repository",
        "supplementary data", "data can be found", "data sharing"
    ])

    method_detail = any(pattern in text_lower for pattern in [
        "we describe", "detailed in", "appendix", "supplementary",
        "algorithm", "pseudocode", "implementation details"
    ])

    hyperparameters = any(pattern in text_lower for pattern in [
        "hyperparameter", "learning rate", "batch size", "epochs",
        "parameters", "configuration", "settings"
    ])

    environment = any(pattern in text_lower for pattern in [
        "implemented in", "using python", "tensorflow", "pytorch",
        "software", "version", "environment"
    ])

    section_names_lower = [s.lower() for s in sections.keys()]
    has_methods = any("method" in s for s in section_names_lower)
    has_appendix = any("appendix" in s or "supplementary" in s for s in section_names_lower)

    score_components = {
        "code_availability": 25 if code_availability else 0,
        "data_availability": 20 if data_availability else 0,
        "method_detail": 20 if method_detail else 0,
        "hyperparameters": 15 if hyperparameters else 0,
        "environment": 10 if environment else 0,
        "has_methods_section": 10 if has_methods else 0
    }

    total_score = sum(score_components.values())

    indicators = {
        "code_available": code_availability,
        "data_available": data_availability,
        "detailed_methods": method_detail,
        "hyperparameters_specified": hyperparameters,
        "environment_documented": environment,
        "has_methods_section": has_methods,
        "has_supplementary": has_appendix
    }

    missing = [k for k, v in indicators.items() if not v]

    recommendations = []
    if not code_availability:
        recommendations.append("Make code available in a public repository")
    if not data_availability:
        recommendations.append("Provide data availability statement")
    if not method_detail:
        recommendations.append("Add detailed methodology description")
    if not hyperparameters:
        recommendations.append("Specify all hyperparameters and settings")
    if not environment:
        recommendations.append("Document software environment and versions")

    return {
        "score": total_score,
        "grade": "A" if total_score >= 80 else "B" if total_score >= 60 else "C" if total_score >= 40 else "D",
        "components": score_components,
        "indicators": indicators,
        "missing_items": missing,
        "recommendations": recommendations
    }


def check_ethical_compliance(text: str) -> Dict:
    text_lower = text.lower()

    human_subjects_indicators = [
        "human subjects", "participants", "patients", "subjects",
        "informed consent", "survey respondents", "user study"
    ]

    animal_subjects_indicators = [
        "animal", "mice", "rats", "subjects (animal)", "ethical approval (animal)"
    ]

    has_human_subjects = any(ind in text_lower for ind in human_subjects_indicators)
    has_animal_subjects = any(ind in text_lower for ind in animal_subjects_indicators)

    ethical_statements = {
        "irb_approval": any(p in text_lower for p in [
            "irb approval", "institutional review board", "ethics committee",
            "ethics approval", "ethical approval"
        ]),
        "informed_consent": any(p in text_lower for p in [
            "informed consent", "consent obtained", "participants consented"
        ]),
        "declaration_helsinki": "declaration of helsinki" in text_lower,
        "hipaa_compliance": "hipaa" in text_lower,
        "gdpr_compliance": "gdpr" in text_lower or "general data protection" in text_lower,
        "data_anonymization": any(p in text_lower for p in [
            "anonymized", "de-identified", "anonymous data"
        ]),
        "conflict_of_interest": any(p in text_lower for p in [
            "conflict of interest", "competing interests", "no conflict"
        ]),
        "funding_disclosure": any(p in text_lower for p in [
            "funding", "financial support", "grant", "sponsored"
        ])
    }

    required_for_human = ["irb_approval", "informed_consent"]
    required_general = ["conflict_of_interest", "funding_disclosure"]

    missing_ethical = []
    if has_human_subjects:
        for req in required_for_human:
            if not ethical_statements.get(req, False):
                missing_ethical.append(req.replace("_", " ").title())

    for req in required_general:
        if not ethical_statements.get(req, False):
            missing_ethical.append(req.replace("_", " ").title())

    compliance_score = sum(1 for v in ethical_statements.values() if v) / len(ethical_statements) * 100

    return {
        "has_human_subjects": has_human_subjects,
        "has_animal_subjects": has_animal_subjects,
        "statements": ethical_statements,
        "missing_requirements": missing_ethical,
        "compliance_score": round(compliance_score, 1),
        "status": "compliant" if len(missing_ethical) == 0 else "needs_attention" if len(missing_ethical) <= 2 else "non_compliant"
    }


def analyze_statistical_rigor(text: str, stats: Dict) -> Dict:
    text_lower = text.lower()

    statistical_tests = {
        "t_test": any(p in text_lower for p in ["t-test", "t test", "student's t"]),
        "anova": "anova" in text_lower or "analysis of variance" in text_lower,
        "chi_square": any(p in text_lower for p in ["chi-square", "chi square", "χ²"]),
        "regression": any(p in text_lower for p in ["regression", "linear model", "logistic regression"]),
        "correlation": any(p in text_lower for p in ["correlation", "pearson", "spearman"]),
        "bayesian": any(p in text_lower for p in ["bayesian", "posterior", "prior distribution"]),
        "non_parametric": any(p in text_lower for p in ["mann-whitney", "wilcoxon", "kruskal"]),
    }

    tests_used = [k for k, v in statistical_tests.items() if v]

    p_values_mentioned = any(p in text_lower for p in [
        "p <", "p <", "p-value", "p value", "significance", "statistically significant"
    ])

    confidence_intervals = any(p in text_lower for p in [
        "confidence interval", "ci =", "95% ci", "99% ci"
    ])

    effect_sizes = any(p in text_lower for p in [
        "effect size", "cohen's d", "odds ratio", "hazard ratio"
    ])

    power_analysis = "power" in text_lower and ("analysis" in text_lower or "calculation" in text_lower)

    multiple_testing = any(p in text_lower for p in [
        "bonferroni", "false discovery rate", "fdr", "multiple testing correction"
    ])

    rigor_indicators = {
        "statistical_tests": len(tests_used),
        "tests_used": tests_used,
        "p_values_reported": p_values_mentioned,
        "confidence_intervals": confidence_intervals,
        "effect_sizes": effect_sizes,
        "power_analysis": power_analysis,
        "multiple_testing_correction": multiple_testing
    }

    score = 0
    if len(tests_used) >= 2:
        score += 25
    elif len(tests_used) >= 1:
        score += 15

    if p_values_mentioned:
        score += 20
    if confidence_intervals:
        score += 20
    if effect_sizes:
        score += 15
    if power_analysis:
        score += 10
    if multiple_testing:
        score += 10

    recommendations = []
    if not p_values_mentioned:
        recommendations.append("Report p-values for statistical tests")
    if not confidence_intervals:
        recommendations.append("Include confidence intervals for estimates")
    if not effect_sizes:
        recommendations.append("Report effect sizes alongside significance")
    if not power_analysis and "sample" in text_lower:
        recommendations.append("Consider reporting power analysis for sample size justification")

    return {
        "score": min(100, score),
        "grade": "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D",
        "indicators": rigor_indicators,
        "recommendations": recommendations
    }


def run_advanced_analysis(text: str, sections: Dict, scores: Dict, stats: Dict) -> Dict:
    quality_data = predict_paper_quality(scores, stats)
    acceptance_data = estimate_acceptance_probability(quality_data, scores.get("domain", "General"))
    writing_data = analyze_writing_quality(text, scores)
    reproducibility_data = compute_reproducibility_score(text, sections)
    ethical_data = check_ethical_compliance(text)
    statistical_data = analyze_statistical_rigor(text, stats)

    return {
        "quality_prediction": quality_data,
        "acceptance_probability": acceptance_data,
        "writing_quality": writing_data,
        "reproducibility": reproducibility_data,
        "ethical_compliance": ethical_data,
        "statistical_rigor": statistical_data
    }
