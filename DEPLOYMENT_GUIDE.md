# 🚀 Streamlit Cloud Deployment Guide

## Step-by-Step Deployment

### 1. Create GitHub Repository

```bash
cd HomeHub
git init
git add .
git commit -m "Initial commit - Home Hub V1"
```

Create a new repository on GitHub (https://github.com/new):
- Name: `homehub`
- Make it **Private** (recommended for security)

```bash
git remote add origin https://github.com/YOUR_USERNAME/homehub.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click **"New app"**
3. Connect your GitHub account
4. Select your repository: `YOUR_USERNAME/homehub`
5. Branch: `main`
6. Main file path: `Login.py`
7. Click **"Deploy!"**

### 3. Wait for Deployment

- Takes 2-5 minutes
- You'll get a URL like: `https://YOUR_APP_NAME.streamlit.app`

### 4. Test Your Deployed App

1. Open the URL in your browser
2. Login with: `sanjai` / `7305559689`
3. Check "Remember me for 30 days"
4. Test all pages (Home, Tasks, Purchases, Groceries, Archive)
5. Try on mobile phone

### 5. Share with Pradhiksha

Send her:
- **URL**: `https://YOUR_APP_NAME.streamlit.app`
- **Username**: `pradhiksha`
- **Password**: `603103`
- **Mobile guide**: See `PWA_INSTALL_GUIDE.md`

## ⚠️ Important Notes

### Database (SQLite)

- ✅ Works immediately
- ⚠️ **Data may be lost** if Streamlit Cloud restarts the app
- **Backup strategy**: Periodically export important data
- **Future upgrade**: Move to PostgreSQL (Supabase) for reliability

### Security

- App is **PUBLIC** if anyone has the URL
- Password protection is your only security
- For production use, consider:
  - Making GitHub repo private
  - Using Streamlit secrets for passwords
  - Adding IP restrictions (paid feature)

### Updating the App

After making changes:
```bash
git add .
git commit -m "Your update message"
git push
```

Streamlit Cloud auto-deploys within 1-2 minutes!

## 📱 Mobile Usage

After deployment, both of you can:
1. Open the URL on your phones
2. Add to home screen (see PWA_INSTALL_GUIDE.md)
3. Use like a native app!

## 🆘 Troubleshooting

**App won't start:**
- Check logs in Streamlit Cloud dashboard
- Verify `requirements.txt` is correct

**Data disappeared:**
- Expected with SQLite on cloud
- Data resets when app restarts
- Consider upgrading to PostgreSQL

**Login not remembering:**
- Clear browser cache and try again
- Make sure cookies are enabled

**Can't access from outside home:**
- Should work anywhere with internet
- Check if URL is correct

## 🔄 Future Upgrades

When ready for production database:
1. Create free Supabase account
2. Set up PostgreSQL database
3. Update `database.py` to use PostgreSQL
4. Add connection string to Streamlit secrets

Need help? Let me know!
