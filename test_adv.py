from core import advanced_ml

r = advanced_ml.run_advanced_analysis(
    'This is a test paper about machine learning. We propose a novel architecture.',
    {'Introduction': 'test'}, 
    {'Technical Depth': 50, 'Novelty Signal': 60, 'Coherence': 70, 'Language': 65, 
     'Readability': 55, 'Reasoning': 60, 'Structural Completeness': 80, 
     'Citation Density': 40, 'Vocabulary Richness': 50}, 
    {'word_count': 100, 'sentence_count': 5, 'citation_density_per_1k': 5, 
     'type_token_ratio': 0.5, 'complex_word_ratio': 0.2}, 
    [], 'CS'
)

with open('test_output.txt', 'w') as f:
    f.write("=== KEYS ===\n")
    f.write(str(list(r.keys())) + "\n\n")
    for key in r:
        val = r[key]
        if isinstance(val, dict):
            f.write(f"{key}: has_data={bool(val)} keys={list(val.keys())}\n")
        else:
            f.write(f"{key}: {val}\n")
