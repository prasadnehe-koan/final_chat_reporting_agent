import streamlit as st
from auth import (
    init_auth_database, 
    authenticate_user, 
    create_user, 
    create_session,
    is_authenticated
)

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Login - AI Procurement Assistant",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit menu
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize database
init_auth_database()

# Check if already logged in
if is_authenticated():
    st.switch_page("pages/Application.py")

# ==========================================================
# STYLING
# ==========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .login-container {
        max-width: 450px;
        margin: 2rem auto;
        padding: 2rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-logo {
        width: 120px;
        height: auto;
        margin-bottom: 1rem;
    }
    
    .login-title {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .login-subtitle {
        color: #6b7280;
        font-size: 0.95rem;
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px !important;
        border: 2px solid #e5e7eb !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.1) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin-top: 1rem !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 16px rgba(102,126,234,0.4) !important;
    }
    
    .tab-container {
        margin-bottom: 1.5rem;
    }
    
    .divider {
        text-align: center;
        margin: 1.5rem 0;
        color: #9ca3af;
        font-size: 0.875rem;
    }
    
    .footer-text {
        text-align: center;
        margin-top: 2rem;
        color: #9ca3af;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# SESSION STATE
# ==========================================================
if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False

# ==========================================================
# HEADER
# ==========================================================
LOGO_URL = "https://media.licdn.com/dms/image/v2/C4E0BAQGtXskL4EvJmA/company-logo_200_200/company-logo_200_200/0/1632401962756/koantek_logo?e=2147483647&v=beta&t=D4GLT1Pu2vvxLR1iKZZbUJWN7K_uaPSF0T1mZl6Le-o"

st.markdown(f"""
<div class="login-header">
    <img src="{LOGO_URL}" class="login-logo" alt="Logo" onerror="this.style.display='none'">
    <div class="login-title">🔐 AI Business Assistant</div>
    <div class="login-subtitle">Sign in to access your workspace</div>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# TAB SELECTOR
# ==========================================================
col1, col2 = st.columns(2)
with col1:
    if st.button("🔑 Login", use_container_width=True, type="primary" if not st.session_state.show_signup else "secondary"):
        st.session_state.show_signup = False
        st.rerun()

with col2:
    if st.button("📝 Sign Up", use_container_width=True, type="primary" if st.session_state.show_signup else "secondary"):
        st.session_state.show_signup = True
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================
# LOGIN FORM
# ==========================================================
if not st.session_state.show_signup:
    with st.form("login_form", clear_on_submit=False):
        st.markdown("### Welcome Back!")
        
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_username"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        submit = st.form_submit_button("🚀 Sign In", use_container_width=True)
        
        if submit:
            if not username or not password:
                st.error("⚠️ Please enter both username and password")
            else:
                success, user_id, username_db = authenticate_user(username, password)
                
                if success:
                    # Create session
                    session_id = create_session(user_id)
                    
                    # Store in session state
                    st.session_state.session_id = session_id
                    st.session_state.user_id = user_id
                    st.session_state.username = username_db
                    
                    st.success("✅ Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

# ==========================================================
# SIGNUP FORM
# ==========================================================
else:
    with st.form("signup_form", clear_on_submit=True):
        st.markdown("### Create Your Account")
        
        new_username = st.text_input(
            "Username",
            placeholder="Choose a username",
            key="signup_username"
        )
        
        new_email = st.text_input(
            "Email (Optional)",
            placeholder="your.email@example.com",
            key="signup_email"
        )
        
        new_password = st.text_input(
            "Password",
            type="password",
            placeholder="Choose a strong password",
            key="signup_password"
        )
        
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            key="signup_confirm"
        )
        
        submit = st.form_submit_button("📝 Create Account", use_container_width=True)
        
        if submit:
            if not new_username or not new_password:
                st.error("⚠️ Username and password are required")
            elif new_password != confirm_password:
                st.error("⚠️ Passwords do not match")
            elif len(new_password) < 6:
                st.error("⚠️ Password must be at least 6 characters long")
            else:
                success, message = create_user(
                    new_username, 
                    new_password, 
                    new_email if new_email else None
                )
                
                if success:
                    st.success(f"✅ {message} Please login!")
                    st.session_state.show_signup = False
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

# ==========================================================
# FOOTER
# ==========================================================
st.markdown("""
<div class="footer-text">
    🔒 Your data is secure and encrypted<br>
    Powered by Koantek
</div>
""", unsafe_allow_html=True)
