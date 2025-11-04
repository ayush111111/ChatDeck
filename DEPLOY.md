# Railway Deployment Guide

## 🚀 Quick Deploy (5 minutes)

### 1. Install Railway CLI
```powershell
npm install -g @railway/cli
```

### 2. Login to Railway
```powershell
railway login
```
This will open your browser to authenticate.

### 3. Initialize Project
```powershell
# From your project directory
railway init
```
Choose "Create a new project" and give it a name like "flashcard-generator"

### 4. Add PostgreSQL Database
After running `railway init`, you'll need to add a database through the Railway dashboard:

**Option A: Via Dashboard**
1. Run `railway open` to open your project dashboard
2. Click "+ New" → "Database" → "Add PostgreSQL"
3. Railway will automatically set all database environment variables

**Option B: Via CLI (if available)**
```powershell
railway add
```
Then select "PostgreSQL" from the menu.

### 5. Set Environment Variables
```powershell
railway variables set OPENROUTER_API_KEY=your-key-here
railway variables set POSTGRES_ENABLED=true
```

### 6. Deploy!
```powershell
railway up
```
This builds your Docker image and deploys it.

### 7. Get Your URL
```powershell
railway domain
```
This generates a public URL like `https://your-app.up.railway.app`

---

## 📋 Environment Variables Railway Will Set Automatically

Railway automatically provides these when you add PostgreSQL:
- `DATABASE_URL` - Full PostgreSQL connection string
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` - Individual components

Your app will automatically detect and use them!

---

## 🔧 Update Your Chrome Extension

After deployment, update the API URL in your extension:

1. Open `flash-card-extension/content_script.js`
2. Find lines with `http://localhost:8000`
3. Replace with your Railway URL: `https://your-app.up.railway.app`
4. Reload the extension in Chrome

---

## 💰 Free Tier Limits

**Railway Free Plan:**
- ✅ 500 hours/month execution time (~20 days)
- ✅ 1GB RAM
- ✅ 1GB disk
- ✅ PostgreSQL database included
- ✅ Custom domain support

**Upgrade triggers:**
- More than 500 hours/month
- Need more than 1GB RAM
- Need multiple services

---

## 🐛 Troubleshooting

### Check logs
```powershell
railway logs
```

### Check if database is connected
```powershell
railway run python -c "from fcg.services.database import db_service; db_service.init_database(); print('✅ Database connected!')"
```

### Redeploy
```powershell
railway up --detach
```

---

## 🔄 Future Updates

Every time you want to deploy changes:
```powershell
git add .
git commit -m "Your changes"
railway up
```

Or enable automatic deployments from GitHub in Railway dashboard!
