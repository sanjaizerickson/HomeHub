"""
Theme and styling configuration for Home Hub
"""
import streamlit as st

# Theme presets
THEMES = {
    'dark': {
        'background': '#0e1117',
        'secondary_bg': '#262730',
        'text': '#fafafa',
        'card_bg': '#1e1e1e'
    },
    'light': {
        'background': '#ffffff',
        'secondary_bg': '#f0f2f6',
        'text': '#262730',
        'card_bg': '#ffffff'
    }
}

# Color scheme for each page
COLORS = {
    'home': {
        'primary': '#667eea',
        'secondary': '#764ba2',
        'gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'text': '#ffffff'
    },
    'tasks': {
        'primary': '#4299e1',
        'secondary': '#3182ce',
        'light': '#bee3f8',
        'text': '#ffffff'
    },
    'shopping': {
        'primary': '#48bb78',
        'secondary': '#38a169',
        'light': '#c6f6d5',
        'text': '#ffffff'
    },
    'groceries': {
        'primary': '#f87171',
        'secondary': '#ef4444',
        'light': '#fecaca',
        'text': '#ffffff'
    },
    'archive': {
        'primary': '#718096',
        'secondary': '#4a5568',
        'light': '#e2e8f0',
        'text': '#ffffff'
    }
}

def apply_theme_switcher():
    """Add theme switcher to sidebar and return current theme"""
    with st.sidebar:
        st.markdown("---")
        theme_choice = st.radio(
            "🎨 Theme",
            options=["System Default", "Dark", "Light"],
            index=0,
            key="theme_preference",
            horizontal=False
        )
        
        # Determine active theme
        if theme_choice == "Dark":
            return 'dark'
        elif theme_choice == "Light":
            return 'light'
        else:
            # System default - check browser preference
            return 'system'


def get_theme_css(theme_mode):
    """Generate CSS for theme override"""
    if theme_mode == 'system':
        # Use CSS media query for system preference
        return """
        <style>
            @media (prefers-color-scheme: dark) {
                :root, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
                    background-color: #0e1117 !important;
                    color: #fafafa !important;
                }
                [data-testid="stSidebar"] {
                    background-color: #262730 !important;
                }
            }
            @media (prefers-color-scheme: light) {
                :root, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
                    background-color: #ffffff !important;
                    color: #262730 !important;
                }
                [data-testid="stSidebar"] {
                    background-color: #f0f2f6 !important;
                }
            }
        </style>
        """
    
    theme = THEMES.get(theme_mode, THEMES['dark'])
    return f"""
    <style>
        :root, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
            background-color: {theme['background']} !important;
            color: {theme['text']} !important;
        }}
        [data-testid="stSidebar"] {{
            background-color: {theme['secondary_bg']} !important;
        }}
        .stTextInput > div > div, .stSelectbox > div > div, .stTextArea > div > div {{
            background-color: {theme['card_bg']} !important;
            color: {theme['text']} !important;
        }}
    </style>
    """


def get_page_style(page_name, mobile_optimized=True):
    """Generate custom CSS for a specific page"""
    color = COLORS.get(page_name, COLORS['home'])
    
    base_style = f"""
    <style>
        /* Page header styling */
        .main-header {{
            background: {color['gradient'] if 'gradient' in color else color['primary']};
            padding: 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
            color: {color['text']};
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        /* Highlight main pages with background color (Tasks, Shopping, Groceries) */
        [data-testid="stSidebarNav"] ul li:nth-child(3) a,
        [data-testid="stSidebarNav"] ul li:nth-child(4) a,
        [data-testid="stSidebarNav"] ul li:nth-child(5) a,
        [data-testid="stSidebarNav"] a[href*="1_Tasks"],
        [data-testid="stSidebarNav"] a[href*="2_Shopping"],
        [data-testid="stSidebarNav"] a[href*="3_Groceries"] {{
            background: linear-gradient(90deg, rgba(102, 126, 234, 0.2) 0%, rgba(102, 126, 234, 0.08) 100%) !important;
            border-left: 4px solid rgba(102, 126, 234, 0.9) !important;
            border-radius: 8px !important;
            padding: 0.75rem 1rem !important;
            margin: 0.25rem 0.5rem !important;
            font-weight: 600 !important;
            font-size: 1.05rem !important;
            transition: all 0.2s ease !important;
        }}
        
        [data-testid="stSidebarNav"] ul li:nth-child(3) a:hover,
        [data-testid="stSidebarNav"] ul li:nth-child(4) a:hover,
        [data-testid="stSidebarNav"] ul li:nth-child(5) a:hover,
        [data-testid="stSidebarNav"] a[href*="1_Tasks"]:hover,
        [data-testid="stSidebarNav"] a[href*="2_Shopping"]:hover,
        [data-testid="stSidebarNav"] a[href*="3_Groceries"]:hover {{
            background: linear-gradient(90deg, rgba(102, 126, 234, 0.3) 0%, rgba(102, 126, 234, 0.15) 100%) !important;
            transform: translateX(3px) !important;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
        }}
        
        /* Secondary pages (Login, Home, Archive) - plain and dimmed */
        [data-testid="stSidebarNav"] ul li:nth-child(1) a,
        [data-testid="stSidebarNav"] ul li:nth-child(2) a,
        [data-testid="stSidebarNav"] ul li:nth-child(6) a,
        [data-testid="stSidebarNav"] a[href*="Login"],
        [data-testid="stSidebarNav"] a[href*="0_Home"],
        [data-testid="stSidebarNav"] a[href*="5_Archive"] {{
            opacity: 0.55 !important;
            font-size: 0.9rem !important;
            padding: 0.5rem 1rem !important;
            margin: 0.1rem 0.5rem !important;
            font-weight: 400 !important;
        }}
        
        [data-testid="stSidebarNav"] ul li:nth-child(1) a:hover,
        [data-testid="stSidebarNav"] ul li:nth-child(2) a:hover,
        [data-testid="stSidebarNav"] ul li:nth-child(6) a:hover,
        [data-testid="stSidebarNav"] a[href*="Login"]:hover,
        [data-testid="stSidebarNav"] a[href*="0_Home"]:hover,
        [data-testid="stSidebarNav"] a[href*="5_Archive"]:hover {{
            opacity: 0.85 !important;
            background: rgba(255, 255, 255, 0.05) !important;
            border-radius: 8px !important;
        }}
        
        /* Mobile optimizations */
        {''.join([
            '''
        @media (max-width: 768px) {{
            .main-header {{
                padding: 1.5rem 1rem;
                margin-bottom: 1.5rem;
            }}
            
            /* Larger touch targets */
            .stButton button {{
                min-height: 48px !important;
                font-size: 16px !important;
                padding: 12px 24px !important;
                width: 100% !important;
            }}
            
            /* Better spacing */
            .element-container {{
                margin-bottom: 1rem !important;
            }}
            
            /* Larger fonts */
            p, span, div {{
                font-size: 16px !important;
            }}
            
            h1 {{
                font-size: 28px !important;
            }}
            
            h2 {{
                font-size: 24px !important;
            }}
            
            h3 {{
                font-size: 20px !important;
            }}
            
            /* Better expanders */
            .streamlit-expanderHeader {{
                font-size: 16px !important;
                padding: 1rem !important;
            }}
            
            /* Form inputs */
            input, textarea, select {{
                font-size: 16px !important;
                min-height: 44px !important;
            }}
        }}
        ''' if mobile_optimized else ''])}
        
        /* Custom button colors */
        .stButton button {{
            background-color: {color['primary']} !important;
            color: {color['text']} !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }}
        
        .stButton button:hover {{
            background-color: {color['secondary']} !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
            transform: translateY(-2px) !important;
        }}
        
        /* Metric styling */
        [data-testid="stMetricValue"] {{
            font-size: 28px !important;
            font-weight: bold !important;
            color: {color['primary']} !important;
        }}
        
        /* Custom divider */
        hr {{
            margin: 2rem 0 !important;
            border: none !important;
            height: 2px !important;
            background: linear-gradient(90deg, transparent, {color['primary']}, transparent) !important;
        }}
        
        /* Expander styling */
        .streamlit-expanderHeader {{
            background-color: {color.get('light', '#f7fafc')} !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
        }}
        
        /* Success messages */
        .stSuccess {{
            background-color: #c6f6d5 !important;
            color: #22543d !important;
            border-radius: 8px !important;
            padding: 1rem !important;
        }}
    </style>
    """
    
    return base_style


def render_page_header(title, icon, page_name):
    """Render a styled page header"""
    # Apply theme switcher and get current theme
    current_theme = apply_theme_switcher()
    
    # Apply theme CSS
    st.markdown(get_theme_css(current_theme), unsafe_allow_html=True)
    
    # Apply page-specific styling
    st.markdown(get_page_style(page_name), unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="main-header">
            <h1>{icon} {title}</h1>
        </div>
    """, unsafe_allow_html=True)


def add_pwa_support():
    """Add PWA meta tags for mobile app-like experience"""
    import streamlit as st
    
    # Add minimal PWA configuration using Streamlit html
    st.html("""
        <script>
            // Set viewport and theme for mobile
            if (!document.querySelector('meta[name="theme-color"]')) {
                const meta = document.createElement('meta');
                meta.name = 'theme-color';
                meta.content = '#667eea';
                document.head.appendChild(meta);
            }
            
            // Register simple service worker for PWA capability
            if ('serviceWorker' in navigator && !navigator.serviceWorker.controller) {
                const swCode = `
                    self.addEventListener('fetch', (event) => {
                        event.respondWith(fetch(event.request));
                    });
                `;
                const blob = new Blob([swCode], { type: 'application/javascript' });
                const swUrl = URL.createObjectURL(blob);
                navigator.serviceWorker.register(swUrl).catch(() => {});
            }
        </script>
    """)


def render_bottom_navigation(current_page='tasks'):
    """Streamlit doesn't support truly fixed elements, so this is disabled.
    Navigation remains in sidebar."""
    pass  # Disabled - Streamlit cannot render fixed bottom nav that stays during scroll

