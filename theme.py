"""
Theme and styling configuration for Home Hub
"""

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
    'purchases': {
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
    import streamlit as st
    
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

