def get_app_styles():
    return """
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1E3A8A;
            text-align: center;
            padding: 1rem 0;
            border-bottom: 3px solid #3B82F6;
            margin-bottom: 2rem;
        }
        .section-header {
            font-size: 1.5rem;
            font-weight: 600;
            color: #1E40AF;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }
        .stExpander {
            border: 1px solid #DBEAFE;
            border-radius: 8px;
            margin-bottom: 0.5rem;
        }
        .upload-section {
            background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
        }
        .keyword-chip {
            display: inline-block;
            background: #DBEAFE;
            color: #1E40AF;
            padding: 0.25rem 0.75rem;
            border-radius: 16px;
            margin: 0.25rem;
            font-size: 0.875rem;
            font-weight: 500;
        }
        .keywords-container {
            margin-top: 1rem;
            padding: 1rem;
            background: #F0F9FF;
            border-radius: 8px;
            border-left: 4px solid #3B82F6;
        }
        .auth-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background-color: white;
        }
        .stButton button {
            width: 100%;
            border-radius: 5px;
            font-weight: 600;
        }
    </style>
    """
