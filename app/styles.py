def get_app_styles():
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
        }

        @keyframes slideUpFade {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }

        @keyframes shimmer {
            0% { background-position: -200% center; }
            100% { background-position: 200% center; }
        }

        .animate-fade-in {
            animation: slideUpFade 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            opacity: 0;
        }

        .delay-1 { animation-delay: 0.1s; }
        .delay-2 { animation-delay: 0.2s; }
        .delay-3 { animation-delay: 0.3s; }
        .delay-4 { animation-delay: 0.4s; }

        .main .block-container {
            padding-top: 2rem !important;
        }

        .main-header {
            font-size: 3rem !important;
            font-weight: 800 !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
            text-align: center !important;
            padding: 1rem 0 !important;
            margin-bottom: 0.5rem !important;
            letter-spacing: -1px !important;
        }

        .sub-header {
            font-size: 1.1rem !important;
            font-weight: 400 !important;
            color: #94a3b8 !important;
            text-align: center !important;
            margin-bottom: 2rem !important;
        }

        .hero-section {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 40%, #312e81 100%);
            border-radius: 24px;
            padding: 3rem 2.5rem;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }

        .hero-section::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -20%;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(99, 102, 241, 0.3) 0%, transparent 70%);
            border-radius: 50%;
        }

        .hero-section::after {
            content: '';
            position: absolute;
            bottom: -30%;
            left: -10%;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(139, 92, 246, 0.2) 0%, transparent 70%);
            border-radius: 50%;
        }

        .hero-title {
            font-size: 2.8rem !important;
            font-weight: 800 !important;
            color: #ffffff !important;
            margin-bottom: 0.5rem !important;
            letter-spacing: -1px;
            position: relative;
            z-index: 1;
        }

        .hero-title span {
            background: linear-gradient(135deg, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .hero-subtitle {
            font-size: 1.1rem;
            color: #94a3b8 !important;
            margin-bottom: 0;
            position: relative;
            z-index: 1;
            line-height: 1.6;
        }

        .upload-card {
            background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
            border: 2px dashed #6366f1;
            border-radius: 20px;
            padding: 2rem;
            text-align: center;
            margin: 1.5rem 0;
            transition: all 0.3s ease;
        }

        .upload-card:hover {
            border-color: #818cf8;
            box-shadow: 0 0 30px rgba(99, 102, 241, 0.2);
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

        .card-elevated {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
            border: 1px solid #e2e8f0;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }

        .card-elevated:hover {
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
            transform: translateY(-3px);
            border-color: #667eea;
        }

        .stExpander {
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            margin-bottom: 0.75rem !important;
            transition: all 0.2s ease;
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        }
        .stExpander summary p {
            color: #1e293b !important;
            font-weight: 600 !important;
        }
        .stExpander * {
            color: #1e293b !important;
        }
        .stExpander:hover {
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
            border-color: #667eea !important;
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
            transition: all 0.25s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            color: #1e293b !important;
        }
        .stat-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.18);
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
        .stat-value.accent {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .domain-badge {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
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

        .summary-box, .summary-box * {
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
            color: white !important;
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

        .stButton > button {
            width: 100% !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            padding: 0.6rem 1.5rem !important;
        }
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4) !important;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%) !important;
        }
        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] .stMarkdown h3 {
            color: #e2e8f0 !important;
        }
        section[data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.1) !important;
        }
        section[data-testid="stSidebar"] .stButton > button {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            box-shadow: 0 8px 20px rgba(99, 102, 241, 0.5) !important;
        }

        div[role='radiogroup'] {
            flex-direction: row !important;
            flex-wrap: wrap !important;
            gap: 8px !important;
            background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%) !important;
            padding: 6px !important;
            border-radius: 14px !important;
            display: inline-flex !important;
            margin-bottom: 1.5rem !important;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15) !important;
        }

        div[role='radiogroup'] > label {
            background: transparent !important;
            border-radius: 10px !important;
            padding: 0.45rem 1.1rem !important;
            margin: 0 !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            border: none !important;
        }

        div[role='radiogroup'] > label:hover {
            background: rgba(255, 255, 255, 0.5) !important;
        }

        div[role='radiogroup'] > label[data-checked="true"] {
            background: #ffffff !important;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2) !important;
        }

        div[role='radiogroup'] > label > div:first-child {
            display: none !important;
        }

        div[role='radiogroup'] > label[data-checked="true"] p {
            color: #4f46e5 !important;
            font-weight: 700 !important;
        }

        div[role='radiogroup'] p {
            font-size: 0.9rem !important;
            color: #3730a3 !important;
            margin: 0 !important;
            font-weight: 500 !important;
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

        .insight-card, .insight-card * {
            background: linear-gradient(135deg, #ffffff 0%, #faf5ff 100%);
            border: 1px solid #e9d5ff;
            border-radius: 14px;
            padding: 1.25rem;
            margin: 0.75rem 0;
            border-left: 4px solid #9333ea;
            color: #581c87 !important;
        }

        .warning-card, .warning-card * {
            background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
            border: 1px solid #fdba74;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #ea580c;
            color: #9a3412 !important;
        }

        .success-card, .success-card * {
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border: 1px solid #86efac;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #16a34a;
            color: #166534 !important;
        }

        .info-card, .info-card * {
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border: 1px solid #93c5fd;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #3b82f6;
            color: #1e40af !important;
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

        .feature-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        .feature-card:hover {
            background: rgba(255,255,255,0.1);
            transform: translateY(-4px);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.2);
        }
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 0.75rem;
        }
        .feature-title {
            font-size: 1rem;
            font-weight: 700;
            color: #e2e8f0;
            margin-bottom: 0.5rem;
        }
        .feature-desc {
            font-size: 0.85rem;
            color: #94a3b8;
            line-height: 1.5;
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

        button[data-testid="stSidebarCollapseButton"],
        button[data-testid="collapsedControl"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.4rem !important;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
            transition: all 0.2s ease !important;
        }
        button[data-testid="stSidebarCollapseButton"]:hover,
        button[data-testid="collapsedControl"]:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 6px 18px rgba(102, 126, 234, 0.5) !important;
        }
        button[data-testid="stSidebarCollapseButton"] svg,
        button[data-testid="collapsedControl"] svg {
            fill: white !important;
            stroke: white !important;
        }
    </style>
    """
