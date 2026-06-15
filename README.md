# Home Hub 🏠

A shared home management application for tracking tasks, purchases, and groceries.

## Features

- 📋 **Tasks Management** - Track and assign household tasks
- 🛒 **Purchase Tracking** - Manage online shopping with 6-stage workflow
- 🥗 **Grocery Lists** - Simple grocery management
- 📦 **Archive** - View completed items
- 🔐 **Secure Login** - User authentication with remember me
- 📱 **PWA Support** - Install as mobile app
- 🎨 **Color-coded Pages** - Easy visual navigation

## Quick Start

1. Login with your credentials
2. Navigate using the sidebar
3. Add tasks, purchases, or groceries
4. Track progress and mark items complete

## Mobile Installation

On your phone:
- **iPhone**: Safari → Share → Add to Home Screen
- **Android**: Chrome → Menu (⋮) → Install app

## Technology

- **Framework**: Streamlit
- **Database**: SQLite
- **Authentication**: Session-based with browser storage
- **PWA**: Progressive Web App for mobile

## For Developers

### Local Setup

```bash
pip install -r requirements.txt
streamlit run Login.py
```

### Password Management

To change passwords, edit `auth.py` and modify the `USERS` dictionary.

---

Built with ❤️ for Sanjai & Pradhiksha
