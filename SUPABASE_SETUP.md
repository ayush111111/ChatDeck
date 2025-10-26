# Supabase Setup Guide

## 🚀 Quick Setup (5 minutes)

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up/login with GitHub
4. Click "New Project"
5. Choose organization and set:
   - **Name**: `flashcard-generator`
   - **Database Password**: `[save this password!]`
   - **Region**: Choose closest to your users
6. Wait 2-3 minutes for setup

### 2. Get Connection Details
After project is created, go to **Settings > Database**:

```bash
# Copy these values to your environment variables
POSTGRES_HOST=db.abc123.supabase.co
POSTGRES_USER=postgres
POSTGRES_PASSWORD=[your password from step 1]
POSTGRES_DB=postgres
```

### 3. Environment Variables

#### For Local Development (.env file):
```bash
# Supabase PostgreSQL (Free tier: 500MB database)
POSTGRES_HOST=db.abc123.supabase.co
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password-here
POSTGRES_DB=postgres

# Your existing variables
OPENROUTER_API_KEY=your-key
OPENROUTER_URL=https://openrouter.ai/api/v1/chat/completions
OPENROUTER_MODEL=qwen/qwen3-4b:free
```

#### For Azure Container Instances:
```bash
az container create \
  --name flashcardgen \
  --environment-variables \
    POSTGRES_HOST=db.abc123.supabase.co \
    POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=your-password \
    POSTGRES_DB=postgres \
    OPENROUTER_API_KEY=your-key
```

### 4. Test Connection
```bash
# Test locally
python -c "
from fcg.services.database import db_service
print('Database URL:', db_service.database_url)
db_service.init_database()
print('✅ Supabase connection successful!')
"
```

## 📊 Supabase Free Tier Limits
- ✅ **Database**: 500MB PostgreSQL
- ✅ **API requests**: 50,000/month
- ✅ **Storage**: 1GB files
- ✅ **Bandwidth**: 2GB
- ✅ **Auth users**: 50,000

Perfect for your flashcard app!

## 🔧 Optional: Supabase Dashboard
- **URL**: https://app.supabase.com/project/abc123
- **SQL Editor**: Write custom queries
- **Table Editor**: Visual database management
- **API Docs**: Auto-generated from your schema

## 🚀 Migration from SQLite
Your existing code will work automatically! The database service detects PostgreSQL and creates tables on first run.

No code changes needed! 🎉
