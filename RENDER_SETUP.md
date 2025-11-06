# Render Free Hosting Setup Guide

## 🎯 Why Render is Perfect for You

✅ **100% Free** (forever with limitations)  
✅ **Free PostgreSQL** included (no database issues!)  
✅ **Custom Domain** support (dreamframellc.com)  
✅ **Auto-deploy** from GitHub  
✅ **Perfect Flask support**  

**Only limitation:** Free tier spins down after 15 min inactivity (cold start ~30 sec)

## 🚀 Step-by-Step Setup

### Step 1: Create Render Account
1. Go to: **https://render.com**
2. **Sign up** with GitHub (recommended)
3. Verify your email

### Step 2: Deploy Web Service
1. In Render dashboard, click **"New +"**
2. Select **"Web Service"**
3. **Connect your GitHub account** (if not already)
4. **Select your repository:** `DreamFrame-LLC-website`
5. Render will auto-detect Flask!

### Step 3: Configure Web Service
- **Name:** `dreamframe-llc`
- **Region:** Choose closest (US East recommended)
- **Branch:** `main` or `master`
- **Root Directory:** Leave blank (or `.` if needed)
- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn --config gunicorn.conf.py wsgi_simple:application`
- **Plan:** **Free** (select this!)

Click **"Create Web Service"**

### Step 4: Add PostgreSQL Database
1. In Render dashboard, click **"New +"**
2. Select **"PostgreSQL"**
3. **Name:** `dreamframe-db`
4. **Database:** `dreamframe`
5. **User:** `dreamframe`
6. **Plan:** **Free**
7. Click **"Create Database"**

**Important:** Render automatically creates `DATABASE_URL` environment variable - you don't need to add it manually!

### Step 5: Link Database to Web Service
1. Go to your **web service** settings
2. Go to **"Environment"** tab
3. Scroll down to **"Add Database"**
4. Select your `dreamframe-db` database
5. Render automatically adds `DATABASE_URL`!

### Step 6: Add Environment Variables
1. In your **web service**, go to **"Environment"** tab
2. Click **"Add Environment Variable"**
3. Add all variables from Vercel (one by one):

**Essential:**
- `SESSION_SECRET` (you have this)
- `OPENAI_API_KEY`
- `STRIPE_LIVE_SECRET_KEY`
- `STRIPE_PK_LIVE`
- `GOOGLE_APPLICATION_CREDENTIALS` (your base64 encoded credentials)
- `SENDGRID_API_KEY`
- `GMAIL_APP_PASSWORD`
- `GMAIL_USER`

**Note:** `DATABASE_URL` is automatically added when you link the database!

### Step 7: Add Custom Domain
1. In your web service, go to **"Settings"**
2. Scroll to **"Custom Domains"**
3. Click **"Add Custom Domain"**
4. Enter: `dreamframellc.com`
5. Render provides DNS instructions
6. Add DNS records in your domain registrar
7. Render handles SSL automatically!

### Step 8: Deploy
- Render auto-deploys when you push to GitHub
- Or click **"Manual Deploy"** → **"Deploy latest commit"**

## ✅ After Deployment

Your site will be live at:
- **Render URL:** `https://dreamframe-llc.onrender.com` (temporary)
- **Custom Domain:** `https://dreamframellc.com` (after DNS setup)

## 🔄 Keep Free Tier Active

To prevent cold starts (15 min inactivity timeout):

**Option 1: UptimeRobot (Free)**
1. Sign up: https://uptimerobot.com
2. Add monitor for your site
3. Set interval to 5 minutes
4. Keeps site warm (free!)

**Option 2: Cron Job**
- Use a free cron service to ping your site

## 📝 Quick Reference

**Render Dashboard:** https://dashboard.render.com  
**Vercel Env Vars (to copy):** https://vercel.com/jeremy-prices-projects-744464c3/dreamframe-llc/settings/environment-variables

## 🎉 That's It!

Render is free, includes PostgreSQL, and works perfectly for Flask apps!

---

**Need help?** I can guide you through any step!

