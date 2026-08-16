import html
import time
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import tempfile
import uuid
import os
from dotenv import load_dotenv

load_dotenv()
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from database import init_db, save_assessment, get_assessments, init_gamification_db
import gamification as gf
from emissions import calculate_footprint, calculate_eco_score
from llm_parser import parse_quick_log

from recommendations import generate_recommendations
from ocr_utils import extract_text_from_file, parse_energy_consumption

# Added for Route Planning & Offsets
from database import (
    init_marketplace_db, save_journey_profile, get_journey_profiles, delete_journey_profile,
    save_offset_transaction, get_offset_transactions, delete_offset_transaction,
    get_total_offsets, get_total_spend
)
from marketplace import (
    calculate_trip_emissions, calculate_recurring_trip_emissions, compare_transit_modes,
    calculate_offset_cost, validate_offset_transaction, get_offset_projects,
    calculate_net_emissions, calculate_net_zero_progress, get_project_by_id, EMISSION_FACTORS
)



def h(text):
    return html.escape(str(text))


# -------------------------
# INIT
# -------------------------

init_db()
init_gamification_db()
init_marketplace_db()

if 'extracted_kwh' not in st.session_state:
    st.session_state.extracted_kwh = 200.0


# -------------------------
# DEFAULT FORM VALUES
# -------------------------
DEFAULT_VALUES = {
    "transport": "Car",
    "distance": 10.0,
    "electricity": 200.0,
    "diet": "Vegetarian",
    "flights": 0,
}

for key, value in DEFAULT_VALUES.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.set_page_config(
    page_title="EcoBuddy",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)



from style import inject_css
inject_css()

# -------------------------
st.markdown("<div class='title'>🌱 EcoBuddy AI+</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Your Personal AI-Powered Carbon Footprint Tracker & Eco Assistant</div>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; margin-bottom: 32px;'>
    <div style='display: inline-flex; gap: 16px; padding: 12px 24px; background: rgba(34, 197, 94, 0.08); border-radius: 50px; border: 1px solid rgba(74, 222, 128, 0.2);'>
        <span style='color: #000; font-size: 15px; font-weight: 700;'>✨ Track • 📊 Analyze • 💡 Improve</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<style>
@keyframes bounce {
    0%,100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

.empty-card{
    background: linear-gradient(135deg,#132238,#0f172a);
    border:1px solid rgba(74,222,128,0.25);
    border-radius:20px;
    padding:45px 35px;
    text-align:center;
    box-shadow:0 12px 30px rgba(0,0,0,.25);
    margin-top:20px;
}

.empty-title{
    font-size:32px;
    font-weight:800;
    color:#4ade80;
    margin-bottom:12px;
}

.empty-subtitle{
    color:#cbd5e1;
    font-size:17px;
    line-height:1.8;
    max-width:650px;
    margin:auto;
}

.empty-checklist{
    margin-top:28px;
    text-align:left;
    display:inline-block;
    color:#e2e8f0;
    font-size:16px;
    line-height:2;
}

.empty-icon{
    font-size:72px;
    animation:bounce 2s infinite;
    margin-bottom:20px;
}

.tip-box{
    margin-top:28px;
    background:rgba(74,222,128,.08);
    border-left:5px solid #4ade80;
    padding:18px;
    border-radius:12px;
    color:#d1fae5;
    font-size:15px;
}
</style>

<div class="empty-card">

    <div class="empty-icon">🌱</div>

    <div class="empty-title">
        Welcome to Your Eco Journey
    </div>

    <div class="empty-subtitle">
        Complete your lifestyle profile above and click
        <b>"Analyze My Impact"</b> to generate your first carbon footprint report.
    </div>

    <div class="empty-checklist">
        ✅ Personalized Eco Score<br>
        ✅ Carbon Footprint Dashboard<br>
        ✅ AI Insights & Recommendations<br>
        ✅ Emission Charts & Trends<br>
        ✅ Downloadable PDF Report
    </div>

    <div class="tip-box">
        💡 <b>Tip:</b> Even small lifestyle changes can make a meaningful impact over time.
        Start with your first assessment and track your progress.
    </div>

</div>
""", unsafe_allow_html=True)


st.markdown("---")

st.markdown("## 🌱 What You'll Unlock")

col1, col2, col3 = st.columns(3)

with col1:
    st.success("📊 Carbon Footprint Dashboard")
    st.caption("Track your yearly emissions.")

with col2:
    st.success("🤖 AI Insights")
    st.caption("Get AI-powered analysis.")

with col3:
    st.success("💡 Smart Recommendations")
    st.caption("Receive personalized eco tips.")


st.markdown("---")

st.markdown("## 🚀 How It Works")

st.info("1️⃣ Fill in your lifestyle details")
st.info("2️⃣ Click **Analyze My Impact**")
st.info("3️⃣ Review your carbon footprint")
st.info("4️⃣ Get personalized AI recommendations")
st.info("5️⃣ Download your PDF report")

st.markdown("---")
st.markdown("## ✨ Why Use EcoBuddy AI?")

feature1, feature2 = st.columns(2)

with feature1:
    st.success("📈 Track your carbon footprint over time")
    st.success("🤖 AI-powered personalized insights")
    st.success("📄 Export reports as PDF")

with feature2:
    st.success("🌍 Build sustainable habits")
    st.success("📊 Interactive charts and trends")
    st.success("🏆 Improve your Eco Score")


st.markdown("---")

st.markdown("## 💡 Eco Tips")

tip_col1, tip_col2 = st.columns(2)

with tip_col1:
    st.success("🚶 Walk or cycle for short trips")
    st.success("💧 Save water whenever possible")
    st.success("♻️ Recycle household waste")

with tip_col2:
    st.success("⚡ Turn off unused appliances")
    st.success("🚌 Use public transport")
    st.success("🌱 Plant more trees")


st.markdown("---")

st.markdown(
"""
### 🌍 Every small action matters

Your sustainability journey starts with a single assessment.
Complete your profile today and discover simple ways to reduce
your carbon footprint and make a positive environmental impact.
"""
)

st.markdown("---")

st.markdown("## 🚀 Ready to Begin?")

st.success(
"Complete the lifestyle form above and click **Analyze My Impact** "
"to generate your first carbon footprint assessment."
)
