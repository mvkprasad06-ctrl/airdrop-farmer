@description('Location for all resources')
param location string = resourceGroup().location

@description('Container App name')
param containerAppName string = 'airdrop-farmer'

@description('Container Registry name')
param registryName string = 'airdropfarmeracr'

@description('Log Analytics Workspace name')
param logAnalyticsWorkspaceName string = 'airdrop-farmer-logs'

@description('Container App Environment name')
param containerAppEnvName string = 'airdrop-farmer-env'

@description('Key Vault name')
param keyVaultName string = 'airdrop-farmer-kv'

@description('Container image')
param containerImage string = ''

@description('Wallet password (stored in Key Vault)')
param walletPassword string = ''

@description('Telegram bot token (stored in Key Vault)')
param telegramBotToken string = ''

@description('Telegram chat ID (stored in Key Vault)')
param telegramChatId string = ''

// Container Registry
resource acr 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: registryName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

// Log Analytics Workspace
resource law 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsWorkspaceName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Container App Environment
resource caEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: containerAppEnvName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: law.properties.customerId
        sharedKey: listKeys(law.id, law.apiVersion).primarySharedKey
      }
    }
  }
}

// Key Vault
resource kv 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    accessPolicies: []
    enableRbacAuthorization: true
  }
}

// Key Vault secrets
resource kvSecretWallet 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: kv
  name: 'wallet-password'
  properties: {
    value: walletPassword
  }
}

resource kvSecretTelegramToken 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: kv
  name: 'telegram-bot-token'
  properties: {
    value: telegramBotToken
  }
}

resource kvSecretTelegramChat 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: kv
  name: 'telegram-chat-id'
  properties: {
    value: telegramChatId
  }
}

// Container App
resource ca 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppName
  location: location
  properties: {
    managedEnvironmentId: caEnv.id
    configuration: {
      secrets: [
        {
          name: 'wallet-password'
          keyVaultUrl: kvSecretWallet.properties.vaultUri
        }
        {
          name: 'telegram-bot-token'
          keyVaultUrl: kvSecretTelegramToken.properties.vaultUri
        }
        {
          name: 'telegram-chat-id'
          keyVaultUrl: kvSecretTelegramChat.properties.vaultUri
        }
      ]
      registries: [
        {
          server: '${registryName}.azurecr.io'
          username: registryName
          passwordSecretRef: 'acr-password'
        }
      ]
    }
    template: {
      containers: [
        {
          name: containerAppName
          image: containerImage
          resources: {
            cpu: 1.0
            memory: '2Gi'
          }
          env: [
            {
              name: 'WALLET_PASSWORD'
              secretRef: 'wallet-password'
            }
            {
              name: 'TELEGRAM_BOT_TOKEN'
              secretRef: 'telegram-bot-token'
            }
            {
              name: 'TELEGRAM_CHAT_ID'
              secretRef: 'telegram-chat-id'
            }
            {
              name: 'CHROME_HEADLESS'
              value: 'true'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
        rules: []
      }
    }
  }
}

// ACR password secret for Container App
resource acrPassword 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: kv
  name: 'acr-password'
  properties: {
    value: listCredentials(acr.id, acr.apiVersion).passwords[0].value
  }
}

// Outputs
output containerAppUrl string = ca.properties.latestRevisionFqdn
output registryLoginServer string = acr.properties.loginServer
output keyVaultUri string = kv.properties.vaultUri