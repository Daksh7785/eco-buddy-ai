import html
import time
import streamlit as st
import os
from dotenv import load_dotenv

from database import init_db, init_gamification_db, init_marketplace_db, create_user, verify_user
from style import inject_css

load_dotenv()

# -------------------------
# INIT
# -------------------------
init_db()
init_gamification_db()
init_marketplace_db()

st.set_page_config(
    page_title="EcoBuddy - Login",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# -------------------------
# HEADER
# -------------------------
st.markdown("<div class='title'>🌱 EcoBuddy AI+</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Your Personal AI-Powered Carbon Footprint Tracker & Eco Assistant</div>", unsafe_allow_html=True)

# -------------------------
# AUTHENTICATION
# -------------------------
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
    st.session_state.username = None

if st.session_state.user_id is None:
    st.markdown("### Welcome! Please Login or Register to continue.")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            login_username = st.text_input("Username")
            login_password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Login")
            
            if submit_login:
                if not login_username or not login_password:
                    st.error("Please enter both username and password.")
                else:
                    user_id = verify_user(login_username, login_password)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.session_state.username = login_username
                        st.success("Login successful! Redirecting...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                        
    with tab2:
        st.subheader("Register")
        with st.form("register_form"):
            reg_username = st.text_input("Username")
            reg_email = st.text_input("Email")
            reg_password = st.text_input("Password", type="password")
            reg_confirm = st.text_input("Confirm Password", type="password")
            submit_register = st.form_submit_button("Register")
            
            if submit_register:
                if not reg_username or not reg_email or not reg_password:
                    st.error("Please fill all fields.")
                elif reg_password != reg_confirm:
                    st.error("Passwords do not match.")
                else:
                    user_id = create_user(reg_username, reg_email, reg_password)
                    if user_id:
                        st.success("Registration successful! You can now login.")
                    else:
                        st.error("Username or email already exists.")
else:
    st.success(f"Welcome back, {st.session_state.username}!")
    
    st.markdown("""
    <div style='text-align: center; margin-top: 30px;'>
        <h3>Use the sidebar on the left to navigate to:</h3>
        <ul style='list-style-type: none; font-size: 18px; line-height: 2;'>
            <li>🌍 Dashboard & Carbon Footprint</li>
            <li>🎮 Gamification & Badges</li>
            <li>🛒 Marketplace & Offsets</li>
            <li>⚡ Energy Audit</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Logout"):
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()
