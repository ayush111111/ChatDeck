#!/bin/bash
# Azure PostgreSQL Free Tier Deployment Script

set -e

# Configuration
RESOURCE_GROUP="flashcardgen-rg"
LOCATION="eastus"
SERVER_NAME="flashcardgen-db-server"
DATABASE_NAME="flashcards"
ADMIN_USER="fcg_admin"
CONTAINER_NAME="flashcardgen-app"

echo "🚀 Deploying Flashcard Generator with Azure PostgreSQL Free Tier"

# Generate a secure password
ADMIN_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
echo "📝 Generated database password: $ADMIN_PASSWORD"
echo "⚠️  Save this password securely!"

# 1. Create Resource Group
echo "📁 Creating resource group..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION

# 2. Create PostgreSQL Flexible Server (FREE TIER!)
echo "🐘 Creating PostgreSQL server (Free Tier)..."
az postgres flexible-server create \
    --resource-group $RESOURCE_GROUP \
    --name $SERVER_NAME \
    --location $LOCATION \
    --admin-user $ADMIN_USER \
    --admin-password "$ADMIN_PASSWORD" \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --storage-size 32 \
    --version 15 \
    --public-access 0.0.0.0 \
    --yes

# 3. Create Database
echo "📊 Creating database..."
az postgres flexible-server db create \
    --resource-group $RESOURCE_GROUP \
    --server-name $SERVER_NAME \
    --database-name $DATABASE_NAME

# 4. Configure firewall (allow Azure services)
echo "🔒 Configuring firewall..."
az postgres flexible-server firewall-rule create \
    --resource-group $RESOURCE_GROUP \
    --name $SERVER_NAME \
    --rule-name "AllowAzureServices" \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0

# 5. Get connection string
DB_HOST="${SERVER_NAME}.postgres.database.azure.com"
CONNECTION_STRING="postgresql://${ADMIN_USER}:${ADMIN_PASSWORD}@${DB_HOST}:5432/${DATABASE_NAME}"

# 6. Deploy Container Instance
echo "🐳 Deploying container..."
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --image your-registry/flashcardgen:latest \
    --dns-name-label flashcardgen-app \
    --ports 8000 \
    --environment-variables \
        POSTGRES_ENABLED=true \
        POSTGRES_HOST="$DB_HOST" \
        POSTGRES_USER="$ADMIN_USER" \
        POSTGRES_PASSWORD="$ADMIN_PASSWORD" \
        POSTGRES_DATABASE="$DATABASE_NAME" \
        OPENROUTER_API_KEY="$OPENROUTER_API_KEY" \
    --restart-policy Always \
    --cpu 1 \
    --memory 1

echo "✅ Deployment complete!"
echo ""
echo "📋 Connection Details:"
echo "Database Host: $DB_HOST"
echo "Database: $DATABASE_NAME"
echo "Username: $ADMIN_USER"
echo "Password: $ADMIN_PASSWORD"
echo ""
echo "🌐 Application URL: http://flashcardgen-app.eastus.azurecontainer.io:8000"
echo ""
echo "💰 Cost: FREE for 12 months (Azure PostgreSQL Free Tier)"
echo "   - 1 vCore Burstable"
echo "   - 32GB storage"
echo "   - 750 hours/month free"
