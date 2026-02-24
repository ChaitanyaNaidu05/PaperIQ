import logging
import re
from typing import List, Dict, Tuple, Set
from collections import Counter
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Entity:
    text: str
    entity_type: str
    count: int = 1
    positions: List[int] = None


RESEARCH_METHODS = [
    "machine learning", "deep learning", "neural network", "convolutional",
    "recurrent", "transformer", "attention mechanism", "reinforcement learning",
    "supervised learning", "unsupervised learning", "semi-supervised",
    "classification", "regression", "clustering", "dimensionality reduction",
    "feature extraction", "transfer learning", "fine-tuning", "pre-training",
    "cross-validation", "random forest", "support vector machine", "decision tree",
    "gradient boosting", "ensemble method", "bayesian inference", "monte carlo",
    "statistical analysis", "hypothesis testing", "anova", "chi-square",
    "linear regression", "logistic regression", "time series", "forecasting",
    "experimental study", "case study", "survey", "meta-analysis",
    "systematic review", "randomized controlled trial", "cohort study",
    "qualitative analysis", "quantitative analysis", "mixed methods",
    "simulation", "modeling", "optimization", "genetic algorithm",
    "particle swarm", "gradient descent", "backpropagation"
]

TECHNICAL_TERMS = [
    "algorithm", "dataset", "benchmark", "baseline", "state-of-the-art",
    "performance", "accuracy", "precision", "recall", "f1-score", "auc",
    "loss function", "activation function", "dropout", "batch normalization",
    "hyperparameter", "learning rate", "epoch", "iteration", "convergence",
    "overfitting", "underfitting", "regularization", "normalization",
    "embedding", "tokenization", "vectorization", "feature engineering",
    "data augmentation", "cross-entropy", "mean squared error", "gradient",
    "backbone", "architecture", "framework", "pipeline", "inference",
    "training", "validation", "testing", "generalization", "robustness"
]

INSTITUTION_PATTERNS = [
    r"\b[A-Z][a-z]+ University\b",
    r"\b[A-Z][a-z]+ College\b",
    r"\b[A-Z][a-z]+ Institute\b",
    r"\b[A-Z][a-z]+ Laboratory\b",
    r"\b[A-Z][a-z]+ Research Center\b",
    r"University of [A-Z][a-z]+",
    r"\bMIT\b",
    r"\bStanford\b",
    r"\bHarvard\b",
    r"\bCambridge\b",
    r"\bOxford\b",
]

SOFTWARE_PATTERNS = [
    r"\bPython\b",
    r"\bTensorFlow\b",
    r"\bPyTorch\b",
    r"\bKeras\b",
    r"\bScikit-learn\b",
    r"\bPandas\b",
    r"\bNumPy\b",
    r"\bMATLAB\b",
    r"\bR\b",
    r"\bSPSS\b",
    r"\bStata\b",
    r"\bTableau\b",
    r"\bExcel\b",
    r"\bSQL\b",
    r"\bMongoDB\b",
    r"\bPostgreSQL\b",
    r"\bMySQL\b",
    r"\bApache\b",
    r"\bHadoop\b",
    r"\bSpark\b",
    r"\bDocker\b",
    r"\bKubernetes\b",
    r"\bAWS\b",
    r"\bAzure\b",
    r"\bGCP\b",
]

DATASET_PATTERNS = [
    r"\bImageNet\b",
    r"\bCIFAR\b",
    r"\bMNIST\b",
    r"\bCOCO\b",
    r"\bWikiText\b",
    r"\bPenn Treebank\b",
    r"\bIMDB\b",
    r"\bYelp\b",
    r"\bAmazon Reviews\b",
    r"\bGoogle Trends\b",
    r"\bKaggle\b",
    r"\bUCI\b",
]


def extract_research_methods(text: str) -> List[Entity]:
    methods = []
    text_lower = text.lower()
    
    for method in RESEARCH_METHODS:
        pattern = r"\b" + re.escape(method) + r"\b"
        matches = list(re.finditer(pattern, text_lower))
        if matches:
            methods.append(Entity(
                text=method,
                entity_type="METHOD",
                count=len(matches),
                positions=[m.start() for m in matches]
            ))
    
    methods.sort(key=lambda x: x.count, reverse=True)
    return methods


def extract_technical_terms(text: str) -> List[Entity]:
    terms = []
    text_lower = text.lower()
    
    for term in TECHNICAL_TERMS:
        pattern = r"\b" + re.escape(term) + r"\b"
        matches = list(re.finditer(pattern, text_lower))
        if matches:
            terms.append(Entity(
                text=term,
                entity_type="TERM",
                count=len(matches),
                positions=[m.start() for m in matches]
            ))
    
    terms.sort(key=lambda x: x.count, reverse=True)
    return terms


def extract_institutions(text: str) -> List[Entity]:
    institutions = []
    
    for pattern in INSTITUTION_PATTERNS:
        matches = list(re.finditer(pattern, text))
        if matches:
            for match in matches:
                institutions.append(Entity(
                    text=match.group(),
                    entity_type="INSTITUTION",
                    count=1,
                    positions=[match.start()]
                ))
    
    institution_counts = Counter([inst.text for inst in institutions])
    unique_institutions = [
        Entity(text=name, entity_type="INSTITUTION", count=count)
        for name, count in institution_counts.items()
    ]
    unique_institutions.sort(key=lambda x: x.count, reverse=True)
    
    return unique_institutions


def extract_software_tools(text: str) -> List[Entity]:
    tools = []
    
    for pattern in SOFTWARE_PATTERNS:
        matches = list(re.finditer(pattern, text))
        if matches:
            for match in matches:
                tools.append(Entity(
                    text=match.group(),
                    entity_type="SOFTWARE",
                    count=1,
                    positions=[match.start()]
                ))
    
    tool_counts = Counter([tool.text for tool in tools])
    unique_tools = [
        Entity(text=name, entity_type="SOFTWARE", count=count)
        for name, count in tool_counts.items()
    ]
    unique_tools.sort(key=lambda x: x.count, reverse=True)
    
    return unique_tools


def extract_datasets(text: str) -> List[Entity]:
    datasets = []
    
    for pattern in DATASET_PATTERNS:
        matches = list(re.finditer(pattern, text))
        if matches:
            for match in matches:
                datasets.append(Entity(
                    text=match.group(),
                    entity_type="DATASET",
                    count=1,
                    positions=[match.start()]
                ))
    
    dataset_counts = Counter([ds.text for ds in datasets])
    unique_datasets = [
        Entity(text=name, entity_type="DATASET", count=count)
        for name, count in dataset_counts.items()
    ]
    unique_datasets.sort(key=lambda x: x.count, reverse=True)
    
    return unique_datasets


def extract_metrics(text: str) -> List[Entity]:
    metric_patterns = [
        (r"(\d+\.?\d*)\s*%", "PERCENTAGE"),
        (r"(\d+\.?\d*)\s*(?:ms|seconds?|minutes?|hours?)", "TIME"),
        (r"accuracy\s*[=:]\s*(\d+\.?\d*)", "ACCURACY"),
        (r"precision\s*[=:]\s*(\d+\.?\d*)", "PRECISION"),
        (r"recall\s*[=:]\s*(\d+\.?\d*)", "RECALL"),
        (r"f1\s*[=:]\s*(\d+\.?\d*)", "F1_SCORE"),
        (r"auc\s*[=:]\s*(\d+\.?\d*)", "AUC"),
        (r"p\s*[<>=]\s*0\.?\d*", "P_VALUE"),
        (r"r\s*[=:]\s*-?\d+\.?\d*", "CORRELATION"),
    ]
    
    metrics = []
    for pattern, metric_type in metric_patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            for match in matches:
                metrics.append(Entity(
                    text=match.group(),
                    entity_type=metric_type,
                    count=1,
                    positions=[match.start()]
                ))
    
    return metrics


def extract_citations(text: str) -> List[Entity]:
    citation_patterns = [
        r"\[\d+(?:[,;\s]+\d+)*\]",
        r"\([A-Z][a-z]+(?:\s+(?:and|&)\s+[A-Z][a-z]+)*,?\s*\d{4}\)",
        r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+et\s+al\.\s*\(\d{4}\)",
        r"\(\d{4}\)",
    ]
    
    citations = []
    for pattern in citation_patterns:
        matches = list(re.finditer(pattern, text))
        if matches:
            for match in matches:
                citations.append(Entity(
                    text=match.group(),
                    entity_type="CITATION",
                    count=1,
                    positions=[match.start()]
                ))
    
    return citations


def extract_all_entities(text: str) -> Dict[str, List[Entity]]:
    return {
        "methods": extract_research_methods(text),
        "technical_terms": extract_technical_terms(text),
        "institutions": extract_institutions(text),
        "software": extract_software_tools(text),
        "datasets": extract_datasets(text),
        "metrics": extract_metrics(text),
        "citations": extract_citations(text)
    }


def get_entity_summary(entities: Dict[str, List[Entity]]) -> Dict[str, Dict]:
    summary = {}
    
    for entity_type, entity_list in entities.items():
        total_count = sum(e.count for e in entity_list)
        unique_count = len(entity_list)
        top_entities = [
            {"text": e.text, "count": e.count}
            for e in entity_list[:10]
        ]
        
        summary[entity_type] = {
            "total_mentions": total_count,
            "unique_entities": unique_count,
            "top_entities": top_entities
        }
    
    return summary


def extract_author_names(text: str) -> List[str]:
    author_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b"
    matches = re.findall(author_pattern, text)
    
    common_words = {
        "The", "This", "That", "These", "Those", "However", "Therefore",
        "Furthermore", "Moreover", "Nevertheless", "Consequently", "Subsequently",
        "Introduction", "Method", "Methodology", "Results", "Discussion",
        "Conclusion", "Abstract", "References", "Acknowledgments", "Appendix",
        "Figure", "Table", "Equation", "Algorithm", "Dataset", "Data"
    }
    
    authors = [m for m in matches if m.split()[0] not in common_words and len(m.split()) <= 3]
    
    author_counts = Counter(authors)
    unique_authors = list(author_counts.keys())[:20]
    
    return unique_authors


def extract_research_questions(text: str) -> List[str]:
    question_patterns = [
        r"(?:research question|hypothesis|question)[s:]?\s*(?:is|are|was|were)?\s*([^.!?]+)",
        r"(?:we ask|we investigate|we examine|this paper asks)\s*([^.!?]+)",
        r"(?:whether|how|what|why|which|when)\s+[^.!?]+\?",
    ]
    
    questions = []
    for pattern in question_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        questions.extend(matches)
    
    questions = [q.strip() for q in questions if len(q.strip()) > 10]
    return questions[:10]


def extract_contributions(text: str) -> List[str]:
    contribution_patterns = [
        r"(?:contribution|contributions|propose|introduce|present)[s:]?\s*(?:is|are|was|were)?\s*([^.!?]+)",
        r"(?:our main|the main|our primary)\s*(?:contribution|goal|objective)\s*(?:is|was)\s*([^.!?]+)",
        r"(?:we propose|we introduce|we present|we develop)\s+([^.!?]+)",
    ]
    
    contributions = []
    for pattern in contribution_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        contributions.extend(matches)
    
    contributions = [c.strip() for c in contributions if len(c.strip()) > 10]
    return contributions[:10]


def analyze_entities_full(text: str) -> Dict:
    entities = extract_all_entities(text)
    summary = get_entity_summary(entities)
    
    authors = extract_author_names(text)
    research_questions = extract_research_questions(text)
    contributions = extract_contributions(text)
    
    return {
        "entities": summary,
        "authors": authors,
        "research_questions": research_questions,
        "contributions": contributions,
        "entity_counts": {
            "methods": len(entities["methods"]),
            "technical_terms": len(entities["technical_terms"]),
            "institutions": len(entities["institutions"]),
            "software": len(entities["software"]),
            "datasets": len(entities["datasets"]),
            "metrics": len(entities["metrics"]),
            "citations": len(entities["citations"])
        }
    }
