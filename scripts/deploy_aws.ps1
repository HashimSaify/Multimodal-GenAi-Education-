# AWS EKS Deployment Script for Multimodal GenAi Education
# Run this script as Administrator in PowerShell

$Region = "eu-north-1"
$ClusterName = "edugen-cluster"

# 1. Install/Check Dependencies
Write-Host "--- Checking Dependencies ---" -ForegroundColor Cyan

function Install-Tool {
    param($Name, $Url, $Dest)
    if (!(Get-Command $Name -ErrorAction SilentlyContinue)) {
        Write-Host "Installing $Name..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $Url -OutFile $Dest
        # Installation logic would go here, but for simplicity we advise the user
        Write-Host "$Name not found. Please install it from $Url and restart PowerShell." -ForegroundColor Red
        exit
    }
}

# In a real environment, we'd use Choco or direct installs. 
# For this project, we check and warn.
if (!(Get-Command aws -ErrorAction SilentlyContinue)) { Write-Host "Please install AWS CLI first." -ForegroundColor Red; exit }
if (!(Get-Command docker -ErrorAction SilentlyContinue)) { Write-Host "Please ensure Docker Desktop is running." -ForegroundColor Red; exit }

# 2. Get API Keys from User
Write-Host "`n--- API Key Configuration ---" -ForegroundColor Cyan
$GeminiKey = Read-Host "Enter your Gemini API Key"
$ImageKey = Read-Host "Enter your Image API Key"

$GeminiB64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($GeminiKey))
$ImageB64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($ImageKey))

# Update secrets.yaml
$SecretFile = "k8s/secrets.yaml"
$SecretContent = Get-Content $SecretFile
$SecretContent = $SecretContent -replace "GEMINI_API_KEY: .*", "GEMINI_API_KEY: $GeminiB64"
$SecretContent = $SecretContent -replace "IMAGE_API_KEY: .*", "IMAGE_API_KEY: $ImageB64"
$SecretContent | Set-Content $SecretFile

# 3. AWS Infrastructure Setup
Write-Host "`n--- AWS ECR Setup ---" -ForegroundColor Cyan
$AccountId = (aws sts get-caller-identity --query Account --output text)
$BackendRepo = "$AccountId.dkr.ecr.$Region.amazonaws.com/edugen-backend"
$FrontendRepo = "$AccountId.dkr.ecr.$Region.amazonaws.com/edugen-frontend"

aws ecr create-repository --repository-name edugen-backend --region $Region 2>$null
aws ecr create-repository --repository-name edugen-frontend --region $Region 2>$null

aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin "$AccountId.dkr.ecr.$Region.amazonaws.com"

# 4. Build and Push Images
Write-Host "`n--- Building and Pushing Images ---" -ForegroundColor Cyan
docker build -t $BackendRepo:latest -f Dockerfile.backend .
docker push $BackendRepo:latest

docker build -t $FrontendRepo:latest -f Dockerfile.frontend .
docker push $FrontendRepo:latest

# 5. Update Manifests with Account ID
Write-Host "`n--- Updating K8s Manifests ---" -ForegroundColor Cyan
(Get-Content k8s/backend-deployment.yaml) -replace "AWS_ACCOUNT_ID", $AccountId | Set-Content k8s/backend-deployment.yaml
(Get-Content k8s/frontend-deployment.yaml) -replace "AWS_ACCOUNT_ID", $AccountId | Set-Content k8s/frontend-deployment.yaml

# 6. Create EKS Cluster
Write-Host "`n--- Creating EKS Cluster (This takes ~20 mins) ---" -ForegroundColor Cyan
Write-Host "Command: eksctl create cluster --name $ClusterName --region $Region --nodegroup-name standard-nodes --nodes 2 --nodes-min 1 --nodes-max 3 --managed" -ForegroundColor Gray
# We recommend the user run this manually as it is a long-running task
# eksctl create cluster --name $ClusterName --region $Region --nodegroup-name standard-nodes --nodes 2 --nodes-min 1 --nodes-max 3 --managed

Write-Host "`nSteps to complete:" -ForegroundColor Yellow
Write-Host "1. Install eksctl if you haven't: 'winget install weaveworks.eksctl'"
Write-Host "2. Run the eksctl command shown above."
Write-Host "3. Finally, run: 'kubectl apply -f k8s/'"
Write-Host "4. Access your app via: 'kubectl get svc frontend-service'"
