def get_app_styles():
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #1E3A8A 0%, #7C3AED 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
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
            border-radius: 10px;
            margin-bottom: 0.5rem;
            transition: box-shadow 0.2s ease;
        }
        .stExpander:hover {
            box-shadow: 0 2px 12px rgba(59, 130, 246, 0.15);
        }

        .upload-section {
            background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
        }

        /* Keyword chips */
        .keyword-chip {
            display: inline-block;
            background: linear-gradient(135deg, #DBEAFE 0%, #C7D2FE 100%);
            color: #1E40AF;
            padding: 0.3rem 0.85rem;
            border-radius: 20px;
            margin: 0.2rem;
            font-size: 0.82rem;
            font-weight: 500;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .keyword-chip:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 6px rgba(30, 64, 175, 0.2);
        }
        .keywords-container {
            margin-top: 1rem;
            padding: 1rem;
            background: #F0F9FF;
            border-radius: 10px;
            border-left: 4px solid #3B82F6;
        }

        /* Stat cards */
        .stat-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1rem 1.2rem;
            margin-bottom: 0.6rem;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        .stat-label {
            font-size: 0.78rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }
        .stat-value {
            font-size: 1.55rem;
            font-weight: 700;
            color: #1e293b;
        }

        /* Domain badge */
        .domain-badge {
            display: inline-block;
            background: linear-gradient(135deg, #7C3AED 0%, #6366F1 100%);
            color: white;
            padding: 0.4rem 1.2rem;
            border-radius: 24px;
            font-size: 0.95rem;
            font-weight: 600;
            letter-spacing: 0.3px;
        }

        /* Structural checklist */
        .struct-found {
            display: inline-block;
            background: #D1FAE5;
            color: #065F46;
            padding: 0.25rem 0.7rem;
            border-radius: 8px;
            margin: 0.2rem;
            font-size: 0.82rem;
            font-weight: 500;
        }
        .struct-missing {
            display: inline-block;
            background: #FEE2E2;
            color: #991B1B;
            padding: 0.25rem 0.7rem;
            border-radius: 8px;
            margin: 0.2rem;
            font-size: 0.82rem;
            font-weight: 500;
        }

        /* Summary box */
        .summary-box {
            background: linear-gradient(135deg, #F0F9FF 0%, #EFF6FF 100%);
            border: 1px solid #BFDBFE;
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            margin: 1rem 0;
            line-height: 1.7;
            font-size: 0.95rem;
            color: #1e293b;
        }

        /* Metric score pill */
        .score-pill {
            display: inline-block;
            background: linear-gradient(135deg, #3B82F6 0%, #6366F1 100%);
            color: white;
            padding: 0.15rem 0.6rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-left: 0.5rem;
        }

        .auth-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            background-color: white;
        }

        .stButton button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            transition: transform 0.1s ease;
        }
        .stButton button:hover {
            transform: translateY(-1px);
        }

        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
        }
        section[data-testid="stSidebar"] .stMarkdown {
            color: #E2E8F0;
        }

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            font-weight: 600;
        }
    </style>
    """
