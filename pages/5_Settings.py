import streamlit as st
import os
from style import inject_css

inject_css()

st.markdown("<div class='section-header'>⚙️ Settings</div>", unsafe_allow_html=True)

st.markdown("### 🌍 Regional Preferences")
region = st.selectbox("Select Your Region for API Emissions Factor", ["Global", "US", "UK", "EU"], index=0)
st.session_state.region = region

st.markdown("---")

st.markdown("### 🔄 Data Management")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Export Data")
    if os.path.exists("eco_buddy.db"):
        with open("eco_buddy.db", "rb") as f:
            st.download_button("Download Primary Database", f, file_name="eco_buddy.db")
    if os.path.exists("gamification.db"):
        with open("gamification.db", "rb") as f:
            st.download_button("Download Gamification Database", f, file_name="gamification.db")
    if os.path.exists("marketplace.db"):
        with open("marketplace.db", "rb") as f:
            st.download_button("Download Marketplace Database", f, file_name="marketplace.db")

with col2:
    st.markdown("#### Reset Assessment")
    DEFAULT_VALUES = {
        "transport": "Car",
        "distance": 10.0,
        "electricity": 200.0,
        "diet": "Vegetarian",
        "flights": 0,
    }
    if st.button("🔄 Reset Assessment Form"):
        for key in DEFAULT_VALUES:
            if key in st.session_state:
                del st.session_state[key]
        st.success("✅ Assessment form has been reset.")
