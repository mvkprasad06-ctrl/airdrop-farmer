#!/bin/bash
# Azure deployment script
# Run: bash scripts/deploy.sh

set -e

RESOURCE_GROUP="airdrop-farmer"
LOCATION="eastus"
REGISTRY_NAME="airdropfarmeracr"
CONTAINER_APP="airdrop-farmer"

echo "=== Azure Farmer Deployment ==="

# 1. Create resource group
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# 2. Create Container Registry
echo "Creating Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --sku Basic --admin-enabled true

# 3. Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $REGISTRY_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv)

# 4. Build and push image
echo "Building and pushing Docker image..."
az acr build --registry $REGISTRY_NAME --image $CONTAINER_APP:latest .

# 5. Deploy infrastructure (Bicep)
echo "Deploying infrastructure..."
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file infra/main.bicep \
  --parameters \
    registryName=$REGISTRY_NAME \
    containerAppName=$CONTAINER_APP \
    containerImage="${REGISTRY_NAME}.azurecr.io/${CONTAINER_APP}:latest" \
    walletPassword="$WALLET_PASSWORD" \
    telegramBotToken="$TELEGRAM_BOT_TOKEN" \
    telegramChatId="$TELEGRAM_CHAT_ID"

# 6. Get deployment outputs
CONTAINER_APP_URL=$(az deployment group show --resource-group $RESOURCE_GROUP --name main --query properties.outputs.containerAppUrl.value -o tsv)
echo "Container App URL: https://$CONTAINER_APP_URL"

echo "=== Deployment Complete ==="
echo "Next steps:"
echo "1. Add GitHub Secrets (see scripts/setup_secrets.sh)"
echo "2. Push to GitHub to trigger build"
echo "3. Check Telegram for alerts"