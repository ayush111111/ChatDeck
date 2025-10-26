#!/bin/bash
# Supabase PostgreSQL Deployment (FREE Forever)

set -e

echo "🚀 Setting up Flashcard Generator with Supabase (FREE Forever)"

echo "📋 Manual Setup Required:"
echo ""
echo "1. Go to https://supabase.com"
echo "2. Create free account"
echo "3. Create new project"
echo "4. Go to Settings > Database"
echo "5. Copy connection string"
echo ""
echo "Example connection string:"
echo "postgresql://postgres.PROJECT_ID:PASSWORD@aws-0-region.pooler.supabase.com:5432/postgres"
echo ""

# Configuration
RESOURCE_GROUP="flashcardgen-rg"
LOCATION="eastus"
CONTAINER_NAME="flashcardgen-app"

read -p "Enter your Supabase connection string: " SUPABASE_URL
read -p "Enter your OpenRouter API key: " OPENROUTER_API_KEY

# Extract components from Supabase URL
DB_HOST=$(echo $SUPABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_USER=$(echo $SUPABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASSWORD=$(echo $SUPABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_NAME=$(echo $SUPABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
DB_PORT=5432

echo "🔍 Parsed connection details:"
echo "Host: $DB_HOST"
echo "User: $DB_USER"
echo "Database: $DB_NAME"

# Create resource group
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION

# Deploy container
echo "🐳 Deploying container with Supabase..."
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --image your-registry/flashcardgen:latest \
    --dns-name-label flashcardgen-supabase \
    --ports 8000 \
    --environment-variables \
        POSTGRES_ENABLED=true \
        POSTGRES_HOST="$DB_HOST" \
        POSTGRES_USER="$DB_USER" \
        POSTGRES_PASSWORD="$DB_PASSWORD" \
        POSTGRES_DATABASE="$DB_NAME" \
        POSTGRES_PORT="$DB_PORT" \
        OPENROUTER_API_KEY="$OPENROUTER_API_KEY" \
    --restart-policy Always \
    --cpu 1 \
    --memory 1

echo "✅ Deployment complete!"
echo ""
echo "🌐 Application URL: http://flashcardgen-supabase.eastus.azurecontainer.io:8000"
echo "💰 Cost: FREE Forever!"
echo "   - Supabase: 2GB database, 500MB file storage"
echo "   - Azure Container: ~$30/month (1 vCore, 1GB RAM)"
