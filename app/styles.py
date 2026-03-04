def get_app_styles():
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .main-header {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            padding: 1.5rem 0;
            margin-bottom: 2rem;
            letter-spacing: -1px;
        }

        .sub-header {
            font-size: 1.2rem;
            font-weight: 500;
            color: #64748b;
            text-align: center;
            margin-bottom: 2rem;
        }

        .section-header {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1e293b;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e2e8f0;
        }

        .stExpander {
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            margin-bottom: 0.75rem;
            transition: all 0.2s ease;
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            color: #1e293b !important;
        }
        .stExpander summary p {
            color: #1e293b !important;
            font-weight: 600 !important;
        }
        .stExpander:hover {
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border-color: #667eea;
        }

        .upload-section {
            background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%);
            padding: 2.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            border: 2px dashed #667eea;
        }

        .keyword-chip {
            display: inline-block;
            background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
            color: #3730a3 !important;
            padding: 0.4rem 1rem;
            border-radius: 20px;
            margin: 0.25rem;
            font-size: 0.85rem;
            font-weight: 600;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .keyword-chip:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        .keywords-container {
            margin-top: 1rem;
            padding: 1.25rem;
            background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
            border-radius: 12px;
            border-left: 4px solid #9333ea;
            color: #1e293b !important;
        }

        .stat-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 0.75rem;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            color: #1e293b !important;
        }
        .stat-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            border-color: #667eea;
        }
        .stat-label {
            font-size: 0.75rem;
            color: #64748b !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        .stat-value {
            font-size: 1.75rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .domain-badge {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.5rem 1.5rem;
            border-radius: 25px;
            font-size: 0.95rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        .struct-found {
            display: inline-block;
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            color: #065f46;
            padding: 0.35rem 0.85rem;
            border-radius: 10px;
            margin: 0.25rem;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .struct-missing {
            display: inline-block;
            background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
            color: #991b1b;
            padding: 0.35rem 0.85rem;
            border-radius: 10px;
            margin: 0.25rem;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .summary-box {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border: 1px solid #bae6fd;
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin: 1rem 0;
            line-height: 1.8;
            font-size: 0.95rem;
            color: #0c4a6e !important;
        }

        .score-pill {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.2rem 0.75rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 700;
            margin-left: 0.5rem;
        }

        .auth-container {
            max-width: 450px;
            margin: 0 auto;
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
        }

        .stButton button {
            width: 100%;
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.2s ease;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            padding: 0.75rem 1.5rem;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        }
        section[data-testid="stSidebar"] .stMarkdown {
            color: #e2e8f0;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px 10px 0 0;
            font-weight: 600;
            padding: 0.75rem 1.5rem;
        }

        .progress-container {
            background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid #c7d2fe;
        }

        .progress-bar {
            width: 100%;
            height: 14px;
            background: #e2e8f0;
            border-radius: 10px;
            overflow: hidden;
            margin: 0.75rem 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            transition: width 0.4s ease;
        }

        .progress-text {
            font-size: 0.9rem;
            color: #3730a3;
            font-weight: 600;
            margin-top: 0.5rem;
        }

        .step-indicator {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 1.5rem 0;
        }

        .step {
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;
            position: relative;
        }

        .step-number {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
            color: #64748b;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1rem;
            margin-bottom: 0.5rem;
            transition: all 0.3s ease;
        }

        .step.active .step-number {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transform: scale(1.1);
        }

        .step.completed .step-number {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
        }

        .step-label {
            font-size: 0.75rem;
            color: #64748b;
            text-align: center;
            max-width: 90px;
        }

        .step.active .step-label {
            color: #3730a3;
            font-weight: 700;
        }

        .step.completed .step-label {
            color: #059669;
        }

        .section-score-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.25rem;
            margin: 0.75rem 0;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            color: #1e293b !important;
        }
        .section-score-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            border-color: #667eea;
        }
        .section-score-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }
        .section-score-name {
            font-size: 0.95rem;
            font-weight: 700;
            color: #1e293b;
        }
        .section-score-value {
            font-size: 1.4rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .section-score-bar {
            width: 100%;
            height: 10px;
            background: #e2e8f0;
            border-radius: 6px;
            overflow: hidden;
        }
        .section-score-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 6px;
            transition: width 0.5s ease;
        }

        .quality-badge {
            display: inline-block;
            padding: 0.5rem 1.25rem;
            border-radius: 25px;
            font-weight: 700;
            font-size: 1.1rem;
            margin: 0.5rem;
        }
        .quality-a-plus {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            color: #92400e;
        }
        .quality-a {
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            color: #065f46;
        }
        .quality-b {
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
            color: #1e40af;
        }
        .quality-c {
            background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
            color: #9a3412;
        }

        .insight-card {
            background: linear-gradient(135deg, #ffffff 0%, #faf5ff 100%);
            border: 1px solid #e9d5ff;
            border-radius: 14px;
            padding: 1.25rem;
            margin: 0.75rem 0;
            border-left: 4px solid #9333ea;
            color: #581c87 !important;
        }

        .warning-card {
            background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
            border: 1px solid #fdba74;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #ea580c;
            color: #9a3412 !important;
        }

        .success-card {
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border: 1px solid #86efac;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #16a34a;
            color: #166534 !important;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }

        .entity-tag {
            display: inline-block;
            background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
            color: #475569;
            padding: 0.35rem 0.85rem;
            border-radius: 8px;
            margin: 0.2rem;
            font-size: 0.8rem;
            font-weight: 500;
            border: 1px solid #cbd5e1;
        }

        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            border-radius: 12px;
            overflow: hidden;
        }
        .comparison-table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            font-weight: 600;
        }
        .comparison-table td {
            padding: 0.75rem;
            border-bottom: 1px solid #e2e8f0;
        }
        .comparison-table tr:hover {
            background: #f8fafc;
        }

        .stTextArea label {
            font-weight: 600;
            color: #1e293b;
        }
        .stTextArea textarea {
            background-color: #ffffff !important;
            color: #1e293b !important;
            border: 1px solid #e2e8f0 !important;
        }
        .stExpander .stTextArea textarea {
            background-color: #f8fafc !important;
        }
    </style>
    """
