import streamlit as st
from auth import login, is_authenticated
from theme import get_page_style, add_pwa_support

st.set_page_config(
    page_title="Login - Home Hub",
    page_icon="🏠",
    layout="centered"
)

# Add PWA support
add_pwa_support()

# Apply theme
st.markdown(get_page_style('home'), unsafe_allow_html=True)

# Custom login page styling
st.markdown("""
    <style>
        /* Center the login form */
        .login-container {
            max-width: 400px;
            margin: 4rem auto;
            padding: 2rem;
            background: white;
            border-radius: 1rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
        }
        
        /* Mobile optimizations */
        @media (max-width: 768px) {
            .login-container {
                margin: 2rem auto;
                padding: 1.5rem;
            }
            
            .stTextInput input {
                font-size: 16px !important;
                min-height: 48px !important;
            }
            
            .stButton button {
                min-height: 48px !important;
                font-size: 18px !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Check if already logged in
if is_authenticated():
    st.success("✅ You are already logged in!")
    st.info("👉 Use the sidebar to navigate to Home, Tasks, Purchases, Groceries, or Archive")
    st.stop()

# Login Header
st.markdown("""
    <div class="login-header">
        <h1>🏠 Home Hub</h1>
        <p style="margin: 0; opacity: 0.9;">Welcome Back!</p>
    </div>
""", unsafe_allow_html=True)

# Login Form
st.subheader("🔐 Login")

with st.form("login_form", clear_on_submit=False):
    username = st.text_input(
        "Username",
        placeholder="Enter your username",
        help="Use: sanjai or pradhiksha"
    )
    
    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password"
    )
    
    remember_me = st.checkbox(
        "Remember me for 30 days",
        value=True,
        help="Stay logged in on this device for 30 days"
    )
    
    col1, col2 = st.columns([2, 1])
    with col1:
        submit = st.form_submit_button("🚀 Login", use_container_width=True)
    
    if submit:
        if username and password:
            success, message = login(username, password, remember_me)
            
            if success:
                st.success(message)
                st.balloons()
                st.info("✅ Login successful! Use the sidebar to navigate.")
                # Rerun to show authenticated state
                st.rerun()
            else:
                st.error(message)
        else:
            st.warning("Please enter both username and password")

# Help section
st.markdown("---")
with st.expander("ℹ️ Need Help?"):
    st.write("""
    **Usernames:**
    - sanjai
    - pradhiksha
    
    **Forgot Password?**
    Contact the administrator to reset your password.
    
    **First Time Here?**
    Use your assigned username and password to log in.
    """)

# Footer
st.markdown("""
    <div style="text-align: center; margin-top: 3rem; color: #718096; font-size: 14px;">
        <p>🏠 Home Hub - Manage your home together</p>
        <p>Sanjai & Pradhiksha</p>
    </div>
""", unsafe_allow_html=True)
