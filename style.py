import streamlit as st

def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
        :root {
            --ink: #111827;
            --muted: #6b7280;
            --paper: rgba(255,255,255,0.75);
            --paper-strong: rgba(255,255,255,0.95);
            --line: rgba(0,0,0,0.08);
            --shadow: 0 10px 30px rgba(0,0,0,0.08);
        }
    
        * {
            box-sizing: border-box;
        }
    
        html {
            scroll-behavior: smooth;
        }
    
        body,
        [data-testid="stAppViewContainer"] {
            color: #1f2937;
            background:
                radial-gradient(circle at top left, #dcfce7 0%, transparent 30%),
                radial-gradient(circle at top right, #dbeafe 0%, transparent 30%),
                #f8fafc !important;
        }
    
        .block-container {
            max-width: 1280px;
            padding: 24px 32px 56px;
        }
    
        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.74);
            border-right: 1px solid var(--line);
            box-shadow: 18px 0 48px rgba(44, 72, 47, 0.08);
            backdrop-filter: blur(18px);
        }
    
        [data-testid="stSidebar"] * {
            color: var(--ink);
        }
    
        .title {
            margin: 8px 0 12px;
            color: var(--ink);
            font-size: clamp(46px, 6vw, 82px);
            line-height: 1;
            font-weight: 800;
            letter-spacing: 0;
            text-align: center;
            animation: fadeUp 700ms ease both;
        }
    
        .subtitle {
            max-width: 720px;
            margin: 0 auto 30px;
            color: var(--muted);
            font-size: 19px;
            line-height: 1.6;
            font-weight: 500;
            text-align: center;
            animation: fadeUp 800ms 80ms ease both;
        }
    
        .section-header {
            margin: 38px 0 18px;
            color: var(--ink);
            font-size: clamp(28px, 3vw, 42px);
            line-height: 1.08;
            font-weight: 800;
            letter-spacing: 0;
            animation: fadeUp 650ms ease both;
        }
    
        .section-header::after {
            content: '';
            display: block;
            width: 88px;
            height: 4px;
            margin-top: 14px;
            border-radius: 999px;
            background: linear-gradient(90deg, #030504, var(--leaf), rgba(120, 169, 69, 0));
        }
    
        .input-section,
        .card,
        .card-highlight,
        .metric-card {
            border: 1px solid var(--line);
            border-radius: var(--radius);
            background: rgba(255,255,255,0.9);
            border: 1px solid #e5e7eb;
            box-shadow: 0 8px 24px rgba(0,0,0,0.06);
            box-shadow: 0 18px 50px rgba(57, 86, 47, 0.12);
            backdrop-filter: blur(18px);
            position: relative;
            overflow: hidden;
            animation: fadeUp 700ms ease both;
            transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
        }
    
        .input-section {
            padding: 34px;
            margin-bottom: 24px;
        }
    
        .card,
        .card-highlight,
        .metric-card {
            padding: 26px;
            margin-bottom: 16px;
        }
    
        .metric-card::before,
        .card-highlight::before {
            content: '';
            position: absolute;
            inset: 0 0 auto 0;
            height: 5px;
            background: linear-gradient(90deg, #030504, var(--leaf), #b6d274);
        }
    
        .metric-card:hover,
        .card:hover,
        .card-highlight:hover {
            transform: translateY(-6px);
            border-color: rgba(95, 143, 54, 0.28);
            box-shadow: 0 26px 64px rgba(57, 86, 47, 0.17);
        }
    
        .card-highlight {
            background:
                linear-gradient(145deg, rgba(255, 255, 255, 0.94), rgba(232, 244, 216, 0.82)),
                linear-gradient(135deg, rgba(120, 169, 69, 0.12), transparent);
        }
    
        .badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 42px;
            padding: 0 20px;
            border-radius: 999px;
            border: 1px solid rgba(8, 11, 10, 0.08);
            background: #030504;
            color: #fff;
            box-shadow: 0 14px 30px rgba(0, 0, 0, 0.14);
            font-size: 14px;
            font-weight: 800;
            letter-spacing: 0;
        }
    
        .badge-champion {
            background: linear-gradient(135deg, #f4c760, #d8831e);
            color: #2c1804;
        }
    
        .badge-guardian {
            background: linear-gradient(135deg, #acd66f, #5f8f36);
            color: #0d1c0f;
        }
    
        .badge-learner {
            background: linear-gradient(135deg, #b9d7f4, #6aa0cf);
            color: #071927;
        }
    
        .badge-high {
            background: linear-gradient(135deg, #ff8e70, #d84b35);
            color: #2e0904;
        }
    
        .progress-bar {
            width: 100%;
            height: 12px;
            margin-top: 12px;
            border-radius: 999px;
            background: rgba(8, 11, 10, 0.08);
            overflow: hidden;
        }
    
        .progress-fill {
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, #030504, var(--moss), var(--leaf));
            box-shadow: 0 0 20px rgba(95, 143, 54, 0.34);
            transition: width 600ms ease;
        }
    
        hr {
            height: 1px;
            margin: 32px 0;
            border: none;
            background: linear-gradient(90deg, transparent, rgba(8, 11, 10, 0.16), transparent);
        }
    
        .stTextInput > div > div > input,
        .stNumberInput input,
        .stSelectbox [data-baseweb="select"],
        .stTextArea textarea {
            min-height: 48px;
            border: 1px solid rgba(8, 11, 10, 0.12) !important;
            border-radius: 12px !important;
            background: rgba(255, 255, 255, 0.88) !important;
            color: var(--ink) !important;
            box-shadow: 0 12px 30px rgba(57, 86, 47, 0.08);
        }
    
        .stTextInput > div > div > input:focus,
        .stNumberInput input:focus,
        .stTextArea textarea:focus {
            border-color: rgba(95, 143, 54, 0.55) !important;
            box-shadow: 0 0 0 4px rgba(120, 169, 69, 0.14) !important;
        }
    
        .stButton > button,
        .stDownloadButton > button,
        [data-testid="stFormSubmitButton"] > button {
            min-height: 52px;
            padding: 0 28px !important;
            border: none !important;
            border-radius: 12px !important;
            background: #030504 !important;
            color: #fff !important;
            box-shadow: 0 16px 34px rgba(0, 0, 0, 0.2) !important;
            font-size: 15px !important;
            font-weight: 800 !important;
            letter-spacing: 0 !important;
            transition: transform 180ms ease, box-shadow 180ms ease, background 180ms ease !important;
        }
    
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        [data-testid="stFormSubmitButton"] > button:hover {
            transform: translateY(-2px);
            background: #101713 !important;
            box-shadow: 0 22px 44px rgba(0, 0, 0, 0.26) !important;
        }
    
        .stInfo,
        .stWarning,
        .stSuccess,
        .stError {
            border-radius: 14px !important;
            border: 1px solid var(--line) !important;
            box-shadow: 0 12px 30px rgba(57, 86, 47, 0.08);
        }
    
        .stInfo {
            background: rgba(185, 215, 244, 0.42) !important;
        }
    
        .stWarning {
            background: rgba(244, 199, 96, 0.24) !important;
        }
    
        .stSuccess {
            background: rgba(172, 214, 111, 0.26) !important;
        }
    
        /* DARK PREMIUM THEME OVERRIDES 
        :root {
            --sky: #8ec5ff;
            --sky-soft: #18273a;
            --field: #4ade80;
            --leaf: #58d27b;
            --moss: #86efac;
            --ink: #f8fafc;
            --muted: #a7b3c6;
            --paper: rgba(15, 23, 42, 0.76);
            --paper-strong: rgba(12, 18, 32, 0.92);
            --line: rgba(148, 163, 184, 0.18);
            --shadow: 0 24px 70px rgba(0, 0, 0, 0.38);
            --radius: 18px;
        }
    
        body,
        [data-testid="stAppViewContainer"] {
            color: var(--ink);
            background:
                radial-gradient(circle at 18% 8%, rgba(74, 222, 128, 0.22), transparent 28%),
                radial-gradient(circle at 84% 12%, rgba(96, 165, 250, 0.18), transparent 30%),
                linear-gradient(145deg, #030712 0%, #07130d 42%, #111827 100%) !important;
        }
    
        .block-container {
            padding-top: 28px;
        }
    
        [data-testid="stSidebar"] {
            background: rgba(3, 7, 18, 0.84);
            border-right: 1px solid var(--line);
            box-shadow: 18px 0 48px rgba(0, 0, 0, 0.26);
        }
    
        [data-testid="stSidebar"] * {
            color: var(--ink);
        }
    
        .title {
            color: var(--ink);
            text-shadow: 0 18px 48px rgba(74, 222, 128, 0.18);
        }
    
        .subtitle,
        .section-header {
            color: var(--ink);
        }
    
        .subtitle {
            color: var(--muted);
        }
    
        .input-section,
        .card,
        .card-highlight,
        .metric-card {
            background:
                linear-gradient(145deg, rgba(15, 23, 42, 0.94), rgba(17, 24, 39, 0.72)),
                linear-gradient(135deg, rgba(74, 222, 128, 0.08), transparent);
            border-color: var(--line);
            box-shadow: var(--shadow);
        }
    
        .card-highlight {
            background:
                linear-gradient(145deg, rgba(13, 36, 25, 0.92), rgba(12, 18, 32, 0.84)),
                linear-gradient(135deg, rgba(74, 222, 128, 0.14), transparent);
        }
    
        .metric-card::before,
        .card-highlight::before,
        .section-header::after {
            background: linear-gradient(90deg, #4ade80, #86efac, rgba(96, 165, 250, 0));
        }
    
        .progress-bar {
            background: rgba(148, 163, 184, 0.14);
        }
    
        .progress-fill {
            background: linear-gradient(90deg, #16a34a, #4ade80, #86efac);
        }
    
        .stTextInput > div > div > input,
        .stNumberInput input,
        .stSelectbox [data-baseweb="select"],
        .stTextArea textarea {
            background: #e6f5e9 !important;
            border-color: rgba(74, 222, 128, 0.4) !important;
            color: #05070a !important;
            box-shadow: 0 14px 36px rgba(0, 0, 0, 0.18);
        }
    
        .stTextInput label,
        .stNumberInput label,
        .stSelectbox label,
        [data-testid="stWidgetLabel"],
        [data-testid="stWidgetLabel"] p {
            color: #ffffff !important;
            opacity: 1 !important;
            font-weight: 800 !important;
        }
    
        .stSelectbox [data-baseweb="select"] *,
        .stNumberInput input,
        .stTextInput input,
        .stTextArea textarea {
            color: #05070a !important;
            -webkit-text-fill-color: #05070a !important;
        }
    
        .stButton > button,
        .stDownloadButton > button,
        [data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(135deg, #0b0f18, #111827) !important;
            color: #ffffff !important;
            border: 1px solid rgba(134, 239, 172, 0.28) !important;
            box-shadow: 0 18px 40px rgba(0, 0, 0, 0.32) !important;
        }
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        [data-testid="stFormSubmitButton"] > button:hover {
            background: linear-gradient(135deg, #111827, #0f2a1a) !important;
            border-color: rgba(134, 239, 172, 0.55) !important;
        }
    
        .stInfo,
        .stWarning,
        .stSuccess,
        .stError {
            color: var(--ink) !important;
            background: rgba(15, 23, 42, 0.78) !important;
            border-color: var(--line) !important;
        }
    
        [style*="#d1d5db"],
        [style*="#9ca3af"],
        [style*="rgb(209, 213, 219)"],
        [style*="rgb(156, 163, 175)"] {
            color: var(--muted) !important;
        }
        
        [style*="#4ade80"],
        [style*="rgb(74, 222, 128)"] {
            color: var(--moss) !important;
        }
    
        [data-testid="stDataFrame"] {
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid var(--line);
            box-shadow: var(--shadow);
            background: var(--paper-strong) !important;
        }
    
        [data-testid="stDataFrame"] > div,
        [data-testid="stDataFrame"] iframe,
        [data-testid="stDataFrame"] [class*="stDataFrame"],
        [data-testid="stDataFrame"] [class*="dataframe"],
        [data-testid="stDataFrame"] [class*="glide"],
        [data-testid="stDataFrame"] [class*="table"] {
            background: transparent !important;
        }
    
        [data-testid="stDataFrame"] canvas {
            background: transparent !important;
        }
    
        [data-testid="stDataFrame"] button,
        [data-testid="stDataFrame"] [role="button"] {
            background: rgba(255, 255, 255, 0.8) !important;
            color: var(--ink) !important;
            border-color: var(--line) !important;
        }
    
        [data-testid="stDataFrame"] svg {
            color: var(--ink) !important;
            fill: var(--ink) !important;
        }
    
        [data-testid="stDataFrame"] [role="grid"],
        [data-testid="stDataFrame"] [role="row"],
        [data-testid="stDataFrame"] [role="columnheader"],
        [data-testid="stDataFrame"] [role="gridcell"] {
            background-color: transparent !important;
            border-color: var(--line) !important;
        }
    
        [data-testid="stDataFrame"] [role="columnheader"] {
            background-color: var(--sky-soft) !important;
            color: var(--moss) !important;
            font-weight: 800 !important;
        }
    
        .history-table-wrap {
            width: 100%;
            overflow-x: auto;
            border: 1px solid rgba(134, 239, 172, 0.24);
            border-radius: 16px;
            background: #0f172a;
            box-shadow: var(--shadow);
        }
    
        .history-table {
            width: 100%;
            border-collapse: collapse;
            background: #0f172a;
            color: #ffffff;
            font-size: 15px;
        }
    
        .history-table thead th {
            padding: 16px 18px;
            background: #07130d;
            color: #ffffff !important;
            border-bottom: 1px solid rgba(134, 239, 172, 0.3);
            font-weight: 800;
            text-align: left;
            white-space: nowrap;
        }
    
        .history-table tbody td {
            padding: 15px 18px;
            color: #ffffff !important;
            border-bottom: 1px solid rgba(148, 163, 184, 0.14);
            text-align: left;
        }
    
        .history-table tbody tr:nth-child(odd) {
            background: #0f172a;
        }
    
        .history-table tbody tr:nth-child(even) {
            background: #111827;
        }
    
        .history-table tbody tr:hover {
            background: rgba(34, 197, 94, 0.14);
        }
    
        @keyframes fadeUp {
            from {
                opacity: 0;
                transform: translateY(18px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    
        @media (max-width: 760px) {
            .block-container {
                padding: 16px 14px 42px;
            }
    
            .input-section,
            .card,
            .card-highlight,
            .metric-card {
                padding: 22px;
            }
        }
    
        button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
            color: #d1d5db !important;
            font-weight: 600 !important;
        }
        
        button[data-baseweb="tab"][aria-selected="true"] > div[data-testid="stMarkdownContainer"] > p {
            color: #4ade80 !important;
            font-weight: 800 !important;
        }
        
        [data-testid="stExpander"] {
            background: #0f172a !important;
            border: 1px solid rgba(134, 239, 172, 0.28) !important;
            border-radius: 8px !important;
            overflow: hidden;
        }
        
        [data-testid="stExpander"] details {
            background: #0f172a !important;
        }
    
        [data-testid="stExpander"] summary {
            background-color: #0f172a !important;
        }
        
        [data-testid="stExpander"] summary:hover {
            background-color: #1e293b !important;
        }
    
        [data-testid="stExpander"] summary,
        [data-testid="stExpander"] summary p,
        [data-testid="stExpander"] summary span,
        [data-testid="stExpander"] summary svg {
            color: #ffffff !important;
            font-weight: 600 !important;
            fill: #ffffff !important;
        }
        
        [data-testid="stExpanderDetails"] {
            background-color: #0f172a !important;
            color: #d1d5db !important;
        }*/
    </style>
    """, unsafe_allow_html=True)
