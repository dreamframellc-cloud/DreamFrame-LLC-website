# 🚀 Deploy to Render - Step by Step

Your code is now on GitHub! Follow these steps to deploy to Render:

## ✅ Step 1: Go to Render Dashboard

1. **Visit:** https://dashboard.render.com
2. **Sign up** or **Log in** (free account works!)

## ✅ Step 2: Create New Web Service

1. Click **"New +"** button (top right)
2. Select **"Web Service"**
3. Click **"Connect GitHub"** (if not already connected)
4. **Authorize Render** to access your GitHub account
5. Select repository: **`dreamframellc-cloud/DreamFrame-LLC-website`**

## ✅ Step 3: Configure Your Service

### Basic Settings:
- **Name:** `dreamframe-website` (or any name)
- **Region:** Choose closest to you (e.g., `Oregon (US West)`)
- **Branch:** `main`
- **Root Directory:** (leave empty)

### Build & Start Commands:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn --config gunicorn.conf.py wsgi_simple:application
```

### Environment Variables:

Click **"Advanced"** → **"Add Environment Variable"** and add:

#### Required Variables:
```
FLASK_ENV=production
PYTHON_VERSION=3.11
DATABASE_URL=<your-neon-database-url>
SESSION_SECRET=<generate-a-random-secret-key>
```

#### API Keys (from your Vercel setup):
```
OPENAI_API_KEY=<your-openai-key>
STRIPE_SECRET_KEY=<your-stripe-key>
STRIPE_PUBLISHABLE_KEY=<your-stripe-publishable>
SENDGRID_API_KEY=<your-sendgrid-key>
TWILIO_ACCOUNT_SID=<your-twilio-sid>
TWILIO_AUTH_TOKEN=<your-twilio-token>
GOOGLE_APPLICATION_CREDENTIALS=<your-google-credentials-json>
```

#### Optional (if you have them):
```
ANTHROPIC_API_KEY=<your-anthropic-key>
CLAUDE_API_KEY=<your-claude-key>
```

### Instance Type:
- **Free:** Select **"Free"** tier (512 MB RAM)
- **Paid:** If you need more resources, select a paid tier

## ✅ Step 4: Create PostgreSQL Database (if needed)

1. Click **"New +"** → **"PostgreSQL"**
2. **Name:** `dreamframe-db`
3. **Database:** `dreamframe`
4. **User:** (auto-generated)
5. **Region:** Same as your web service
6. Click **"Create Database"**
7. Copy the **Internal Database URL** (for Render services)
8. Use this as your `DATABASE_URL` environment variable

## ✅ Step 5: Deploy!

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repo
   - Install dependencies
   - Start your app
3. Wait 5-10 minutes for first deployment

## ✅ Step 6: Get Your URL

After deployment, you'll get a URL like:
```
https://dreamframe-website.onrender.com
```

## ✅ Step 7: Connect Your Domain

1. In Render dashboard, go to your service
2. Click **"Settings"** → **"Custom Domains"**
3. Add: `dreamframellc.com`
4. Add: `www.dreamframellc.com`
5. Render will provide DNS records
6. Update your DNS at your domain registrar:
   - **Type:** CNAME
   - **Name:** `@` (or root domain)
   - **Value:** Render's provided hostname
   - **Type:** CNAME
   - **Name:** `www`
   - **Value:** Render's provided hostname

## 🎉 Done!

Your website will be live at `dreamframellc.com`!

---

## 📝 Quick Reference

**Your GitHub Repo:**
```
https://github.com/dreamframellc-cloud/DreamFrame-LLC-website
```

**Render Dashboard:**
```
https://dashboard.render.com
```

**Need Help?**
- Render Docs: https://render.com/docs
- Support: support@render.com

