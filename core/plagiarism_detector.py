import logging
import re
import numpy as np
from typing import List, Dict, Tuple, Set
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def split_into_sentences(text: str) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 20]


def generate_ngrams(text: str, n: int = 3) -> Set[str]:
    words = text.lower().split()
    ngrams = set()
    for i in range(len(words) - n + 1):
        ngram = ' '.join(words[i:i+n])
        ngrams.add(ngram)
    return ngrams


def calculate_ngram_overlap(text1: str, text2: str, n: int = 3) -> float:
    ngrams1 = generate_ngrams(text1, n)
    ngrams2 = generate_ngrams(text2, n)
    
    if not ngrams1 or not ngrams2:
        return 0.0
    
    intersection = ngrams1 & ngrams2
    union = ngrams1 | ngrams2
    
    return len(intersection) / len(union) if union else 0.0


def detect_sentence_similarity(sentences: List[str], threshold: float = 0.75) -> List[Dict]:
    if len(sentences) < 2:
        return []
    
    suspicious_pairs = []
    
    try:
        vectorizer = TfidfVectorizer(stop_words='english', min_df=1)
        tfidf_matrix = vectorizer.fit_transform(sentences)
        
        for i in range(len(sentences)):
            for j in range(i + 1, len(sentences)):
                similarity = cosine_similarity(tfidf_matrix[i:i+1], tfidf_matrix[j:j+1])[0][0]
                
                if similarity >= threshold:
                    suspicious_pairs.append({
                        'sentence_1_index': i,
                        'sentence_2_index': j,
                        'sentence_1': sentences[i][:200],
                        'sentence_2': sentences[j][:200],
                        'similarity': round(float(similarity), 4),
                        'type': 'self_plagiarism'
                    })
    except Exception as e:
        logger.error(f"Error in sentence similarity detection: {e}")
    
    return suspicious_pairs


def detect_paraphrasing(text: str) -> List[Dict]:
    sentences = split_into_sentences(text)
    paraphrase_candidates = []
    
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            ngram_overlap = calculate_ngram_overlap(sentences[i], sentences[j], n=4)
            
            if 0.3 <= ngram_overlap < 0.7:
                paraphrase_candidates.append({
                    'sentence_1_index': i,
                    'sentence_2_index': j,
                    'sentence_1': sentences[i][:200],
                    'sentence_2': sentences[j][:200],
                    'ngram_overlap': round(ngram_overlap, 4),
                    'type': 'potential_paraphrase'
                })
    
    return paraphrase_candidates


def detect_common_phrases(text: str) -> Dict:
    common_academic_phrases = [
        r'\bin this paper\b',
        r'\bwe propose\b',
        r'\bour method\b',
        r'\bexperimental results\b',
        r'\bstate of the art\b',
        r'\bfuture work\b',
        r'\bin conclusion\b',
        r'\bthis study\b',
        r'\bour approach\b',
        r'\bwe present\b',
        r'\bwe introduce\b',
        r'\bwe demonstrate\b',
        r'\bour results show\b',
        r'\bwe evaluate\b',
        r'\bwe compare\b',
    ]
    
    text_lower = text.lower()
    phrase_counts = {}
    
    for phrase_pattern in common_academic_phrases:
        matches = re.findall(phrase_pattern, text_lower)
        if matches:
            phrase = phrase_pattern.replace(r'\b', '').replace('\\', '')
            phrase_counts[phrase] = len(matches)
    
    return phrase_counts


def detect_copied_sections(text: str, min_length: int = 100) -> List[Dict]:
    sentences = split_into_sentences(text)
    copied_sections = []
    
    for i in range(len(sentences) - 1):
        for j in range(i + 2, len(sentences)):
            section_1 = ' '.join(sentences[i:i+2])
            section_2 = ' '.join(sentences[j:j+2])
            
            if len(section_1) < min_length or len(section_2) < min_length:
                continue
            
            try:
                vectorizer = TfidfVectorizer(stop_words='english')
                tfidf = vectorizer.fit_transform([section_1, section_2])
                similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
                
                if similarity >= 0.85:
                    copied_sections.append({
                        'section_1_start': i,
                        'section_2_start': j,
                        'section_1': section_1[:300],
                        'section_2': section_2[:300],
                        'similarity': round(float(similarity), 4),
                        'type': 'copied_section'
                    })
            except:
                continue
    
    return copied_sections


def calculate_plagiarism_score(
    sentence_matches: List[Dict],
    paraphrase_matches: List[Dict],
    copied_sections: List[Dict],
    total_sentences: int
) -> Dict:
    if total_sentences == 0:
        return {
            'overall_score': 0.0,
            'risk_level': 'none',
            'affected_sentences': 0,
            'affected_percentage': 0.0
        }
    
    affected_sentence_indices = set()
    
    for match in sentence_matches:
        affected_sentence_indices.add(match['sentence_1_index'])
        affected_sentence_indices.add(match['sentence_2_index'])
    
    for match in paraphrase_matches:
        affected_sentence_indices.add(match['sentence_1_index'])
        affected_sentence_indices.add(match['sentence_2_index'])
    
    for section in copied_sections:
        affected_sentence_indices.add(section['section_1_start'])
        affected_sentence_indices.add(section['section_2_start'])
    
    affected_count = len(affected_sentence_indices)
    affected_percentage = (affected_count / total_sentences) * 100
    
    high_similarity_count = sum(1 for m in sentence_matches if m['similarity'] >= 0.9)
    section_count = len(copied_sections)
    
    score = min(100, (
        (affected_percentage * 0.5) +
        (high_similarity_count * 2) +
        (section_count * 5) +
        (len(paraphrase_matches) * 0.5)
    ))
    
    if score >= 30:
        risk_level = 'high'
    elif score >= 15:
        risk_level = 'medium'
    elif score >= 5:
        risk_level = 'low'
    else:
        risk_level = 'minimal'
    
    return {
        'overall_score': round(score, 2),
        'risk_level': risk_level,
        'affected_sentences': affected_count,
        'affected_percentage': round(affected_percentage, 2)
    }


def analyze_plagiarism(text: str, reference_texts: List[str] = None) -> Dict:
    sentences = split_into_sentences(text)
    total_sentences = len(sentences)
    
    if total_sentences < 5:
        return {
            'error': 'Document too short for plagiarism analysis',
            'total_sentences': total_sentences
        }
    
    sentence_matches = detect_sentence_similarity(sentences, threshold=0.75)
    
    paraphrase_matches = detect_paraphrasing(text)
    
    copied_sections = detect_copied_sections(text, min_length=100)
    
    common_phrases = detect_common_phrases(text)
    
    plagiarism_score = calculate_plagiarism_score(
        sentence_matches,
        paraphrase_matches,
        copied_sections,
        total_sentences
    )
    
    external_matches = []
    if reference_texts:
        external_matches = compare_with_references(text, reference_texts)
    
    recommendations = generate_recommendations(
        plagiarism_score,
        len(sentence_matches),
        len(paraphrase_matches),
        len(copied_sections)
    )
    
    return {
        'plagiarism_score': plagiarism_score,
        'total_sentences': total_sentences,
        'self_similarity_matches': sentence_matches[:10],
        'paraphrase_candidates': paraphrase_matches[:10],
        'copied_sections': copied_sections[:5],
        'common_phrases': common_phrases,
        'external_matches': external_matches[:10],
        'statistics': {
            'total_self_matches': len(sentence_matches),
            'total_paraphrase_candidates': len(paraphrase_matches),
            'total_copied_sections': len(copied_sections),
            'total_external_matches': len(external_matches)
        },
        'recommendations': recommendations
    }


def compare_with_references(text: str, reference_texts: List[str]) -> List[Dict]:
    sentences = split_into_sentences(text)
    matches = []
    
    for ref_idx, ref_text in enumerate(reference_texts):
        ref_sentences = split_into_sentences(ref_text)
        
        try:
            all_sentences = sentences + ref_sentences
            vectorizer = TfidfVectorizer(stop_words='english', min_df=1)
            tfidf_matrix = vectorizer.fit_transform(all_sentences)
            
            for i in range(len(sentences)):
                for j in range(len(ref_sentences)):
                    ref_j = len(sentences) + j
                    similarity = cosine_similarity(
                        tfidf_matrix[i:i+1],
                        tfidf_matrix[ref_j:ref_j+1]
                    )[0][0]
                    
                    if similarity >= 0.8:
                        matches.append({
                            'sentence_index': i,
                            'sentence': sentences[i][:200],
                            'reference_index': ref_idx,
                            'reference_sentence': ref_sentences[j][:200],
                            'similarity': round(float(similarity), 4),
                            'type': 'external_match'
                        })
        except Exception as e:
            logger.error(f"Error comparing with reference {ref_idx}: {e}")
            continue
    
    matches.sort(key=lambda x: x['similarity'], reverse=True)
    return matches


def generate_recommendations(
    plagiarism_score: Dict,
    self_matches: int,
    paraphrase_count: int,
    copied_sections: int
) -> List[str]:
    recommendations = []
    
    risk_level = plagiarism_score['risk_level']
    
    if risk_level == 'high':
        recommendations.append('HIGH RISK: Significant similarity detected. Review and revise affected sections.')
    elif risk_level == 'medium':
        recommendations.append('MEDIUM RISK: Moderate similarity found. Consider rephrasing similar sections.')
    elif risk_level == 'low':
        recommendations.append('LOW RISK: Minor similarities detected. Review flagged sections.')
    else:
        recommendations.append('MINIMAL RISK: Document appears original with standard academic phrasing.')
    
    if self_matches > 10:
        recommendations.append(f'Found {self_matches} self-similar sentences. Reduce repetition and redundancy.')
    
    if paraphrase_count > 5:
        recommendations.append(f'Detected {paraphrase_count} potential paraphrases. Ensure proper citation.')
    
    if copied_sections > 0:
        recommendations.append(f'Found {copied_sections} copied sections. These require immediate attention.')
    
    if plagiarism_score['affected_percentage'] > 20:
        recommendations.append('More than 20% of sentences flagged. Consider major revision.')
    
    recommendations.append('Always cite sources properly and use quotation marks for direct quotes.')
    recommendations.append('Use paraphrasing tools responsibly and verify originality.')
    
    return recommendations


def generate_plagiarism_report(analysis_result: Dict) -> str:
    if 'error' in analysis_result:
        return analysis_result['error']
    
    score = analysis_result['plagiarism_score']
    stats = analysis_result['statistics']
    
    report = f"Plagiarism Analysis Report\n"
    report += f"{'=' * 50}\n\n"
    report += f"Overall Score: {score['overall_score']}/100\n"
    report += f"Risk Level: {score['risk_level'].upper()}\n"
    report += f"Affected Sentences: {score['affected_sentences']} ({score['affected_percentage']}%)\n"
    report += f"Total Sentences Analyzed: {analysis_result['total_sentences']}\n\n"
    
    report += f"Detection Statistics:\n"
    report += f"  - Self-similarity matches: {stats['total_self_matches']}\n"
    report += f"  - Paraphrase candidates: {stats['total_paraphrase_candidates']}\n"
    report += f"  - Copied sections: {stats['total_copied_sections']}\n"
    report += f"  - External matches: {stats['total_external_matches']}\n\n"
    
    report += f"Recommendations:\n"
    for i, rec in enumerate(analysis_result['recommendations'], 1):
        report += f"  {i}. {rec}\n"
    
    return report
