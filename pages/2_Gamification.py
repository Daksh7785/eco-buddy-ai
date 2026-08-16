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


st.markdown("<div class='section-header'>🎮 Your Eco Journey</div>", unsafe_allow_html=True)

# Header: Level, XP, Streak
total_xp = gf.get_total_xp(1)
level = gf.calculate_level(total_xp)
progress = gf.calculate_level_progress(total_xp)
streak = gf.calculate_streak(1, [])

g_col1, g_col2, g_col3 = st.columns(3)
g_col1.metric("Current Level", f"Lvl {level}")
g_col2.metric("Total XP", f"{total_xp} XP")
g_col3.metric("Current Streak", f"{streak} Days 🔥")

st.progress(progress, text=f"Progress to Level {level+1}")

st.markdown("---")
st.markdown("### 🏆 Weekly Challenges")

user_challenges = gf.get_user_challenges(1)
enrolled_ids = [c['challenge_id'] for c in user_challenges if c['status'] != 'expired']

for ch_id, ch_data in gf.CHALLENGES.items():
    with st.expander(f"{ch_data['title']} ({ch_data['xp']} XP) - {ch_data['category']}"):
        st.write(f"Target: {ch_data['target']} {ch_data['unit']}")
        if ch_id in enrolled_ids:
            status = [c['status'] for c in user_challenges if c['challenge_id'] == ch_id][-1]
            if status == 'completed':
                st.success("Challenge Completed! 🎉")
            else:
                current_prog = [c['progress_value'] for c in user_challenges if c['challenge_id'] == ch_id][-1]
                st.write(f"Progress: {current_prog} / {ch_data['target']}")
                
                prog_val = st.number_input(f"Update Progress for {ch_id}", min_value=0.0, step=1.0, key=f"prog_{ch_id}")
                if st.button("Update", key=f"btn_prog_{ch_id}"):
                    gf.update_challenge_progress(1, ch_id, progress_increment=prog_val)
                    gf.validate_challenge_progress(1, ch_id)
                    st.rerun()
        else:
            if st.button("Enroll", key=f"enroll_{ch_id}"):
                gf.enroll_challenge(1, ch_id)
                st.rerun()

st.markdown("---")
st.markdown("### 🎖️ Achievement Badges")

unlocked = gf.get_unlocked_badges(1)
unlocked_ids = [b['badge_id'] for b in unlocked]

cols = st.columns(len(gf.BADGES))
for i, (b_id, b_data) in enumerate(gf.BADGES.items()):
    with cols[i % len(cols)]:
        if b_id in unlocked_ids:
            st.markdown(f"**✅ {b_data['name']}**")
            st.caption(b_data['desc'])
            if st.button("Share Card", key=f"share_{b_id}"):
                file_path = gf.generate_achievement_card(1, b_id, f"badge_{b_id}.png")
                if file_path:
                    with open(file_path, "rb") as f:
                        st.download_button("Download Card", f, file_name=f"badge_{b_id}.png", key=f"dl_{b_id}")
        else:
            st.markdown(f"**🔒 {b_data['name']}**")
            st.caption(b_data['desc'])

