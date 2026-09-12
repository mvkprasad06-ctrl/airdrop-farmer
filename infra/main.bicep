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

@description('Container image')
param containerImage string = ''

// Container Registry (existing)
resource acr 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' existing = {
  name: registryName
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

// Container App
resource ca 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppName
  location: location
  properties: {
    managedEnvironmentId: caEnv.id
    configuration: {
      registries: [
        {
          server: acr.properties.loginServer
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
            cpu: 1
            memory: '2Gi'
          }
          env: [
            {
              name: 'WALLET_PASSWORD'
              value: 'PLACEHOLDER'
            }
            {
              name: 'TELEGRAM_BOT_TOKEN'
              value: 'PLACEHOLDER'
            }
            {
              name: 'TELEGRAM_CHAT_ID'
              value: 'PLACEHOLDER'
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

// Outputs
output containerAppUrl string = ca.properties.latestRevisionFqdn
output registryLoginServer string = acr.properties.loginServer