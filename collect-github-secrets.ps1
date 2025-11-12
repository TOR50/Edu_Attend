# GitHub Secrets Collection Script
# Run this script to collect all values needed for GitHub Secrets

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  GitHub Secrets Collection for EduAttend  " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Azure CLI is installed
$azInstalled = Get-Command az -ErrorAction SilentlyContinue
if (-not $azInstalled) {
    Write-Host "❌ Azure CLI not found!" -ForegroundColor Red
    Write-Host "   Install with: winget install Microsoft.AzureCLI" -ForegroundColor Yellow
    Write-Host "   Then restart PowerShell and run this script again." -ForegroundColor Yellow
    Write-Host ""
    pause
    exit
}

Write-Host "✅ Azure CLI found" -ForegroundColor Green
Write-Host ""

# Check Azure login
Write-Host "Checking Azure login status..." -ForegroundColor Cyan
$azAccount = az account show 2>$null
if (-not $azAccount) {
    Write-Host "❌ Not logged into Azure!" -ForegroundColor Red
    Write-Host "   Run: az login" -ForegroundColor Yellow
    Write-Host "   Then: az account set --subscription 'a5297a7c-204c-433b-8259-6541e8f2b3d9'" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit
}

Write-Host "✅ Logged into Azure" -ForegroundColor Green
Write-Host ""

# Create output directory
$outputDir = ".\github-secrets-output"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

$outputFile = "$outputDir\secrets-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"

# Start collecting
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Collecting GitHub Secrets Values         " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Initialize output
"GitHub Secrets for EduAttend DevOps Pipeline" | Out-File $outputFile
"Generated: $(Get-Date)" | Out-File $outputFile -Append
"============================================`n" | Out-File $outputFile -Append

# 1. Azure Service Principal
Write-Host "1️⃣  Creating Azure Service Principal..." -ForegroundColor Yellow
Write-Host "   (This may take 30 seconds...)" -ForegroundColor Gray

try {
    $spOutput = az ad sp create-for-rbac `
        --name "eduattend-github-actions-$(Get-Date -Format 'yyyyMMdd')" `
        --role Contributor `
        --scopes /subscriptions/a5297a7c-204c-433b-8259-6541e8f2b3d9 `
        --sdk-auth 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Service Principal created!" -ForegroundColor Green
        
        "[1] AZURE_CREDENTIALS" | Out-File $outputFile -Append
        "Copy the entire JSON below:" | Out-File $outputFile -Append
        $spOutput | Out-File $outputFile -Append
        "`n" | Out-File $outputFile -Append
        
        # Parse JSON to get individual values
        $sp = $spOutput | ConvertFrom-Json
        
        "[2] AZURE_CLIENT_ID" | Out-File $outputFile -Append
        $sp.clientId | Out-File $outputFile -Append
        "`n" | Out-File $outputFile -Append
        
        "[3] AZURE_CLIENT_SECRET" | Out-File $outputFile -Append
        $sp.clientSecret | Out-File $outputFile -Append
        "`n" | Out-File $outputFile -Append
        
        "[4] AZURE_SUBSCRIPTION_ID" | Out-File $outputFile -Append
        "a5297a7c-204c-433b-8259-6541e8f2b3d9" | Out-File $outputFile -Append
        "`n" | Out-File $outputFile -Append
        
        "[5] AZURE_TENANT_ID" | Out-File $outputFile -Append
        $sp.tenantId | Out-File $outputFile -Append
        "`n" | Out-File $outputFile -Append
    } else {
        Write-Host "   ⚠️  Service Principal creation failed" -ForegroundColor Yellow
        Write-Host "   Manual creation needed" -ForegroundColor Yellow
        "[1-5] Azure credentials - CREATE MANUALLY" | Out-File $outputFile -Append
        "Run: az ad sp create-for-rbac --name 'eduattend-github' --role Contributor --scopes /subscriptions/a5297a7c-204c-433b-8259-6541e8f2b3d9 --sdk-auth" | Out-File $outputFile -Append
        "`n" | Out-File $outputFile -Append
    }
} catch {
    Write-Host "   ❌ Error creating service principal" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# 2. SSH Private Key
Write-Host "2️⃣  Reading SSH Private Key..." -ForegroundColor Yellow

$sshKeyPath = ".\.ssh\azure_vm_key"
if (Test-Path $sshKeyPath) {
    $sshKey = Get-Content $sshKeyPath -Raw
    Write-Host "   ✅ SSH Key found!" -ForegroundColor Green
    
    "[6] AZURE_VM_SSH_KEY" | Out-File $outputFile -Append
    "Copy the entire key including BEGIN and END lines:" | Out-File $outputFile -Append
    $sshKey | Out-File $outputFile -Append
    "`n" | Out-File $outputFile -Append
} else {
    Write-Host "   ❌ SSH Key not found at $sshKeyPath" -ForegroundColor Red
    "[6] AZURE_VM_SSH_KEY - NOT FOUND" | Out-File $outputFile -Append
    "Generate with: ssh-keygen -t rsa -b 4096 -f .ssh/azure_vm_key" | Out-File $outputFile -Append
    "`n" | Out-File $outputFile -Append
}

Write-Host ""

# 3. GitHub Username
Write-Host "3️⃣  GitHub Container Registry Username..." -ForegroundColor Yellow
Write-Host "   ✅ Using: TOR50" -ForegroundColor Green

"[7] GHCR_USERNAME" | Out-File $outputFile -Append
"TOR50" | Out-File $outputFile -Append
"`n" | Out-File $outputFile -Append

Write-Host ""

# 4. GitHub Token
Write-Host "4️⃣  GitHub Personal Access Token..." -ForegroundColor Yellow
Write-Host "   ⚠️  You need to create this manually!" -ForegroundColor Yellow
Write-Host "   Go to: https://github.com/settings/tokens" -ForegroundColor Cyan
Write-Host "   Generate new token (classic) with scopes:" -ForegroundColor Cyan
Write-Host "   - repo (full control)" -ForegroundColor Gray
Write-Host "   - read:packages" -ForegroundColor Gray
Write-Host "   - write:packages" -ForegroundColor Gray

"[8] GHCR_TOKEN" | Out-File $outputFile -Append
"CREATE MANUALLY at https://github.com/settings/tokens" | Out-File $outputFile -Append
"Scopes needed: repo, read:packages, write:packages" | Out-File $outputFile -Append
"Format: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" | Out-File $outputFile -Append
"`n" | Out-File $outputFile -Append

Write-Host ""

# 5. Database URL
Write-Host "5️⃣  Database URL (Neon PostgreSQL)..." -ForegroundColor Yellow
Write-Host "   ⚠️  Get this from your Neon dashboard!" -ForegroundColor Yellow
Write-Host "   Go to: https://neon.tech/" -ForegroundColor Cyan

"[9] DATABASE_URL" | Out-File $outputFile -Append
"Get from Neon dashboard: https://neon.tech/" | Out-File $outputFile -Append
"Format: postgresql://user:password@host.neon.tech/dbname?sslmode=require" | Out-File $outputFile -Append
"`n" | Out-File $outputFile -Append

Write-Host ""

# 6. Cloudinary URL
Write-Host "6️⃣  Cloudinary URL..." -ForegroundColor Yellow
Write-Host "   ⚠️  Get this from your Cloudinary dashboard!" -ForegroundColor Yellow
Write-Host "   Go to: https://cloudinary.com/console" -ForegroundColor Cyan

"[10] CLOUDINARY_URL" | Out-File $outputFile -Append
"Get from Cloudinary dashboard: https://cloudinary.com/console" | Out-File $outputFile -Append
"Format: cloudinary://api_key:api_secret@cloud_name" | Out-File $outputFile -Append
"`n" | Out-File $outputFile -Append

Write-Host ""

# 7. Django Secret Key
Write-Host "7️⃣  Generating Django Secret Key..." -ForegroundColor Yellow

try {
    $djangoKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Django Secret Key generated!" -ForegroundColor Green
        
        "[11] DJANGO_SECRET_KEY" | Out-File $outputFile -Append
        $djangoKey | Out-File $outputFile -Append
        "`n" | Out-File $outputFile -Append
    } else {
        Write-Host "   ⚠️  Python/Django not found, using fallback" -ForegroundColor Yellow
        $fallbackKey = "django-insecure-" + (-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 50 | ForEach-Object {[char]$_}))
        
        "[11] DJANGO_SECRET_KEY" | Out-File $outputFile -Append
        $fallbackKey | Out-File $outputFile -Append
        "`n" | Out-File $outputFile -Append
    }
} catch {
    Write-Host "   ⚠️  Error generating key, using fallback" -ForegroundColor Yellow
    $fallbackKey = "django-insecure-" + (-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 50 | ForEach-Object {[char]$_}))
    
    "[11] DJANGO_SECRET_KEY" | Out-File $outputFile -Append
    $fallbackKey | Out-File $outputFile -Append
    "`n" | Out-File $outputFile -Append
}

Write-Host ""

# Summary
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Summary                                   " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

"============================================" | Out-File $outputFile -Append
"SUMMARY" | Out-File $outputFile -Append
"============================================`n" | Out-File $outputFile -Append

Write-Host "✅ Secrets saved to: $outputFile" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Open the output file" -ForegroundColor White
Write-Host "   2. Create missing values (GitHub token, Database, Cloudinary)" -ForegroundColor White
Write-Host "   3. Go to: https://github.com/TOR50/TOR50-Capstone_KC739_CSE399/settings/secrets/actions" -ForegroundColor White
Write-Host "   4. Add each secret using values from the file" -ForegroundColor White
Write-Host "   5. Trigger the GitHub Actions workflow" -ForegroundColor White
Write-Host ""

"Next Steps:" | Out-File $outputFile -Append
"1. Complete manual values (GHCR_TOKEN, DATABASE_URL, CLOUDINARY_URL)" | Out-File $outputFile -Append
"2. Go to: https://github.com/TOR50/TOR50-Capstone_KC739_CSE399/settings/secrets/actions" | Out-File $outputFile -Append
"3. Add each secret (11 total)" | Out-File $outputFile -Append
"4. Trigger workflow: Actions → DevOps Demo Pipeline → Run workflow" | Out-File $outputFile -Append
"`n" | Out-File $outputFile -Append

Write-Host "⚠️  Manual Setup Required:" -ForegroundColor Yellow
Write-Host "   - GitHub Personal Access Token" -ForegroundColor Gray
Write-Host "   - Database URL (Neon)" -ForegroundColor Gray
Write-Host "   - Cloudinary URL" -ForegroundColor Gray
Write-Host ""

"Manual Setup Required:" | Out-File $outputFile -Append
"- GitHub PAT: https://github.com/settings/tokens" | Out-File $outputFile -Append
"- Database: https://neon.tech/" | Out-File $outputFile -Append
"- Cloudinary: https://cloudinary.com/console" | Out-File $outputFile -Append

Write-Host "Opening output file..." -ForegroundColor Cyan
Start-Sleep -Seconds 1
notepad $outputFile

Write-Host ""
Write-Host "✅ Done! Review the opened file for all secret values." -ForegroundColor Green
Write-Host ""
pause
