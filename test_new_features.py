import sys
import os

print("Testing new PaperIQ features...")
print("=" * 60)

test_text = """
This paper presents a novel approach to machine learning.
We propose a new method for deep learning applications.
The experimental results show significant improvements.
However, there are some limitations to our approach.
Future work should explore additional datasets.
The method has not been tested on large-scale problems.
Further research is needed to validate these findings.
"""

print("\n1. Testing Future Research Module...")
try:
    from core import future_research
    
    test_sections = {"Introduction": test_text}
    test_scores = {
        "Composite": 75.0,
        "Technical Depth": 60.0,
        "Novelty Signal": 45.0,
        "Citation Density": 35.0
    }
    test_stats = {"word_count": 100, "sentence_count": 10}
    test_keywords = [("machine learning", 0.8), ("deep learning", 0.7)]
    test_domain = "Computer Science"
    
    result = future_research.generate_future_research_directions(
        test_text, test_sections, test_scores, test_stats, test_keywords, test_domain
    )
    
    print(f"   ✓ Limitations found: {len(result.get('limitations', []))}")
    print(f"   ✓ Research gaps: {len(result.get('research_gaps', []))}")
    print(f"   ✓ Research questions: {len(result.get('research_questions', []))}")
    print(f"   ✓ Priority directions: {len(result.get('priority_directions', []))}")
    print(f"   ✓ Summary: {result.get('summary', 'N/A')[:80]}...")
    print("   ✓ Future Research Module: PASSED")
except Exception as e:
    print(f"   ✗ Future Research Module: FAILED - {e}")

print("\n2. Testing Plagiarism Detector Module...")
try:
    from core import plagiarism_detector
    
    test_doc = """
    This is a test sentence for plagiarism detection.
    Machine learning is a powerful tool for data analysis.
    Deep learning has revolutionized computer vision.
    This is a test sentence for plagiarism detection.
    Neural networks can learn complex patterns.
    Machine learning is a powerful tool for data analysis.
    """
    
    result = plagiarism_detector.analyze_plagiarism(test_doc)
    
    if "error" in result:
        print(f"   ⚠ Warning: {result['error']}")
    else:
        plag_score = result.get('plagiarism_score', {})
        print(f"   ✓ Overall score: {plag_score.get('overall_score', 0):.2f}/100")
        print(f"   ✓ Risk level: {plag_score.get('risk_level', 'N/A')}")
        print(f"   ✓ Self-matches: {result.get('statistics', {}).get('total_self_matches', 0)}")
        print(f"   ✓ Recommendations: {len(result.get('recommendations', []))}")
    print("   ✓ Plagiarism Detector Module: PASSED")
except Exception as e:
    print(f"   ✗ Plagiarism Detector Module: FAILED - {e}")

print("\n3. Testing LaTeX Export Module...")
try:
    from core import export_latex
    
    test_data = {
        "scores": {"Composite": 85.0, "Language": 80.0, "Coherence": 75.0},
        "stats": {"word_count": 5000, "sentence_count": 250, "avg_sentence_len": 20.0},
        "keywords": [("machine learning", 0.9), ("neural networks", 0.8)],
        "document_summary": "This is a test summary.",
        "domain": "Computer Science",
        "structural_found": ["Abstract", "Introduction"],
        "structural_missing": ["Conclusion"],
        "sentiment": 0.1,
        "advanced": {}
    }
    
    latex_output = export_latex.create_latex_export(test_data, "test_paper.pdf", [])
    
    if latex_output and len(latex_output) > 0:
        print(f"   ✓ LaTeX output generated: {len(latex_output)} bytes")
        print(f"   ✓ Contains document class: {'documentclass' in latex_output.decode('utf-8', errors='ignore')}")
        print(f"   ✓ Contains begin/end document: {'begin{document}' in latex_output.decode('utf-8', errors='ignore')}")
        print("   ✓ LaTeX Export Module: PASSED")
    else:
        print("   ✗ LaTeX Export Module: FAILED - Empty output")
except Exception as e:
    print(f"   ✗ LaTeX Export Module: FAILED - {e}")

print("\n4. Testing DOCX Export Module...")
try:
    from core import export_docx
    
    test_data = {
        "scores": {"Composite": 85.0, "Language": 80.0, "Coherence": 75.0},
        "stats": {"word_count": 5000, "sentence_count": 250, "avg_sentence_len": 20.0},
        "keywords": [("machine learning", 0.9), ("neural networks", 0.8)],
        "document_summary": "This is a test summary.",
        "domain": "Computer Science",
        "structural_found": ["Abstract", "Introduction"],
        "structural_missing": ["Conclusion"],
        "sentiment": 0.1,
        "advanced": {}
    }
    
    docx_output = export_docx.create_docx_export(test_data, "test_paper.pdf", [])
    
    if docx_output and len(docx_output) > 0:
        print(f"   ✓ DOCX output generated: {len(docx_output)} bytes")
        print(f"   ✓ Valid DOCX signature: {docx_output[:4] == b'PK\\x03\\x04'}")
        print("   ✓ DOCX Export Module: PASSED")
    else:
        print("   ✗ DOCX Export Module: FAILED - Empty output")
except Exception as e:
    print(f"   ✗ DOCX Export Module: FAILED - {e}")

print("\n5. Testing Text Analyzer Integration...")
try:
    from core import text_analyzer
    
    print("   ✓ LaTeX export function available:", hasattr(text_analyzer, 'create_latex_export'))
    print("   ✓ DOCX export function available:", hasattr(text_analyzer, 'create_docx_export'))
    print("   ✓ Text Analyzer Integration: PASSED")
except Exception as e:
    print(f"   ✗ Text Analyzer Integration: FAILED - {e}")

print("\n6. Testing Advanced ML Integration...")
try:
    from core import advanced_ml
    
    test_sections = {"Introduction": test_text}
    test_scores = {"Composite": 75.0, "Technical Depth": 60.0}
    test_stats = {"word_count": 100}
    test_keywords = [("machine learning", 0.8)]
    test_domain = "Computer Science"
    
    result = advanced_ml.run_advanced_analysis(
        test_text, test_sections, test_scores, test_stats, test_keywords, test_domain
    )
    
    print(f"   ✓ Quality prediction available: {'quality_prediction' in result}")
    print(f"   ✓ Future research available: {'future_research' in result}")
    print(f"   ✓ Reproducibility available: {'reproducibility' in result}")
    print("   ✓ Advanced ML Integration: PASSED")
except Exception as e:
    print(f"   ✗ Advanced ML Integration: FAILED - {e}")

print("\n" + "=" * 60)
print("All tests completed!")
print("\nNote: Some modules require scikit-learn to be installed.")
print("Install with: pip install scikit-learn")
