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

if not st.session_state.get('user_id'):
    st.warning("Please login from the main page first.")
    st.stop()


import database as db
import energy_audit as ea
import plotly.graph_objects as go

st.markdown("<div class='section-header'>⚡ Home Energy Audit</div>", unsafe_allow_html=True)

# Init energy db
db.init_energy_db()

st.markdown("### 🔌 Appliance Registry")
with st.expander("➕ Add New Appliance", expanded=False):
    with st.form("appliance_form"):
        c1, c2, c3 = st.columns(3)
        app_name = c1.text_input("Appliance Name")
        app_cat = c2.selectbox("Category", ["AC", "EV Charger", "Heat Pump", "Refrigerator", "Lighting", "Other"])
        app_qty = c3.number_input("Quantity", min_value=1, value=1)

        c4, c5, c6 = st.columns(3)
        app_power = c4.number_input("Power Rating (Watts)", min_value=0.0, value=100.0)
        app_hours = c5.number_input("Hours Used/Day", min_value=0.0, max_value=24.0, value=1.0)
        app_standby = c6.number_input("Standby Draw (Watts)", min_value=0.0, value=0.0)

        submit_app = st.form_submit_button("Add Appliance")
        if submit_app and app_name:
            db.add_appliance(st.session_state.user_id, app_name, app_cat, app_qty, app_power, app_hours, app_standby)
            st.success(f"Added {app_name}")
            st.rerun()

appliances = db.get_appliances(st.session_state.user_id)
if appliances:
    # Build a styled HTML table instead of st.dataframe
    category_icons = {"AC": "❄️", "EV Charger": "🔋", "Heat Pump": "🌡️", "Refrigerator": "🧊", "Lighting": "💡", "Other": "🔌"}
    table_rows = ""
    for a in appliances:
        icon = category_icons.get(a['category'], '🔌')
        table_rows += f"""
        <tr>
            <td>{icon} {h(a['name'])}</td>
            <td><span style='background:rgba(74,222,128,0.15); padding:4px 10px; border-radius:8px; font-size:13px;'>{h(a['category'])}</span></td>
            <td style='text-align:center;'>{a['quantity']}</td>
            <td style='text-align:right;'>{a['power_rating_watts']:.0f} W</td>
            <td style='text-align:right;'>{a['hours_used_per_day']:.1f} h</td>
            <td style='text-align:right;'>{a['standby_draw_watts']:.1f} W</td>
        </tr>"""

    st.markdown(f"""
    <div style='border:1px solid rgba(134,239,172,0.24); border-radius:16px; overflow:hidden; background:#0f172a; box-shadow:0 24px 70px rgba(0,0,0,0.38);'>
        <table style='width:100%; border-collapse:collapse; color:#fff; font-size:15px;'>
            <thead>
                <tr style='background:#07130d;'>
                    <th style='padding:14px 18px; text-align:left; font-weight:700; color:#86efac;'>Appliance</th>
                    <th style='padding:14px 18px; text-align:left; font-weight:700; color:#86efac;'>Category</th>
                    <th style='padding:14px 18px; text-align:center; font-weight:700; color:#86efac;'>Qty</th>
                    <th style='padding:14px 18px; text-align:right; font-weight:700; color:#86efac;'>Power</th>
                    <th style='padding:14px 18px; text-align:right; font-weight:700; color:#86efac;'>Hours/Day</th>
                    <th style='padding:14px 18px; text-align:right; font-weight:700; color:#86efac;'>Standby</th>
                </tr>
            </thead>
            <tbody>{table_rows}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # Delete appliance controls
    st.markdown("")
    del_cols = st.columns([3, 1])
    with del_cols[0]:
        del_id = st.selectbox("Select appliance to remove", options=[(a['id'], a['name']) for a in appliances], format_func=lambda x: x[1], label_visibility="collapsed")
    with del_cols[1]:
        if st.button("🗑️ Remove", key="del_app"):
            db.delete_appliance(del_id[0])
            st.rerun()

    # Calculate summaries
    daily_kwh, monthly_kwh, yearly_kwh = ea.calculate_home_energy_summary(appliances)

    st.markdown("### 📊 Energy Patterns")
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Daily Consumption", f"{daily_kwh:.2f} kWh")
    sc2.metric("Monthly Consumption", f"{monthly_kwh:.2f} kWh")
    sc3.metric("Yearly Consumption", f"{yearly_kwh:.2f} kWh")

    # Hourly profile chart
    profile = ea.generate_hourly_energy_profile(appliances)
    fig_hr = go.Figure(data=[go.Bar(x=list(range(24)), y=profile, marker_color='#fbbf24')])
    fig_hr.update_layout(title="Hourly Energy Demand (kWh)", xaxis_title="Hour of Day", yaxis_title="kWh", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_hr, width="stretch")

else:
    st.markdown("""
    <div style='text-align:center; padding:48px 24px; border:1px dashed rgba(134,239,172,0.3); border-radius:16px; background:rgba(15,23,42,0.5);'>
        <div style='font-size:48px; margin-bottom:12px;'>🔌</div>
        <div style='font-size:18px; font-weight:600; color:#e5e7eb; margin-bottom:8px;'>No Appliances Yet</div>
        <div style='font-size:14px; color:#94a3b8;'>Click <b>"➕ Add New Appliance"</b> above to register your first household appliance and start tracking energy consumption.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("### ☀️ Solar ROI Calculator")

sc_form1, sc_form2 = st.columns(2)
with sc_form1:
    roof_space = st.number_input("Available Roof Space (m²)", min_value=0.0, value=30.0)
    panel_eff = st.number_input("Panel Efficiency (%)", min_value=0.0, max_value=100.0, value=20.0)
    sun_hours = st.number_input("Peak Sun Hours/Day", min_value=0.0, value=4.5)
    install_cost = st.number_input("Installation Cost per kW ($)", min_value=0.0, value=2500.0)
with sc_form2:
    util_rate = st.number_input("Utility Rate ($/kWh)", min_value=0.0, value=0.15)
    maint_cost = st.number_input("Annual Maintenance Cost ($)", min_value=0.0, value=100.0)
    rate_inc = st.number_input("Annual Rate Increase (%)", min_value=0.0, value=3.0)

sys_size = ea.calculate_solar_system_size(roof_space, panel_eff)
ann_gen = ea.calculate_annual_solar_generation(sys_size, sun_hours)
inst_cost = ea.calculate_solar_installation_cost(sys_size, install_cost)
ann_savings = ann_gen * util_rate
payback = ea.calculate_solar_payback_period(inst_cost, ann_savings)
savings_20y = ea.calculate_long_term_solar_savings(ann_gen, util_rate, 20, rate_inc, maint_cost) - inst_cost
carbon_offset = ea.calculate_solar_carbon_offset(ann_gen)

st.markdown("#### 📈 Solar Simulation Results")
r1, r2, r3, r4 = st.columns(4)
r1.metric("System Size", f"{sys_size:.1f} kW")
r2.metric("Annual Generation", f"{ann_gen:.0f} kWh")
r3.metric("Est. Installation", f"${inst_cost:,.0f}")
r4.metric("Payback Period", f"{payback:.1f} years" if payback != float('inf') else "N/A")

st.markdown(f"""
<div style='padding:18px 24px; border-radius:14px; background:linear-gradient(135deg, rgba(34,197,94,0.15), rgba(74,222,128,0.08)); border:1px solid rgba(74,222,128,0.3); margin-top:8px;'>
    <span style='font-size:18px;'>💡</span>
    <span style='color:#e5e7eb; font-size:15px;'>Over 20 years, you could save <b style="color:#4ade80;">${savings_20y:,.0f}</b> and offset <b style="color:#4ade80;">{carbon_offset:,.0f} kg CO₂</b> annually.</span>
</div>
""", unsafe_allow_html=True)
