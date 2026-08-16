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

from style import inject_css
inject_css()


st.markdown("<div class='section-header'>📝 Your Lifestyle Profile</div>", unsafe_allow_html=True)

st.markdown("### Region Setting")
region = st.selectbox("Select Your Region for API Emissions Factor", ["Global", "US", "UK", "EU"])

# -------------------------
# QUICK LOG (AI)
# -------------------------
st.markdown("### 🤖 AI Quick Log")
col_ai_input, col_ai_btn = st.columns([4, 1])
with col_ai_input:
    quick_log_text = st.text_area("Let AI auto-fill your profile! Describe your day naturally.", placeholder="e.g., 'I drove 15 miles in my SUV and had a beef steak'", key="quick_log_input", height=68)
with col_ai_btn:
    st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
    parse_btn = st.button("✨ Parse with AI", use_container_width=True)
    
if parse_btn:
    if quick_log_text.strip():
        with st.spinner("Analyzing text..."):
            parsed_data = parse_quick_log(quick_log_text)
            if parsed_data:
                st.session_state.temp_parsed = parsed_data
            else:
                st.error("Could not parse the text. Please try again.")
    else:
        st.warning("Please enter some text first.")

if "temp_parsed" in st.session_state:
    tp = st.session_state.temp_parsed
    st.info(f"**We found:** {tp.get('distance', 10.0)} km by {tp.get('transport', 'Car')}, and {tp.get('diet', 'Vegetarian')} diet. Is this correct?")
    c_yes, c_no = st.columns(2)
    with c_yes:
        if st.button("✅ Yes, use this", key="confirm_yes"):
            st.session_state.transport = tp.get('transport', 'Car')
            st.session_state.distance = float(tp.get('distance', 10.0))
            st.session_state.diet = tp.get('diet', 'Vegetarian')
            del st.session_state.temp_parsed
            st.rerun()
    with c_no:
        if st.button("❌ No, cancel", key="confirm_no"):
            del st.session_state.temp_parsed
            st.rerun()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 16px;'>
        <span style='font-size: 24px;'>🚗</span>
        <span style='font-size: 18px; font-weight: 700; color: #000;'>Transportation</span>
    </div>
    """, unsafe_allow_html=True)
    transport = st.selectbox("Primary Transport", ["Car", "Public Transport", "Bike", "Walking"])
    distance = st.number_input("Daily Distance (km)", min_value=0.0, value=10.0, step=1.0)

with col2:
    st.markdown("""
    <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 16px;'>
        <span style='font-size: 24px;'>⚡</span>
        <span style='font-size: 18px; font-weight: 700; color: #000;'>Energy & Diet</span>
    </div>
    """, unsafe_allow_html=True)
    uploaded_bill = st.file_uploader("Upload Utility Bill (PDF/Image)", type=["pdf", "png", "jpg", "jpeg"])
    if uploaded_bill is not None:
        # We use a button to trigger extraction so it doesn't re-run infinitely on every interaction
        if st.button("Extract Energy Usage"):
            with st.spinner("Extracting data from bill..."):
                extracted_text = extract_text_from_file(uploaded_bill)
                parsed_val = parse_energy_consumption(extracted_text)
                if parsed_val is not None:
                    st.session_state.extracted_kwh = float(parsed_val)
                    st.success(f"Extracted {parsed_val} kWh from bill!")
                else:
                    st.warning("Could not extract energy consumption. Please enter manually.")

    electricity = st.number_input("Monthly Electricity (kWh)", min_value=0.0, value=float(st.session_state.extracted_kwh), step=10.0)
    diet = st.selectbox("Diet Type", ["Vegetarian", "Non-Vegetarian"])

    col1, col2 = st.columns(2)
with col3:
    st.markdown("""
    <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 16px;'>
        <span style='font-size: 24px;'>✈️</span>
        <span style='font-size: 18px; font-weight: 700; color: #000;'>Travel</span>
    </div>
    """, unsafe_allow_html=True)
    flights = st.number_input("Annual Flights", min_value=0, value=0, step=1)
    st.info("💡 How many long-distance flights per year?")
    


# PDF REPORT GENERATION
# -------------------------
def generate_pdf(total, eco_score, insight):
    try:
        file_name = os.path.join(tempfile.gettempdir(), f"eco_report_{uuid.uuid4().hex}.pdf")
        doc = SimpleDocTemplate(file_name)
        styles = getSampleStyleSheet()

        content = [
            Paragraph("EcoBuddy AI Report", styles["Title"]),
            Paragraph(f"Carbon Footprint: {total:.2f} kg CO₂", styles["Normal"]),
            Paragraph(f"Eco Score: {eco_score}/100", styles["Normal"]),
            Paragraph("Key Insight:", styles["Heading2"]),
            Paragraph(insight, styles["Normal"])
        ]

        doc.build(content)
        return file_name
    except Exception:
        st.error("Could not generate the PDF report. Please check disk space and permissions, then try again.")
        return None


# -------------------------
# CALCULATE & ANALYZE
# -------------------------
# col_btn1, col_btn2, col_btn3 = st.columns([1, 1.5, 1])
# with col_btn2:
#     analyze_btn = st.button("🌿 Analyze My Impact")
col_btn1, col_btn2, col_btn3 = st.columns([1, 1.5, 1])
with col_btn1:
    reset_btn = st.button("🔄 Reset Assessment")
    if reset_btn:
        for key in DEFAULT_VALUES:
            if key in st.session_state:
                del st.session_state[key]
        st.success("✅ Assessment form has been reset.")
        st.rerun()

with col_btn2:
    analyze_btn = st.button("🌿 Analyze My Impact")

if analyze_btn:

    with st.spinner("🌍 Analyzing your carbon footprint..."):
        total, contributors = calculate_footprint(
            transport, distance, electricity, diet, flights, region
        )

    eco_score = calculate_eco_score(total)

    insight, recommendations = generate_recommendations(
        transport, electricity, diet, flights, contributors
    )

    save_assessment(
        transport, distance, electricity, diet, flights, total, eco_score
    )

    st.success("✅ Analysis completed!")

    st.markdown("---")


    # Top metrics row
    met1, met2, met3, met4 = st.columns(4)

    with met1:
        st.markdown("""
        <div class='metric-card'>
            <div style='font-size: 14px; color: #d1d5db; margin-bottom: 8px;'>🌍 Total Footprint</div>
            <div style='font-size: 36px; font-weight: 900; color: #4ade80;'>{:.0f}</div>
            <div style='font-size: 12px; color: #9ca3af;'>kg CO₂/year</div>
        </div>
        """.format(total), unsafe_allow_html=True)

    with met2:
        st.markdown("""
        <div class='metric-card'>
            <div style='font-size: 14px; color: #d1d5db; margin-bottom: 8px;'>🏆 Eco Score</div>
            <div style='font-size: 36px; font-weight: 900; color: #4ade80;'>{}</div>
            <div style='font-size: 12px; color: #9ca3af;'>out of 100</div>
        </div>
        """.format(eco_score), unsafe_allow_html=True)

    with met3:
        st.markdown("""
        <div class='metric-card'>
            <div style='font-size: 14px; color: #d1d5db; margin-bottom: 8px;'>📈 Biggest Impact</div>
            <div style='font-size: 24px; font-weight: 700; color: #4ade80;'>{}</div>
            <div style='font-size: 12px; color: #9ca3af;'>{:.0f} kg CO₂</div>
        </div>
        """.format(max(contributors, key=contributors.get), max(contributors.values())), unsafe_allow_html=True)

    with met4:
        st.markdown("""
        <div class='metric-card'>
            <div style='font-size: 14px; color: #d1d5db; margin-bottom: 8px;'>🎯 Status</div>
            <div style='font-size: 18px; font-weight: 700; color: #4ade80;'>Active</div>
            <div style='font-size: 12px; color: #9ca3af;'>Tracking enabled</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # -------------------------
    # ECO SCORE PROGRESS & BADGE
    # -------------------------
    col_badge1, col_badge2 = st.columns([1, 1])

    with col_badge1:
        st.markdown("<div class='section-header' style='margin-top: 0;'>🏅 Eco Achievement</div>", unsafe_allow_html=True)

        if eco_score >= 85:
            badge_text = "🌟 Eco Champion"
            badge_class = "badge badge-champion"
        elif eco_score >= 70:
            badge_text = "🌿 Green Guardian"
            badge_class = "badge badge-guardian"
        elif eco_score >= 50:
            badge_text = "🍃 Eco Learner"
            badge_class = "badge badge-learner"
        else:
            badge_text = "🔥 High Impact User"
            badge_class = "badge badge-high"

        st.markdown(f"<div class='{badge_class}'>{badge_text}</div>", unsafe_allow_html=True)

        # Progress bar
        st.markdown(f"""
        <div style='margin-top: 16px;'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 6px;'>
                <span style='color: #d1d5db; font-size: 14px;'>Score Progress</span>
                <span style='color: #4ade80; font-weight: 700;'>{eco_score}%</span>
            </div>
            <div class='progress-bar'>
                <div class='progress-fill' style='width: {eco_score}%;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Description
        if eco_score >= 85:
            st.info("🌟 Excellent! You're making exceptional environmental choices. Keep it up!")
        elif eco_score >= 70:
            st.info("🌿 Great work! Your footprint is below average. Focus on small improvements.")
        elif eco_score >= 50:
            st.info("🍃 Good start! There's room to improve. Check recommendations below.")
        else:
            st.warning("🔥 Your carbon footprint is above average. Let's work on reducing it!")

    with col_badge2:
        st.markdown("<div class='section-header' style='margin-top: 0;'>📊 Emission Sources</div>", unsafe_allow_html=True)

        # Pie chart with Plotly
        fig = go.Figure(data=[go.Pie(
            labels=list(contributors.keys()),
            values=list(contributors.values()),
            hole=0.4,
            marker=dict(
                colors=['#4ade80', '#60a5fa', '#fbbf24', '#f87171'],
                line=dict(color='rgba(0,0,0,0.1)', width=2)
            ),
            textposition='auto',
            hovertemplate='<b>%{label}</b><br>%{value:.0f} kg CO₂<br>%{percent}<extra></extra>'
        )])

        fig.update_layout(
            showlegend=True,
            height=280,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#d1d5db', size=12),
            legend=dict(
                x=-0.15,
                y=1,
                bgcolor='rgba(0,0,0,0.3)',
                bordercolor='rgba(74, 222, 128, 0.3)',
                borderwidth=1
            )
        )

        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

    st.markdown("---")

    # -------------------------
    # DETAILED BREAKDOWN
    # -------------------------
    st.markdown("<div class='section-header'>📋 Detailed Breakdown</div>", unsafe_allow_html=True)

    # Bar chart
    breakdown_fig = go.Figure(data=[
        go.Bar(
            x=list(contributors.keys()),
            y=list(contributors.values()),
            marker=dict(
                color=['#4ade80', '#60a5fa', '#fbbf24', '#f87171'],
                line=dict(color='rgba(255,255,255,0.2)', width=2)
            ),
            text=[f'{v:.0f} kg' for v in contributors.values()],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>%{y:.0f} kg CO₂<extra></extra>'
        )
    ])

    breakdown_fig.update_layout(
        height=350,
        margin=dict(l=40, r=20, t=20, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(55, 65, 81, 0.2)',
        font=dict(color='#d1d5db', size=12),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            color='#9ca3af'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(74, 222, 128, 0.1)',
            zeroline=False,
            color='#9ca3af'
        ),
        showlegend=False
    )

    st.plotly_chart(breakdown_fig, width="stretch", config={'displayModeBar': False})

    st.markdown("---")

    # -------------------------
    # AI INSIGHT
    # -------------------------
    st.markdown("<div class='section-header'>🤖 AI Insights & Analysis</div>", unsafe_allow_html=True)

    col_insight1, col_insight2 = st.columns([1.2, 0.8])

    with col_insight1:
        st.markdown(f"""
        <div class='card-highlight'>
            <div style='display: flex; gap: 12px; align-items: flex-start;'>
                <div style='font-size: 32px;'>💡</div>
                <div style='flex: 1;'>
                    <div style='font-size: 16px; font-weight: 800; color: #4ade80; margin-bottom: 12px;'>Key Finding</div>
                    <div style='font-size: 15px; color: #d1d5db; line-height: 1.8;'>{h(insight)}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_insight2:
        st.markdown("""
        <div class='card'>
            <div style='display: flex; gap: 12px; align-items: flex-start;'>
                <div style='font-size: 32px;'>🎯</div>
                <div style='flex: 1;'>
                    <div style='font-size: 16px; font-weight: 800; color: #4ade80; margin-bottom: 12px;'>Quick Tips</div>
                    <ul style='color: #d1d5db; font-size: 14px; line-height: 2.2; padding-left: 20px; margin: 0;'>
                        <li>Start with small daily changes</li>
                        <li>Track progress regularly</li>
                        <li>Share with friends & family</li>
                        <li>Focus on your biggest source</li>
                    </ul>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # -------------------------
    # RECOMMENDATIONS
    # -------------------------
    st.markdown("<div class='section-header'>💡 Personalized Recommendations</div>", unsafe_allow_html=True)

    if len(recommendations) > 0:
        for idx, r in enumerate(recommendations):
            st.markdown(f"""
            <div class='card' style='border-left: 4px solid #22c55e;'>
                <div style='display: flex; gap: 12px;'>
                    <div style='font-size: 24px;'>💚</div>
                    <div style='flex: 1;'>
                        <div style='font-size: 15px; line-height: 1.8; color: #d1d5db;'>{h(r)}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='card-highlight'>
            <div style='display: flex; gap: 16px; align-items: center;'>
                <div style='font-size: 48px;'>🌟</div>
                <div>
                    <div style='font-size: 18px; font-weight: 700; color: #4ade80; margin-bottom: 4px;'>Excellent Work!</div>
                    <div style='color: #d1d5db;'>Your lifestyle is already very eco-friendly. Keep maintaining these amazing habits!</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # -------------------------
    # PDF DOWNLOAD
    # -------------------------
    report = generate_pdf(total, eco_score, insight)

    if report:
        with open(report, "rb") as f:
            pdf_bytes = f.read()
            
        try:
            os.remove(report)
        except OSError:
            pass
            
        st.download_button(
            "📄 Download Eco Report (PDF)",
            pdf_bytes,
            file_name="EcoBuddy_Report.pdf"
        )


# -------------------------
# HISTORY & TRACKING
# -------------------------
st.markdown("---")

st.markdown("<div class='section-header'>📈 Your Eco Journey</div>", unsafe_allow_html=True)

history = get_assessments()

if history:

    df = pd.DataFrame(history, columns=[
        "id", "date", "transport", "distance",
        "electricity", "diet", "flights",
        "footprint", "eco_score"
    ])

    latest = history[0]

    # Latest stats
    stat1, stat2, stat3, stat4 = st.columns(4)

    with stat1:
        st.markdown(f"""
        <div class='card'>
            <div style='font-size: 12px; color: #9ca3af;'>Latest Footprint</div>
            <div style='font-size: 28px; font-weight: 900; color: #4ade80;'>{latest[7]:.0f}</div>
            <div style='font-size: 11px; color: #9ca3af;'>kg CO₂</div>
        </div>
        """, unsafe_allow_html=True)

    with stat2:
        st.markdown(f"""
        <div class='card'>
            <div style='font-size: 12px; color: #9ca3af;'>Latest Score</div>
            <div style='font-size: 28px; font-weight: 900; color: #4ade80;'>{latest[8]}</div>
            <div style='font-size: 11px; color: #9ca3af;'>out of 100</div>
        </div>
        """, unsafe_allow_html=True)

    if len(history) >= 2:
        prev = history[1][7]
        change = ((prev - latest[7]) / prev) * 100 if prev else 0

        with stat3:
            if change > 0:
                color = "#4ade80"
                emoji = "📉"
                label = "Reduced"
            elif change < 0:
                color = "#f87171"
                emoji = "📈"
                label = "Increased"
            else:
                color = "#60a5fa"
                emoji = "→"
                label = "No Change"

            st.markdown(f"""
            <div class='card'>
                <div style='font-size: 12px; color: #9ca3af;'>{emoji} {label}</div>
                <div style='font-size: 28px; font-weight: 900; color: {color};'>{abs(change):.1f}%</div>
                <div style='font-size: 11px; color: #9ca3af;'>vs previous</div>
            </div>
            """, unsafe_allow_html=True)

    with stat4:
        st.markdown(f"""
        <div class='card'>
            <div style='font-size: 12px; color: #9ca3af;'>Total Records</div>
            <div style='font-size: 28px; font-weight: 900; color: #4ade80;'>{len(history)}</div>
            <div style='font-size: 11px; color: #9ca3af;'>assessments</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # -------------------------
    # TREND VISUALIZATION
    # -------------------------
    st.markdown("<div style='font-size: 22px; font-weight: 800; background: linear-gradient(135deg, #4ade80, #86efac); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 16px;'>📉 Carbon Footprint Trend</div>", unsafe_allow_html=True)

    trend_df = df[["date", "footprint"]].iloc[::-1].reset_index(drop=True)
    trend_df['date'] = pd.to_datetime(trend_df['date'])

    trend_fig = go.Figure()
    trend_fig.add_trace(go.Scatter(
        x=trend_df['date'],
        y=trend_df['footprint'],
        mode='lines+markers',
        name='Carbon Footprint',
        line=dict(color='#4ade80', width=3),
        marker=dict(size=8, color='#4ade80', line=dict(color='#86efac', width=2)),
        fill='tozeroy',
        fillcolor='rgba(74, 222, 128, 0.2)',
        hovertemplate='<b>%{x|%b %d}</b><br>%{y:.0f} kg CO₂<extra></extra>'
    ))

    trend_fig.update_layout(
        height=320,
        margin=dict(l=40, r=20, t=20, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(55, 65, 81, 0.2)',
        font=dict(color='#d1d5db', size=12),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            color='#9ca3af'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(74, 222, 128, 0.1)',
            zeroline=False,
            color='#9ca3af'
        ),
        showlegend=False,
        hovermode='x unified'
    )

    st.plotly_chart(trend_fig, width="stretch", config={'displayModeBar': False})

    st.markdown("---")

    # -------------------------
    # HISTORY TABLE
    # -------------------------
    st.markdown("<div style='font-size: 22px; font-weight: 800; background: linear-gradient(135deg, #4ade80, #86efac); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 16px;'>📋 Assessment History</div>", unsafe_allow_html=True)

    # Create a nice table display
    display_df = df[["date", "transport", "electricity", "footprint", "eco_score"]].copy()
    display_df.columns = ["📅 Date", "🚗 Transport", "⚡ Electricity (kWh)", "🌍 Footprint (kg CO₂)", "🏆 Score"]
    display_df = display_df.iloc[::-1].reset_index(drop=True)

    st.markdown(
        "<div class='history-table-wrap'>"
        + display_df.to_html(index=False, classes="history-table", border=0)
        + "</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    # -------------------------
    # STATS & INSIGHTS
    # -------------------------
    st.markdown("<div style='font-size: 22px; font-weight: 800; background: linear-gradient(135deg, #4ade80, #86efac); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 16px;'>📊 Your Statistics</div>", unsafe_allow_html=True)

    stats_col1, stats_col2, stats_col3 = st.columns(3)

    avg_footprint = df['footprint'].mean()
    avg_score = df['eco_score'].mean()
    max_footprint = df['footprint'].max()
    min_footprint = df['footprint'].min()

    with stats_col1:
        st.markdown(f"""
        <div class='card'>
            <div style='font-size: 13px; color: #9ca3af; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 700;'>📊 Average Footprint</div>
            <div style='font-size: 36px; font-weight: 900; color: #4ade80;'>{avg_footprint:.0f}</div>
            <div style='font-size: 12px; color: #9ca3af; margin-top: 8px;'>kg CO₂ across {len(history)} records</div>
        </div>
        """, unsafe_allow_html=True)

    with stats_col2:
        st.markdown(f"""
        <div class='card'>
            <div style='font-size: 13px; color: #9ca3af; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 700;'>🎯 Average Score</div>
            <div style='font-size: 36px; font-weight: 900; color: #4ade80;'>{avg_score:.0f}</div>
            <div style='font-size: 12px; color: #9ca3af; margin-top: 8px;'>out of 100 points</div>
        </div>
        """, unsafe_allow_html=True)

    with stats_col3:
        range_val = max_footprint - min_footprint
        st.markdown(f"""
        <div class='card'>
            <div style='font-size: 13px; color: #9ca3af; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 700;'>📈 Range Variation</div>
            <div style='font-size: 28px; font-weight: 700; color: #4ade80;'>{min_footprint:.0f}</div>
            <div style='font-size: 14px; color: #9ca3af;'>to</div>
            <div style='font-size: 28px; font-weight: 700; color: #4ade80;'>{max_footprint:.0f}</div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class='card-highlight'>
        <div style='text-align: center; padding: 48px 32px;'>
            <div style='font-size: 72px; margin-bottom: 20px; animation: bounce 2s infinite;'>🌱</div>
            <div style='font-size: 26px; font-weight: 800; background: linear-gradient(135deg, #22c55e, #4ade80); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 12px;'>No Data Yet</div>
            <div style='color: #d1d5db; font-size: 16px; line-height: 1.6; max-width: 400px; margin: 0 auto;'>
                Start your eco journey! Complete the lifestyle profile above and click "Analyze My Impact" to generate your personalized carbon footprint report.
            </div>
        </div>
    </div>
    <style>
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
    </style>
    """, unsafe_allow_html=True)
