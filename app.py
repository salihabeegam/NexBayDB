# app.py - Department-based dashboard interface (BEIGE THEME)

import streamlit as st
import pandas as pd
from io import BytesIO
from database import VesselDatabase, initialize_database
import os

# Page configuration
st.set_page_config(
    page_title="NexBay International - Management System",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# BEIGE THEME CSS
st.markdown("""
<style>
    /* Hide sidebar */
    [data-testid="collapsedControl"] {
        display: none;
    }
    section[data-testid="stSidebar"] {
        display: none;
    }

    /* Main background */
    .main {
        background-color: #f5f1e8;
    }

    /* Main header */
    .main-header {
        text-align: center;
        padding: 50px 0;
        background: linear-gradient(135deg, #8b7355 0%, #6b5444 100%);
        color: #fff;
        border-radius: 15px;
        margin-bottom: 40px;
        box-shadow: 0 4px 15px rgba(107, 84, 68, 0.3);
    }

    .company-name {
        font-size: 52px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #fff;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }

    .company-tagline {
        font-size: 20px;
        font-style: italic;
        opacity: 0.95;
        color: #f5f1e8;
    }

    /* Breadcrumb styling */
    .breadcrumb {
        padding: 15px 0;
        font-size: 15px;
        color: #6b5444;
        font-weight: 500;
    }

    /* Department cards */
    .dept-card-ops {
        background: linear-gradient(135deg, #d4a574 0%, #c69463 100%);
    }

    .dept-card-accounts {
        background: linear-gradient(135deg, #b8956a 0%, #a67c52 100%);
    }

    .dept-card-sales {
        background: linear-gradient(135deg, #9e8b6f 0%, #8b7355 100%);
    }

    /* Buttons */
    .stButton>button {
        background-color: #8b7355;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #6b5444;
        box-shadow: 0 4px 12px rgba(107, 84, 68, 0.3);
        transform: translateY(-2px);
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #6b5444;
    }

    /* Info boxes */
    .stAlert {
        background-color: #fff8f0;
        border-left: 4px solid #c69463;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #fff8f0;
        border-radius: 8px;
        color: #6b5444;
    }

    /* Input fields */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>select {
        background-color: #ffffff;
        border: 1px solid #d4a574;
        border-radius: 8px;
        color: #4a3f35;
    }

    /* Radio buttons */
    .stRadio>div {
        background-color: #fff8f0;
        padding: 10px;
        border-radius: 8px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f5f1e8;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #fff8f0;
        border-radius: 8px 8px 0 0;
        color: #6b5444;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background-color: #8b7355;
        color: white;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #fff8f0;
        border: 2px dashed #c69463;
        border-radius: 10px;
    }

    /* DataFrames */
    .dataframe {
        background-color: white;
        border-radius: 8px;
    }

    /* Success/Error messages */
    .stSuccess {
        background-color: #e8f5e9;
        border-left: 4px solid #81c784;
    }

    .stError {
        background-color: #ffebee;
        border-left: 4px solid #e57373;
    }

    .stWarning {
        background-color: #fff8e1;
        border-left: 4px solid #ffd54f;
    }
</style>
""", unsafe_allow_html=True)

# Initialize
initialize_database()
db = VesselDatabase()

# Session state
if 'current_department' not in st.session_state:
    st.session_state.current_department = None
if 'current_section' not in st.session_state:
    st.session_state.current_section = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = None


# Navigation
def go_to_department(dept):
    st.session_state.current_department = dept
    st.session_state.current_section = None
    st.session_state.current_page = None


def go_to_section(section):
    st.session_state.current_section = section
    st.session_state.current_page = None


def go_to_page(page):
    st.session_state.current_page = page


def go_home():
    st.session_state.current_department = None
    st.session_state.current_section = None
    st.session_state.current_page = None


# ===================================
# MAIN DASHBOARD
# ===================================
def show_main_dashboard():
    st.markdown("""
    <div class="main-header">
        <div class="company-name">⚓ NexBay International LLC</div>
        <div class="company-tagline">Moving Your Fleet Forward....</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🏢 Select Department")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #d4a574 0%, #c69463 100%); border-radius: 15px; color: white; height: 200px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 4px 15px rgba(212, 165, 116, 0.3); transition: transform 0.3s;">
            <div style="font-size: 60px; margin-bottom: 15px;">🔧</div>
            <div style="font-size: 26px; font-weight: bold;">Operations</div>
            <div style="font-size: 14px; opacity: 0.95; margin-top: 8px;">Manager & Vessel Management</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Operations →", key="btn_ops", use_container_width=True, type="primary"):
            go_to_department("Operations")
            st.rerun()

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #b8956a 0%, #a67c52 100%); border-radius: 15px; color: white; height: 200px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 4px 15px rgba(184, 149, 106, 0.3);">
            <div style="font-size: 60px; margin-bottom: 15px;">💰</div>
            <div style="font-size: 26px; font-weight: bold;">Accounts</div>
            <div style="font-size: 14px; opacity: 0.95; margin-top: 8px;">Invoice Generation & Management</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Accounts →", key="btn_acc", use_container_width=True, type="primary"):
            go_to_department("Accounts")
            st.rerun()

    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #9e8b6f 0%, #8b7355 100%); border-radius: 15px; color: white; height: 200px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 4px 15px rgba(158, 139, 111, 0.3);">
            <div style="font-size: 60px; margin-bottom: 15px;">📧</div>
            <div style="font-size: 26px; font-weight: bold;">Sales & Marketing</div>
            <div style="font-size: 14px; opacity: 0.95; margin-top: 8px;">Email Communications</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Sales & Marketing →", key="btn_sales", use_container_width=True, type="primary"):
            go_to_department("Sales & Marketing")
            st.rerun()


# ===================================
# OPERATIONS DEPARTMENT
# ===================================
def show_operations_department():
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown('<p class="breadcrumb">🏠 Home > <strong>🔧 Operations</strong></p>', unsafe_allow_html=True)
    with col2:
        if st.button("🏠 Home", use_container_width=True, key="home_ops"):
            go_home()
            st.rerun()

    st.title("🔧 Operations Department")
    st.markdown("---")

    if not st.session_state.current_section:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #d4a574 0%, #c69463 100%); padding: 35px; border-radius: 15px; color: white; box-shadow: 0 4px 15px rgba(212, 165, 116, 0.3);">
                <h2 style="margin: 0; color: white;">👔 Manager Management</h2>
                <p style="margin: 10px 0 0 0; opacity: 0.95; font-size: 15px;">Add, view, edit, and manage company managers</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Manager Management →", use_container_width=True, type="primary", key="btn_mgr"):
                go_to_section("Manager Management")
                st.rerun()

        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #b8956a 0%, #a67c52 100%); padding: 35px; border-radius: 15px; color: white; box-shadow: 0 4px 15px rgba(184, 149, 106, 0.3);">
                <h2 style="margin: 0; color: white;">⚓ Vessel Management</h2>
                <p style="margin: 10px 0 0 0; opacity: 0.95; font-size: 15px;">Add, view, edit, and manage vessel/master details</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Vessel Management →", use_container_width=True, type="primary", key="btn_vessel"):
                go_to_section("Vessel Management")
                st.rerun()

    elif st.session_state.current_section == "Manager Management":
        show_manager_management()
    elif st.session_state.current_section == "Vessel Management":
        show_vessel_management()


def show_manager_management():
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        st.markdown('<p class="breadcrumb">🏠 Home > 🔧 Operations > <strong>👔 Manager Management</strong></p>',
                    unsafe_allow_html=True)
    with col2:
        if st.button("⬅️ Back", use_container_width=True, key="back_mgr"):
            st.session_state.current_section = None
            st.rerun()
    with col3:
        if st.button("🏠 Home", use_container_width=True, key="home_mgr"):
            go_home()
            st.rerun()

    st.title("👔 Manager Management")

    from pages import manager_operations
    manager_operations.show_manager_page(db)


def show_vessel_management():
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        st.markdown('<p class="breadcrumb">🏠 Home > 🔧 Operations > <strong>⚓ Vessel Management</strong></p>',
                    unsafe_allow_html=True)
    with col2:
        if st.button("⬅️ Back", use_container_width=True, key="back_vessel"):
            st.session_state.current_section = None
            st.rerun()
    with col3:
        if st.button("🏠 Home", use_container_width=True, key="home_vessel"):
            go_home()
            st.rerun()

    st.title("⚓ Vessel/Master Management")

    from pages import vessel_operations
    vessel_operations.show_vessel_page(db)


# ===================================
# ACCOUNTS DEPARTMENT
# ===================================
def show_accounts_department():
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown('<p class="breadcrumb">🏠 Home > <strong>💰 Accounts</strong></p>', unsafe_allow_html=True)
    with col2:
        if st.button("🏠 Home", use_container_width=True, key="home_acc"):
            go_home()
            st.rerun()

    st.title("💰 Accounts Department")
    st.markdown("---")

    from pages import invoice_operations
    invoice_operations.show_invoice_page(db)


# ===================================
# SALES & MARKETING DEPARTMENT
# ===================================
def show_sales_marketing_department():
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown('<p class="breadcrumb">🏠 Home > <strong>📧 Sales & Marketing</strong></p>', unsafe_allow_html=True)
    with col2:
        if st.button("🏠 Home", use_container_width=True, key="home_sales"):
            go_home()
            st.rerun()

    st.title("📧 Sales & Marketing Department")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #d4a574 0%, #c69463 100%); padding: 35px; border-radius: 15px; color: white; box-shadow: 0 4px 15px rgba(212, 165, 116, 0.3);">
            <h2 style="margin: 0; color: white;">📧 Email to Managers</h2>
            <p style="margin: 10px 0 0 0; opacity: 0.95;">Send emails to company managers</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Send to Managers →", use_container_width=True, type="primary", key="btn_email_mgr"):
            go_to_page("Email Managers")
            st.rerun()

    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #b8956a 0%, #a67c52 100%); padding: 35px; border-radius: 15px; color: white; box-shadow: 0 4px 15px rgba(184, 149, 106, 0.3);">
            <h2 style="margin: 0; color: white;">📧 Email to Vessels</h2>
            <p style="margin: 10px 0 0 0; opacity: 0.95;">Send emails to vessel masters</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Send to Vessels →", use_container_width=True, type="primary", key="btn_email_vessel"):
            go_to_page("Email Vessels")
            st.rerun()

    if st.session_state.current_page == "Email Managers":
        st.markdown("---")
        from pages import email_operations
        email_operations.show_manager_email_page(db)

    elif st.session_state.current_page == "Email Vessels":
        st.markdown("---")
        from pages import email_operations
        email_operations.show_vessel_email_page(db)


# ===================================
# MAIN APP LOGIC
# ===================================
def main():
    if not st.session_state.current_department:
        show_main_dashboard()
    elif st.session_state.current_department == "Operations":
        show_operations_department()
    elif st.session_state.current_department == "Accounts":
        show_accounts_department()
    elif st.session_state.current_department == "Sales & Marketing":
        show_sales_marketing_department()


if __name__ == "__main__":
    main()