"""
Authentication module for Home Hub
Handles user login, session management, and password storage
"""
import streamlit as st
from datetime import datetime, timedelta

# User credentials - EDIT HERE TO CHANGE PASSWORDS
USERS = {
    'sanjai': {
        'password': '7305559689',
        'name': 'Sanjai'
    },
    'pradhiksha': {
        'password': '603103',
        'name': 'Pradhiksha'
    }
}

# Session timeout (30 days for Remember Me)
REMEMBER_ME_DAYS = 30


def hash_password(password):
    """Hash password for secure comparison (optional, keeping plain for easy changes)"""
    return password  # Using plain text for easy password changes


def verify_credentials(username, password):
    """Verify username and password"""
    username = username.lower().strip()
    if username in USERS:
        return USERS[username]['password'] == password
    return False


def get_user_name(username):
    """Get display name for user"""
    username = username.lower().strip()
    if username in USERS:
        return USERS[username]['name']
    return username


def auto_login_from_url():
    """Check URL for remember-me token and auto-login"""
    try:
        # Check if remember_user is in query params
        if 'remember_user' in st.query_params:
            username = st.query_params['remember_user']
            if username in USERS and 'authenticated' not in st.session_state:
                # Auto-login this user
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.session_state['user_display_name'] = USERS[username]['name']
                st.session_state['remember_me'] = True
                return True
    except Exception:
        pass
    return False


def login(username, password, remember_me=False):
    """
    Attempt to log in user
    Returns: (success: bool, message: str)
    """
    if verify_credentials(username, password):
        username = username.lower().strip()
        
        # Set session state
        st.session_state['authenticated'] = True
        st.session_state['username'] = username
        st.session_state['user_display_name'] = get_user_name(username)
        st.session_state['login_time'] = datetime.now()
        st.session_state['remember_me'] = remember_me
        
        # Add remember_user to URL if remember me is checked
        if remember_me:
            st.query_params['remember_user'] = username
            
        return True, f"Welcome back, {get_user_name(username)}!"
    else:
        return False, "Invalid username or password"


def logout():
    """Log out current user"""
    # Remove remember_user from URL
    if 'remember_user' in st.query_params:
        del st.query_params['remember_user']
    
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def is_authenticated():
    """Check if user is authenticated"""
    # First check if we can auto-login from URL
    if 'authenticated' not in st.session_state:
        auto_login_from_url()
    
    return st.session_state.get('authenticated', False)


def require_auth():
    """
    Decorator/check for pages that require authentication
    Shows login prompt if not authenticated
    """
    # Try to restore session from browser first
    if not is_authenticated():
        st.warning("⚠️ Please log in to access Home Hub")
        
        # Show inline login form
        st.subheader("🔐 Quick Login")
        with st.form("quick_login_form"):
            username = st.text_input("Username", placeholder="sanjai or pradhiksha")
            password = st.text_input("Password", type="password")
            remember_me = st.checkbox("Remember me for 30 days", value=True)
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if username and password:
                    success, message = login(username, password, remember_me)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter username and password")
        
        st.stop()
    return True


def get_current_user():
    """Get current logged in username"""
    return st.session_state.get('username', None)


def get_current_user_display():
    """Get current logged in user's display name"""
    return st.session_state.get('user_display_name', 'User')


def render_logout_button():
    """Render logout button in sidebar"""
    if is_authenticated():
        st.sidebar.divider()
        st.sidebar.write(f"👤 Logged in as: **{get_current_user_display()}**")
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()


# Instructions for changing passwords
"""
TO CHANGE PASSWORDS:
1. Open this file: auth.py
2. Find the USERS dictionary above
3. Change the 'password' value for any user
4. Save the file
5. Restart Streamlit

Example:
USERS = {
    'sanjai': {
        'password': 'NEW_PASSWORD_HERE',
        'name': 'Sanjai'
    },
    ...
}
"""
