#!/bin/bash
# GitHub Secrets Setup Script
# Run: bash scripts/setup_secrets.sh

set -e

REPO_OWNER="YOUR_GITHUB_USERNAME"
REPO_NAME="airdrop-farmer"
RESOURCE_GROUP="airdrop-farmer"
REGISTRY_NAME="airdropfarmeracr"

echo "=== GitHub Secrets Setup ==="
echo "You need to create these secrets in GitHub:"
echo "Settings > Secrets and variables > Actions > New repository secret"
echo ""

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $REGISTRY_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv)

# Get Azure credentials for GitHub Actions
AZURE_CREDENTIALS=$(az ad sp create-for-rbac --name "github-actions-farmer" --role contributor \
  --scopes /subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP \
  --sdk-auth)

echo "1. ACR_USERNAME = $ACR_USERNAME"
echo "2. ACR_PASSWORD = $ACR_PASSWORD"
echo "3. AZURE_CREDENTIALS = (JSON below)"
echo "$AZURE_CREDENTIALS"
echo ""
echo "4. WALLET_PASSWORD = (your wallet encryption password)"
echo "5. TELEGRAM_BOT_TOKEN = (from @BotFather)"
echo "6. TELEGRAM_CHAT_ID = (your chat ID from @userinfobot)"
echo ""
echo "=== GitHub CLI Commands (if you have gh installed) ==="
echo "gh secret set ACR_USERNAME --body \"$ACR_USERNAME\" --repo $REPO_OWNER/$REPO_NAME"
echo "gh secret set ACR_PASSWORD --body \"$ACR_PASSWORD\" --repo $REPO_OWNER/$REPO_NAME"
echo "gh secret set AZURE_CREDENTIALS --body '$AZURE_CREDENTIALS' --repo $REPO_OWNER/$REPO_NAME"
echo "gh secret set WALLET_PASSWORD --body \"YOUR_PASSWORD\" --repo $REPO_OWNER/$REPO_NAME"
echo "gh secret set TELEGRAM_BOT_TOKEN --body \"YOUR_BOT_TOKEN\" --repo $REPO_OWNER/$REPO_NAME"
echo "gh secret set TELEGRAM_CHAT_ID --body \"YOUR_CHAT_ID\" --repo $REPO_OWNER/$REPO_NAME"