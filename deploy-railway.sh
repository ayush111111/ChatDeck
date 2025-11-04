#!/bin/bash
# Railway.app Deployment (FREE PostgreSQL + App Hosting)

echo "🚀 Railway.app Deployment Guide (FREE Forever)"
echo ""
echo "Railway provides both PostgreSQL and app hosting for free!"
echo ""

# Create Railway configuration
cat > railway.toml << 'EOF'
[build]
builder = "dockerfile"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "always"

[[services]]
name = "web"
source = "."

[services.web.variables]
PORT = "8000"
POSTGRES_ENABLED = "true"

[[services]]
name = "database"
source = "postgres"

[services.database.variables]
POSTGRES_DB = "flashcards"
POSTGRES_USER = "postgres"
EOF

# Create Dockerfile optimized for Railway
cat > Dockerfile.railway << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Expose port (Railway sets PORT env var)
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Railway provides DATABASE_URL automatically
ENV POSTGRES_ENABLED=true

# Run the application
CMD uvicorn fcg.main:app --host 0.0.0.0 --port $PORT
EOF

echo "📋 Setup Instructions:"
echo ""
echo "1. Install Railway CLI:"
echo "   npm install -g @railway/cli"
echo ""
echo "2. Login to Railway:"
echo "   railway login"
echo ""
echo "3. Create new project:"
echo "   railway new"
echo ""
echo "4. Add PostgreSQL database:"
echo "   railway add postgresql"
echo ""
echo "5. Deploy your app:"
echo "   railway up"
echo ""
echo "6. Set environment variables:"
echo "   railway variables set OPENROUTER_API_KEY=your-key-here"
echo ""
echo "📁 Files created:"
echo "   - railway.toml (Railway configuration)"
echo "   - Dockerfile.railway (Optimized Dockerfile)"
echo ""
echo "💰 Cost: FREE Forever!"
echo "   - PostgreSQL: 512MB RAM, 1GB storage"
echo "   - App hosting: 512MB RAM, 1GB disk"
echo "   - Custom domain included"
echo ""
echo "🎯 Advantages:"
echo "   ✅ Zero configuration"
echo "   ✅ Automatic HTTPS"
echo "   ✅ Git-based deployments"
echo "   ✅ Built-in PostgreSQL"
echo "   ✅ No credit card required"

# Make scripts executable
chmod +x deploy-azure-free.sh deploy-supabase.sh

echo ""
echo "🚀 Next Steps:"
echo "1. Choose your preferred option above"
echo "2. Or use Azure PostgreSQL free tier: ./deploy-azure-free.sh"
echo "3. Or use Supabase: ./deploy-supabase.sh"
