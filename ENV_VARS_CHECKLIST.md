# Environment Variables Checklist for Render

Copy these from your Vercel dashboard or local `.env` file:

## 🔐 Required Variables

### Database
```
DATABASE_URL=<your-postgresql-connection-string>
```
**Options:**
- Use Render's PostgreSQL (create in dashboard)
- Use Neon database (recommended - free tier available)
- Format: `postgresql://user:password@host:port/database`

### Flask Configuration
```
FLASK_ENV=production
SESSION_SECRET=<generate-random-string>
```
**Generate SESSION_SECRET:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## 🔑 API Keys

### OpenAI
```
OPENAI_API_KEY=sk-...
```

### Stripe
```
STRIPE_SECRET_KEY=sk_live_... or sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_live_... or pk_test_...
```

### SendGrid (Email)
```
SENDGRID_API_KEY=SG....
```

### Twilio (SMS)
```
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
```

### Google Cloud (Video Generation)
```
GOOGLE_APPLICATION_CREDENTIALS={"type":"service_account",...}
```
**Note:** This should be a single-line JSON string, not a file path.

## 📋 Optional Variables

### Anthropic/Claude (if used)
```
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_API_KEY=sk-ant-...
```

### Server Configuration
```
SERVER_NAME=dreamframellc.com
PORT=8000  # Render sets this automatically
```

## 🚀 How to Add in Render

1. Go to your service in Render dashboard
2. Click **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Paste each key-value pair
5. Click **"Save Changes"**
6. Service will automatically redeploy

## ✅ Quick Copy-Paste Format

For easy copying, here's the format:

```
DATABASE_URL=
FLASK_ENV=production
SESSION_SECRET=
OPENAI_API_KEY=
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
SENDGRID_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
GOOGLE_APPLICATION_CREDENTIALS=
```

Fill in the values and add them one by one in Render!

