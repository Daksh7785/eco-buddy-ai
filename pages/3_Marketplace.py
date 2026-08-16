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


st.markdown("<div class='section-header'>🗺️ Route Planning & Carbon Offsets</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Compare transit modes, track your footprint, and build a simulated offset portfolio. Note: This is a simulation and does not process real financial transactions.</div>", unsafe_allow_html=True)

route_col, offset_col = st.columns([1.2, 1])

with route_col:
    st.subheader("📍 Transit Mode Comparison")
    
    with st.form("route_form"):
        dist_val = st.number_input("Trip Distance (km)", min_value=0.1, value=15.0, step=1.0)
        pass_val = st.number_input("Number of Passengers", min_value=1, value=1, step=1)
        freq = st.selectbox("Trip Frequency", ["One-time", "Weekly Commute (10 trips/week)", "Daily (14 trips/week)"])
        
        calc_btn = st.form_submit_button("Compare Emissions")
        
    if calc_btn:
        try:
            comparisons = compare_transit_modes(dist_val, pass_val)
            st.write(f"**Estimated Emissions for a {dist_val}km trip:**")
            
            # Chart
            df_comp = pd.DataFrame(comparisons)
            
            # Handle frequency
            if "Weekly" in freq:
                df_comp['emissions_kg'] = df_comp['emissions_kg'] * 10
                st.write("*Calculated for 10 trips per week*")
            elif "Daily" in freq:
                df_comp['emissions_kg'] = df_comp['emissions_kg'] * 14
                st.write("*Calculated for 14 trips per week*")
                
            fig = px.bar(df_comp, x='mode', y='emissions_kg', 
                        title='CO2e by Transit Mode (Lower is Better)',
                        color='emissions_kg', color_continuous_scale='Greens_r')
            st.plotly_chart(fig, width="stretch")
            
            st.dataframe(df_comp.style.format({'emissions_kg': '{:.2f}'}))
            
        except Exception as e:
            st.error(f"Error calculating emissions: {e}")

with offset_col:
    st.subheader("🛒 Simulated Offset Marketplace")
    st.info("💡 Invest your simulated eco-points to offset carbon.")
    
    projects = get_offset_projects()
    proj_names = [p["name"] for p in projects]
    selected_proj_name = st.selectbox("Select an Offset Project", proj_names)
    
    selected_proj = next(p for p in projects if p["name"] == selected_proj_name)
    
    st.markdown(f"**{selected_proj['image']} {selected_proj['name']}**")
    st.write(f"*{selected_proj['description']}*")
    st.write(f"**Category:** {selected_proj['category']} | **Region:** {selected_proj['region']}")
    st.write(f"**Cost:** ${selected_proj['cost_per_tonne']:.2f} per tonne")
    
    with st.form("offset_form"):
        tonnes = st.number_input("Tonnes of CO2e to Offset", min_value=0.1, value=1.0, step=0.1)
        purchase_btn = st.form_submit_button("Purchase Simulated Offset")
        
        if purchase_btn:
            is_valid, msg = validate_offset_transaction(tonnes, selected_proj["available_capacity"])
            if is_valid:
                cost = calculate_offset_cost(tonnes, selected_proj["cost_per_tonne"])
                if save_offset_transaction(st.session_state.user_id, selected_proj["id"], selected_proj["name"], tonnes, selected_proj["cost_per_tonne"], cost):
                    st.success(f"Simulated purchase successful! Offset {tonnes}t for ${cost:.2f}.")
                else:
                    st.error("Failed to save transaction.")
            else:
                st.error(msg)

st.markdown("---")

st.markdown("<div class='section-header'>📈 Your Offset Portfolio</div>", unsafe_allow_html=True)
port_col1, port_col2 = st.columns([1, 2])

with port_col1:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    total_offsets = get_total_offsets(st.session_state.user_id)
    total_spend = get_total_spend(st.session_state.user_id)
    st.metric("Total Tonnes Offset", f"{total_offsets:.2f}t")
    st.metric("Total Simulated Spend", f"${total_spend:.2f}")
    
    estimated_footprint = 50.0  # Just a placeholder lifetime footprint
    net_progress = calculate_net_zero_progress(estimated_footprint, total_offsets)
    st.metric("Net-Zero Progress (Estimated)", f"{net_progress:.1f}%")
    st.progress(net_progress / 100)
    st.markdown("</div>", unsafe_allow_html=True)

with port_col2:
    st.subheader("Transaction History")
    transactions = get_offset_transactions(st.session_state.user_id)
    if transactions:
        df_trans = pd.DataFrame(transactions)
        st.dataframe(df_trans[['created_at', 'project_name', 'offset_tonnes', 'total_cost', 'transaction_status']])
        
        # Button to clear history for demo purposes
        if st.button("Clear History"):
            for t in transactions:
                delete_offset_transaction(t['id'])
            st.rerun()
    else:
        st.info("No transactions yet. Visit the marketplace to start your portfolio!")
