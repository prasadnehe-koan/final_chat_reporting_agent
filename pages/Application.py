import streamlit as st

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="AI Business Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide default Streamlit menu
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ==========================================================
# HEADER
# ==========================================================
LOGO_URL = "https://media.licdn.com/dms/image/v2/C4E0BAQGtXskL4EvJmA/company-logo_200_200/company-logo_200_200/0/1632401962756/koantek_logo?e=2147483647&v=beta&t=D4GLT1Pu2vvxLR1iKZZbUJWN7K_uaPSF0T1mZl6Le-o"

st.markdown(f"""
<style>
    .main-header {{
        background:  linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.25rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.25rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    
    .header-content {{
        flex: 1;
    }}
    
    .header-logo {{
        height: 60px;
        width: auto;
        max-width: 200px;
        object-fit: contain;
    }}
    
    .main-header h1 {{
        color: white;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
    }}
    
    .main-header p {{
        color: rgba(255,255,255,0.9);
        font-size: 0.875rem;
        margin: 0.25rem 0 0 0;
    }}
    
    /* Style the buttons to look like nav cards */
    button[kind="secondary"], button[kind="primary"], button[data-baseweb="button"] {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 2rem !important;
        height: 220px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        white-space: pre-line !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
    }}

    /* Hover */
    button[kind="secondary"]:hover,
    button[kind="primary"]:hover,
    button[data-baseweb="button"]:hover {{
        transform: translateY(-5px) !important;
        box-shadow: 0 8px 12px rgba(102,126,234,0.4) !important;
    }}

    /* Pressed */
    button[kind="secondary"]:active,
    button[kind="primary"]:active,
    button[data-baseweb="button"]:active {{
        transform: translateY(-2px) !important;
    }}

    /* Button container and text */
    button[kind="secondary"] div,
    button[kind="primary"] div,
    button[data-baseweb="button"] div {{
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        width: 100% !important;
    }}

    /* Emoji icon size - much larger */
    button[kind="secondary"] div p:first-child,
    button[kind="primary"] div p:first-child,
    button[data-baseweb="button"] div p:first-child {{
        font-size: 4.5rem !important;
        line-height: 1 !important;
        margin: 0 0 1rem 0 !important;
    }}

    /* Title text */
    button[kind="secondary"] div p:nth-child(2),
    button[kind="primary"] div p:nth-child(2),
    button[data-baseweb="button"] div p:nth-child(2) {{
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        line-height: 1.3 !important;
        margin: 0.5rem 0 !important;
    }}

    /* Description text */
    button[kind="secondary"] div p:last-child,
    button[kind="primary"] div p:last-child,
    button[data-baseweb="button"] div p:last-child {{
        font-size: 0.95rem !important;
        opacity: 0.9 !important;
        line-height: 1.4 !important;
        margin: 0.3rem 0 0 0 !important;
    }}

    /* Select a Tool heading */
    .stMarkdown h2 {{
        text-align: center;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        color: #1f2937;
    }}

</style>

<div class="main-header">
    <div class="header-content">
        <h1>🧠 AI Business Assistant</h1>
        <p>Choose your tool below</p>
    </div>
    <img src="{LOGO_URL}" class="header-logo" alt="Koantek Logo" onerror="this.style.display='none'">
</div>
""", unsafe_allow_html=True)

# ==========================================================
# NAVIGATION CARDS
# ==========================================================
st.markdown("## Select a Tool")

col1, col2 = st.columns(2)

with col1:
    if st.button("📊\n\nReport Generator\n\nAI-powered business reports", key="nav_report", use_container_width=True):
        st.switch_page("pages/1_Report_Generator.py")

with col2:
    if st.button("💬\n\nAI Chatbot\n\nChat with AI about your business data", key="nav_chat", use_container_width=True):
        st.switch_page("pages/2_Chatbot.py")

# ==========================================================
# FOOTER
# ==========================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; font-size: 0.8rem; padding: 0.75rem;">
    <p style="color: #6b7280;">Powered by Koantek</p>
</div>
""", unsafe_allow_html=True)


# import streamlit as st

# # ==========================================================
# # PAGE CONFIG
# # ==========================================================
# st.set_page_config(
#     page_title="AI Business Assistant",
#     page_icon="📊",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# # Hide default Streamlit menu
# hide_streamlit_style = """
# <style>
# #MainMenu {visibility: hidden;}
# footer {visibility: hidden;}
# .stDeployButton {display:none;}
# </style>
# """
# st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# # ==========================================================
# # HEADER
# # ==========================================================
# LOGO_URL = "https://media.licdn.com/dms/image/v2/C4E0BAQGtXskL4EvJmA/company-logo_200_200/company-logo_200_200/0/1632401962756/koantek_logo?e=2147483647&v=beta&t=D4GLT1Pu2vvxLR1iKZZbUJWN7K_uaPSF0T1mZl6Le-o"

# st.markdown(f"""
# <style>
#     .main-header {{
#         background:  linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         padding: 1.25rem 1.5rem;
#         border-radius: 10px;
#         margin-bottom: 1.25rem;
#         box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#         display: flex;
#         justify-content: space-between;
#         align-items: center;
#     }}
    
#     .header-content {{
#         flex: 1;
#     }}
    
#     .header-logo {{
#         height: 60px;
#         width: auto;
#         max-width: 200px;
#         object-fit: contain;
#     }}
    
#     .main-header h1 {{
#         color: white;
#         font-size: 1.5rem;
#         font-weight: 700;
#         margin: 0;
#     }}
    
#     .main-header p {{
#         color: rgba(255,255,255,0.9);
#         font-size: 0.875rem;
#         margin: 0.25rem 0 0 0;
#     }}
    
#     .nav-card {{
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         padding: 2rem;
#         border-radius: 10px;
#         color: white;
#         text-align: center;
#         cursor: pointer;
#         transition: all 0.3s ease;
#         box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#         height: 200px;
#         display: flex;
#         flex-direction: column;
#         justify-content: center;
#         align-items: center;
#         margin-bottom: 1rem;
#     }}
    
#     .nav-card:hover {{
#         transform: translateY(-5px);
#         box-shadow: 0 8px 12px rgba(102,126,234,0.4);
#     }}
    
#     .nav-icon {{
#         font-size: 3rem;
#         margin-bottom: 1rem;
#     }}
    
#     .nav-title {{
#         font-size: 1.5rem;
#         font-weight: 700;
#         margin-bottom: 0.5rem;
#     }}
    
#     .nav-description {{
#         font-size: 0.9rem;
#         opacity: 0.9;
#     }}
    
#     /* Style the buttons to look like nav cards */
#     /* Remove Streamlit's default orange background */
#     button[kind="secondary"], button[kind="primary"], button[data-baseweb="button"] {{
#     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
#     color: white !important;
#     border: none !important;
#     border-radius: 10px !important;
#     padding: 2rem !important;
#     height: 200px !important;
#     transition: all 0.3s ease !important;
#     box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
#     white-space: pre-line !important;
#     font-size: 4rem !important;
#     line-height: 1.8 !important;
# }}

# /* Hover */
# button[kind="secondary"]:hover,
# button[kind="primary"]:hover,
# button[data-baseweb="button"]:hover {{
#     transform: translateY(-5px) !important;
#     box-shadow: 0 8px 12px rgba(102,126,234,0.4) !important;
# }}

# /* Pressed */
# button[kind="secondary"]:active,
# button[kind="primary"]:active,
# button[data-baseweb="button"]:active {{
#     transform: translateY(-2px) !important;
# }}
# /* Increase inside text + emoji icon size */
# button[kind="secondary"],
# button[kind="primary"],
# button[data-baseweb="button"] {{
#     font-size: 2rem !important;      /* ⬆️ Increase text size */
#     line-height: 1rem !important;    /* Better spacing */
#     padding-top: 2.5rem !important;
#     padding-bottom: 2.5rem !important;
# }}

# /* If icon/emoji is used (📊, 💬 etc), increase size */
# button[kind="secondary"] span,
# button[kind="primary"] span,
# button[data-baseweb="button"] div span {{
#     font-size: 4 rem !important;
#     line-height: 3.2rem !important;
# }}     

# /* To ensure multiline stays centered */
# button[kind="secondary"] div,
# button[kind="primary"] div,
# button[data-baseweb="button"] div {{
#     font-size: 1.1rem !important;
#     white-space: pre-line !important;
#     text-align: center !important;
# }}


# </style>

# <div class="main-header">
#     <div class="header-content">
#         <h1>📊 AI Business Assistant</h1>
#         <p>Choose your tool below</p>
#     </div>
#     <img src="{LOGO_URL}" class="header-logo" alt="Koantek Logo" onerror="this.style.display='none'">
# </div>
# """, unsafe_allow_html=True)

# # ==========================================================
# # NAVIGATION CARDS
# # ==========================================================
# st.markdown("## Select a Tool")

# col1, col2 = st.columns(2)

# with col1:
#     if st.button("📊\n\nReport Generator\n\n AI-powered business reports", key="nav_report", use_container_width=True):
#         st.switch_page("pages/1_Report_Generator.py")

# with col2:
#     if st.button("💬\n\nAI Chatbot\n\nChat with AI about your business data", key="nav_chat", use_container_width=True):
#         st.switch_page("pages/2_Chatbot.py")

# # ==========================================================
# # FOOTER
# # ==========================================================
# st.markdown("---")
# st.markdown("""
# <div style="text-align: center; font-size: 0.8rem; padding: 0.75rem;">
#     <p style="color: #6b7280;">Powered by Koantek</p>
# </div>
# """, unsafe_allow_html=True)
