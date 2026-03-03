import logging
import re
from typing import List, Dict, Set, Tuple
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_limitations(text: str) -> List[str]:
    text_lower = text.lower()
    limitations = []
    
    limitation_patterns = [
        r'(?:limitation|limited|constraint|drawback|shortcoming)[s]?\s+(?:of|in|is|are|include)[^.!?]{10,200}[.!?]',
        r'(?:however|unfortunately|regrettably),?\s+[^.!?]{10,200}[.!?]',
        r'(?:cannot|unable to|failed to|did not)[^.!?]{10,200}[.!?]',
        r'(?:future work|further research|additional study)[^.!?]{10,200}[.!?]',
        r'(?:scope of this|beyond the scope)[^.!?]{10,200}[.!?]',
    ]
    
    for pattern in limitation_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            clean_match = match.strip()
            if 20 < len(clean_match) < 300:
                limitations.append(clean_match)
    
    return list(set(limitations))[:10]


def identify_research_gaps(text: str, domain: str) -> List[Dict]:
    gaps = []
    text_lower = text.lower()
    
    gap_indicators = [
        'not yet explored',
        'remains unclear',
        'little is known',
        'poorly understood',
        'requires further investigation',
        'warrants additional research',
        'has not been studied',
        'gap in the literature',
        'unexplored area',
        'open question',
        'future research',
        'needs to be addressed',
        'remains to be seen',
        'insufficient evidence',
        'lack of research',
    ]
    
    for indicator in gap_indicators:
        if indicator in text_lower:
            context_pattern = r'.{0,100}' + re.escape(indicator) + r'.{0,100}'
            matches = re.findall(context_pattern, text_lower, re.IGNORECASE)
            
            for match in matches:
                gaps.append({
                    'indicator': indicator,
                    'context': match.strip(),
                    'type': 'explicit_gap',
                    'confidence': 'high'
                })
    
    missing_methods = detect_missing_methodologies(text, domain)
    for method in missing_methods:
        gaps.append({
            'indicator': 'missing_methodology',
            'context': f'Could explore {method} approach',
            'type': 'methodological_gap',
            'confidence': 'medium'
        })
    
    return gaps[:15]


def detect_missing_methodologies(text: str, domain: str) -> List[str]:
    text_lower = text.lower()
    missing = []
    
    methodology_sets = {
        'Computer Science': [
            'deep learning', 'reinforcement learning', 'transfer learning',
            'ensemble methods', 'neural architecture search', 'meta-learning',
            'federated learning', 'adversarial training', 'self-supervised learning'
        ],
        'Biology / Medicine': [
            'randomized controlled trial', 'meta-analysis', 'cohort study',
            'case-control study', 'systematic review', 'genome-wide association',
            'proteomics', 'metabolomics', 'single-cell analysis'
        ],
        'Physics': [
            'monte carlo simulation', 'molecular dynamics', 'density functional theory',
            'finite element analysis', 'lattice boltzmann', 'quantum monte carlo'
        ],
        'Mathematics / Statistics': [
            'bayesian inference', 'markov chain monte carlo', 'bootstrap',
            'cross-validation', 'regularization', 'dimensionality reduction'
        ]
    }
    
    methods = methodology_sets.get(domain, [])
    
    for method in methods:
        if method not in text_lower:
            missing.append(method)
    
    return missing[:5]


def analyze_trends_and_directions(keywords: List[Tuple[str, float]], domain: str) -> List[Dict]:
    directions = []
    
    emerging_topics = {
        'Computer Science': [
            'explainable AI', 'edge computing', 'quantum machine learning',
            'neuromorphic computing', 'green AI', 'few-shot learning',
            'continual learning', 'multimodal learning', 'graph neural networks'
        ],
        'Biology / Medicine': [
            'precision medicine', 'immunotherapy', 'gene editing',
            'microbiome research', 'organoid technology', 'liquid biopsy',
            'digital health', 'personalized treatment', 'biomarker discovery'
        ],
        'Physics': [
            'quantum computing', 'topological materials', 'metamaterials',
            'spintronics', 'photonics', 'plasma physics applications'
        ],
        'Mathematics / Statistics': [
            'causal inference', 'topological data analysis', 'optimal transport',
            'tensor methods', 'high-dimensional statistics', 'network analysis'
        ]
    }
    
    topics = emerging_topics.get(domain, [])
    keyword_texts = [kw[0].lower() for kw in keywords]
    
    for topic in topics:
        topic_words = topic.lower().split()
        relevance = sum(1 for kw in keyword_texts if any(tw in kw for tw in topic_words))
        
        if relevance > 0:
            directions.append({
                'topic': topic,
                'relevance_score': relevance,
                'category': 'emerging_trend',
                'rationale': f'Related to current work through {relevance} keyword matches'
            })
    
    return sorted(directions, key=lambda x: x['relevance_score'], reverse=True)[:8]


def generate_research_questions(gaps: List[Dict], domain: str, keywords: List[Tuple[str, float]]) -> List[str]:
    questions = []
    
    top_keywords = [kw[0] for kw in keywords[:5]]
    
    question_templates = [
        f"How can {top_keywords[0] if top_keywords else 'the proposed method'} be extended to address {domain.lower()} challenges?",
        f"What are the implications of combining {top_keywords[0] if top_keywords else 'this approach'} with {top_keywords[1] if len(top_keywords) > 1 else 'alternative methods'}?",
        f"Can {top_keywords[0] if top_keywords else 'the methodology'} be applied to real-world {domain.lower()} applications?",
        "How does the approach scale to larger datasets or more complex scenarios?",
        "What are the theoretical foundations that could strengthen this work?",
    ]
    
    for gap in gaps[:3]:
        if gap['type'] == 'explicit_gap':
            context = gap['context'][:100]
            questions.append(f"How can we address: {context}?")
    
    questions.extend(question_templates[:5 - len(questions)])
    
    return questions[:8]


def suggest_methodological_improvements(text: str, scores: Dict, domain: str) -> List[Dict]:
    suggestions = []
    
    if scores.get('Technical Depth', 0) < 60:
        suggestions.append({
            'area': 'Technical Depth',
            'suggestion': 'Incorporate more advanced mathematical formulations or algorithmic details',
            'priority': 'high',
            'expected_impact': 'Increase rigor and reproducibility'
        })
    
    if scores.get('Novelty Signal', 0) < 50:
        suggestions.append({
            'area': 'Novelty',
            'suggestion': 'Clearly articulate unique contributions and compare with state-of-the-art',
            'priority': 'high',
            'expected_impact': 'Strengthen positioning and impact'
        })
    
    if scores.get('Citation Density', 0) < 40:
        suggestions.append({
            'area': 'Literature Review',
            'suggestion': 'Expand related work section with recent publications and seminal papers',
            'priority': 'medium',
            'expected_impact': 'Better contextualization'
        })
    
    text_lower = text.lower()
    
    if 'ablation' not in text_lower and domain == 'Computer Science':
        suggestions.append({
            'area': 'Experimental Design',
            'suggestion': 'Add ablation studies to validate component contributions',
            'priority': 'medium',
            'expected_impact': 'Demonstrate component importance'
        })
    
    if 'statistical significance' not in text_lower and 'p-value' not in text_lower:
        suggestions.append({
            'area': 'Statistical Analysis',
            'suggestion': 'Include statistical significance tests and confidence intervals',
            'priority': 'medium',
            'expected_impact': 'Strengthen empirical claims'
        })
    
    if 'limitation' not in text_lower:
        suggestions.append({
            'area': 'Discussion',
            'suggestion': 'Add explicit discussion of limitations and boundary conditions',
            'priority': 'low',
            'expected_impact': 'Increase transparency and credibility'
        })
    
    return suggestions


def generate_collaboration_opportunities(domain: str, keywords: List[Tuple[str, float]]) -> List[Dict]:
    opportunities = []
    
    interdisciplinary_connections = {
        'Computer Science': ['Biology', 'Medicine', 'Physics', 'Social Sciences', 'Economics'],
        'Biology / Medicine': ['Computer Science', 'Engineering', 'Chemistry', 'Statistics'],
        'Physics': ['Computer Science', 'Engineering', 'Mathematics', 'Materials Science'],
        'Mathematics / Statistics': ['Computer Science', 'Economics', 'Biology', 'Physics'],
        'Economics / Finance': ['Computer Science', 'Mathematics', 'Social Sciences', 'Policy']
    }
    
    related_fields = interdisciplinary_connections.get(domain, [])
    
    for field in related_fields[:3]:
        opportunities.append({
            'field': field,
            'type': 'interdisciplinary',
            'rationale': f'Combine {domain} methods with {field} applications',
            'potential_impact': 'high'
        })
    
    keyword_texts = ' '.join([kw[0] for kw in keywords[:10]]).lower()
    
    if 'data' in keyword_texts or 'learning' in keyword_texts:
        opportunities.append({
            'field': 'Data Science',
            'type': 'methodological',
            'rationale': 'Leverage data-driven approaches for enhanced analysis',
            'potential_impact': 'medium'
        })
    
    if 'model' in keyword_texts or 'simulation' in keyword_texts:
        opportunities.append({
            'field': 'Computational Modeling',
            'type': 'methodological',
            'rationale': 'Develop computational models for prediction and validation',
            'potential_impact': 'medium'
        })
    
    return opportunities[:5]


def suggest_dataset_extensions(text: str, domain: str) -> List[Dict]:
    extensions = []
    text_lower = text.lower()
    
    if domain == 'Computer Science':
        if 'imagenet' in text_lower or 'image' in text_lower:
            extensions.append({
                'dataset_type': 'Image Dataset',
                'suggestion': 'Extend to COCO, Open Images, or domain-specific image datasets',
                'rationale': 'Validate generalization across diverse visual domains'
            })
        
        if 'text' in text_lower or 'language' in text_lower:
            extensions.append({
                'dataset_type': 'Text Dataset',
                'suggestion': 'Test on multilingual corpora or domain-specific text collections',
                'rationale': 'Assess cross-lingual and domain transfer capabilities'
            })
    
    if 'small' in text_lower or 'limited data' in text_lower:
        extensions.append({
            'dataset_type': 'Scale Extension',
            'suggestion': 'Evaluate on larger-scale datasets to test scalability',
            'rationale': 'Demonstrate practical applicability to real-world scenarios'
        })
    
    extensions.append({
        'dataset_type': 'Benchmark Suite',
        'suggestion': 'Create comprehensive benchmark suite for systematic evaluation',
        'rationale': 'Enable standardized comparison with future methods'
    })
    
    return extensions[:5]


def generate_future_research_directions(
    text: str,
    sections: Dict,
    scores: Dict,
    stats: Dict,
    keywords: List[Tuple[str, float]],
    domain: str
) -> Dict:
    
    limitations = extract_limitations(text)
    
    gaps = identify_research_gaps(text, domain)
    
    trends = analyze_trends_and_directions(keywords, domain)
    
    research_questions = generate_research_questions(gaps, domain, keywords)
    
    methodological_improvements = suggest_methodological_improvements(text, scores, domain)
    
    collaboration_opportunities = generate_collaboration_opportunities(domain, keywords)
    
    dataset_extensions = suggest_dataset_extensions(text, domain)
    
    short_term = []
    medium_term = []
    long_term = []
    
    for improvement in methodological_improvements:
        if improvement['priority'] == 'high':
            short_term.append(improvement['suggestion'])
        else:
            medium_term.append(improvement['suggestion'])
    
    for gap in gaps[:3]:
        if gap['confidence'] == 'high':
            short_term.append(f"Address: {gap['context'][:100]}")
    
    for trend in trends[:3]:
        medium_term.append(f"Explore {trend['topic']} integration")
    
    for opportunity in collaboration_opportunities[:2]:
        long_term.append(f"Develop {opportunity['field']} collaboration for {opportunity['rationale']}")
    
    for extension in dataset_extensions[:2]:
        medium_term.append(extension['suggestion'])
    
    priority_directions = []
    
    if scores.get('Novelty Signal', 0) < 50:
        priority_directions.append({
            'direction': 'Strengthen novelty claims',
            'rationale': 'Low novelty score indicates need for clearer contribution statements',
            'timeline': 'immediate',
            'difficulty': 'low'
        })
    
    if scores.get('Technical Depth', 0) < 60:
        priority_directions.append({
            'direction': 'Enhance technical rigor',
            'rationale': 'Add mathematical proofs, complexity analysis, or theoretical foundations',
            'timeline': 'short-term',
            'difficulty': 'medium'
        })
    
    if len(gaps) > 5:
        priority_directions.append({
            'direction': 'Address identified research gaps',
            'rationale': f'Multiple gaps detected ({len(gaps)} total) provide clear research opportunities',
            'timeline': 'medium-term',
            'difficulty': 'medium'
        })
    
    for trend in trends[:2]:
        priority_directions.append({
            'direction': f'Integrate {trend["topic"]}',
            'rationale': trend['rationale'],
            'timeline': 'medium-term',
            'difficulty': 'high'
        })
    
    return {
        'limitations': limitations,
        'research_gaps': gaps,
        'emerging_trends': trends,
        'research_questions': research_questions,
        'methodological_improvements': methodological_improvements,
        'collaboration_opportunities': collaboration_opportunities,
        'dataset_extensions': dataset_extensions,
        'timeline': {
            'short_term': short_term[:5],
            'medium_term': medium_term[:5],
            'long_term': long_term[:3]
        },
        'priority_directions': priority_directions,
        'summary': generate_summary(
            len(limitations),
            len(gaps),
            len(trends),
            len(priority_directions)
        )
    }


def generate_summary(limitation_count: int, gap_count: int, trend_count: int, priority_count: int) -> str:
    summary = f"Identified {limitation_count} limitations, {gap_count} research gaps, "
    summary += f"and {trend_count} emerging trends. "
    summary += f"Generated {priority_count} priority research directions for future work."
    return summary
