# 🔐 GitHub Secrets Setup Guide

Complete guide to configure GitHub Secrets for automated CI/CD pipeline.

---

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ Azure CLI installed
- ✅ Logged into Azure (`az login`)
- ✅ GitHub repository access
- ✅ Repository admin permissions

---

## 🚀 Quick Setup (Step-by-Step)

### Step 1: Install Azure CLI (If Not Installed)

**Windows PowerShell:**
```powershell
# Install Azure CLI
winget install Microsoft.AzureCLI

# Close and reopen PowerShell, then login
az login

# Set subscription
az account set --subscription "a5297a7c-204c-433b-8259-6541e8f2b3d9"

# Verify
az account show
```

---

### Step 2: Create Azure Service Principal

**Run this command:**
```powershell
az ad sp create-for-rbac --name "eduattend-github-actions" --role Contributor --scopes /subscriptions/a5297a7c-204c-433b-8259-6541e8f2b3d9 --sdk-auth
```

**Expected output:**
```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "subscriptionId": "a5297a7c-204c-433b-8259-6541e8f2b3d9",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

**⚠️ SAVE THIS ENTIRE OUTPUT!** You'll need it for GitHub Secrets.

---

### Step 3: Get GitHub Personal Access Token

1. Go to: **https://github.com/settings/tokens**
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. **Token name:** `eduattend-devops-deployment`
4. **Expiration:** 90 days (or custom)
5. **Select scopes:**
   - ✅ `repo` (Full control of private repositories)
   - ✅ `read:packages` (Download packages from GitHub Package Registry)
   - ✅ `write:packages` (Upload packages to GitHub Package Registry)
6. Click **"Generate token"**
7. **⚠️ COPY THE TOKEN IMMEDIATELY** (you can't see it again!)

**Token format:** `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

### Step 4: Get SSH Private Key

**Run this command:**
```powershell
Get-Content ".ssh\azure_vm_key"
```

**Copy the entire output**, including:
```
-----BEGIN OPENSSH PRIVATE KEY-----
...entire key content...
-----END OPENSSH PRIVATE KEY-----
```

---

### Step 5: Generate Django Secret Key

**Run this command:**
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Copy the output** (random string like: `django-insecure-xxxxx...`)

---

### Step 6: Get Database & Cloudinary URLs

**You need these from your existing setup:**

1. **DATABASE_URL** (Neon PostgreSQL)
   - Go to: https://neon.tech/
   - Login → Your Project → Connection String
   - Format: `postgresql://user:password@host/database`

2. **CLOUDINARY_URL**
   - Go to: https://cloudinary.com/console
   - Login → Dashboard → API Environment variable
   - Format: `cloudinary://api_key:api_secret@cloud_name`

---

## 🔐 Add Secrets to GitHub

### Navigate to Repository Secrets

1. Go to: **https://github.com/TOR50/TOR50-Capstone_KC739_CSE399/settings/secrets/actions**
2. Or: Your repo → **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** for each secret below

---

### Required Secrets (12 Total)

| # | Secret Name | Value | Source |
|---|-------------|-------|--------|
| 1 | `AZURE_CREDENTIALS` | **Entire JSON output** from Step 2 | Azure Service Principal |
| 2 | `AZURE_CLIENT_ID` | `clientId` from JSON | Azure Service Principal |
| 3 | `AZURE_CLIENT_SECRET` | `clientSecret` from JSON | Azure Service Principal |
| 4 | `AZURE_SUBSCRIPTION_ID` | `a5297a7c-204c-433b-8259-6541e8f2b3d9` | Known |
| 5 | `AZURE_TENANT_ID` | `tenantId` from JSON | Azure Service Principal |
| 6 | `AZURE_VM_SSH_KEY` | **Entire private key** from Step 4 | `.ssh/azure_vm_key` |
| 7 | `GHCR_USERNAME` | `TOR50` | Your GitHub username |
| 8 | `GHCR_TOKEN` | Token from Step 3 | GitHub PAT |
| 9 | `DATABASE_URL` | Your Neon PostgreSQL URL | Neon Dashboard |
| 10 | `CLOUDINARY_URL` | Your Cloudinary URL | Cloudinary Dashboard |
| 11 | `DJANGO_SECRET_KEY` | Generated key from Step 5 | Django command |
| 12 | `SSH_HOST` | Will get after Terraform | Terraform output |

**Note:** `SSH_HOST` will be added after first Terraform deployment.

---

## 📝 Detailed Instructions for Each Secret

### 1. AZURE_CREDENTIALS

**Format:** Entire JSON object
```json
{
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "a5297a7c-204c-433b-8259-6541e8f2b3d9",
  "tenantId": "...",
  ...
}
```

### 2-5. Azure Individual Values

Extract from the JSON:
- **AZURE_CLIENT_ID**: Copy `clientId` value only
- **AZURE_CLIENT_SECRET**: Copy `clientSecret` value only
- **AZURE_SUBSCRIPTION_ID**: `a5297a7c-204c-433b-8259-6541e8f2b3d9`
- **AZURE_TENANT_ID**: Copy `tenantId` value only

### 6. AZURE_VM_SSH_KEY

**Format:** Complete SSH private key
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAACFwAAAAdzc2gtcn
...
(many lines)
...
AAAAGGVkdWF0dGVuZC1henVyZS12bQECAwQF
-----END OPENSSH PRIVATE KEY-----
```

### 7-8. GitHub Container Registry

- **GHCR_USERNAME**: `TOR50` (your GitHub username)
- **GHCR_TOKEN**: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 9-10. Database & Storage

- **DATABASE_URL**: `postgresql://user:pass@host.neon.tech/dbname?sslmode=require`
- **CLOUDINARY_URL**: `cloudinary://123456789012345:AbCdEfGhIjKlMnOpQrSt@your-cloud-name`

### 11. Django Secret Key

**Format:** Random string (50-60 characters)
```
django-insecure-w3#k5$x9&m2@n8!p4^r6*t1%y7-q0=s8+v5_d3~h9
```

---

## ✅ Verify Secrets

After adding all secrets:

1. Go to: **Actions** → **Secrets**
2. You should see 11 secrets (12th added after deployment)
3. Secrets are masked (shown as `***`)
4. You can update but not view secret values

---

## 🚀 Trigger the Pipeline

### First Deployment

1. Go to: **https://github.com/TOR50/TOR50-Capstone_KC739_CSE399/actions**
2. Click **"DevOps Demo Pipeline"** workflow
3. Click **"Run workflow"** button
4. Configure:
   - **Terraform action:** `apply`
   - **Deploy application:** ✅ (checked)
   - **Setup monitoring:** ✅ (checked)
5. Click **"Run workflow"**

### Monitor Progress

Watch the pipeline execute:
- ✅ **Terraform** (5-7 minutes) - Provisions Azure VM
- ✅ **Ansible Deploy** (10-15 minutes) - Deploys application
- ✅ **Ansible Monitoring** (10-15 minutes) - Installs Nagios
- ✅ **Summary** - Shows access URLs

**Total time:** ~25-35 minutes

---

## 📊 After First Deployment

### Get VM IP Address

The pipeline outputs will show:
```
VM IP: XX.XX.XX.XX
Application URL: http://XX.XX.XX.XX:8000
Nagios URL: http://XX.XX.XX.XX:8080/nagios
```

### Add SSH_HOST Secret (Optional)

If you plan to use the existing `ci-cd.yml` workflow:

1. Copy the VM IP from output
2. Go to: **Secrets** → **New repository secret**
3. Name: `SSH_HOST`
4. Value: `XX.XX.XX.XX` (VM IP address)

---

## 🔄 Re-run Pipeline

### Update Application

To redeploy after code changes:

1. **Actions** → **DevOps Demo Pipeline** → **Run workflow**
2. Configure:
   - **Terraform action:** `plan` (or skip)
   - **Deploy application:** ✅
   - **Setup monitoring:** ❌ (already installed)
3. Click **"Run workflow"**

### Destroy Infrastructure

To delete all Azure resources:

1. **Actions** → **DevOps Demo Pipeline** → **Run workflow**
2. Configure:
   - **Terraform action:** `destroy`
   - **Deploy application:** ❌
   - **Setup monitoring:** ❌
3. Click **"Run workflow"**

---

## 🐛 Troubleshooting

### Pipeline Fails at Terraform

**Issue:** "Error: building account: could not acquire access token"

**Solution:**
- Verify `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID` are correct
- Ensure service principal has Contributor role
- Check Azure subscription is active

### Pipeline Fails at Ansible

**Issue:** "Failed to connect to host"

**Solution:**
- Wait 2-3 minutes after Terraform completes (VM booting)
- Verify `AZURE_VM_SSH_KEY` is the complete private key
- Check NSG allows SSH (port 22)

### Container Pull Fails

**Issue:** "Failed to pull container image"

**Solution:**
- Verify `GHCR_USERNAME` is `TOR50`
- Regenerate `GHCR_TOKEN` with correct scopes
- Check container image exists: `ghcr.io/tor50/tor50-capstone_kc739_cse399:latest`

### Application Won't Start

**Issue:** "Application health check failed"

**Solution:**
- Verify `DATABASE_URL` is correct and accessible
- Verify `CLOUDINARY_URL` is correct
- Check `DJANGO_SECRET_KEY` is set
- Review Docker logs in pipeline output

---

## 🔒 Security Best Practices

✅ **DO:**
- Use unique, strong secrets
- Rotate tokens every 90 days
- Use separate service principal per environment
- Enable two-factor authentication on GitHub
- Review secret access logs

❌ **DON'T:**
- Commit secrets to repository
- Share secrets in plain text
- Use same credentials for production and demo
- Give unnecessary permissions to service principal

---

## 📚 Additional Resources

### Azure Service Principal
- [Create Service Principal](https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli)
- [Manage Credentials](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)

### GitHub Secrets
- [Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Using Secrets in Workflows](https://docs.github.com/en/actions/security-guides/encrypted-secrets#using-encrypted-secrets-in-a-workflow)

### GitHub Packages
- [Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Working with Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

---

## ✅ Checklist

Before triggering pipeline:

- [ ] Azure CLI installed
- [ ] Logged into Azure
- [ ] Service principal created
- [ ] GitHub PAT generated
- [ ] All 11 secrets added to GitHub
- [ ] Secret names match exactly
- [ ] Repository has Actions enabled
- [ ] Azure subscription has available credits

After successful deployment:

- [ ] VM accessible via SSH
- [ ] Application running on port 8000
- [ ] Nagios running on port 8080
- [ ] All Nagios services GREEN
- [ ] Pipeline shows success ✅

---

## 🎯 Expected Results

**After successful pipeline run:**

```
✅ Infrastructure provisioned with Terraform
✅ Application deployed with Ansible
✅ Nagios monitoring configured
✅ All services healthy

🌐 Access URLs:
- Application: http://XX.XX.XX.XX:8000
- Nagios: http://XX.XX.XX.XX:8080/nagios
- SSH: ssh -i .ssh/azure_vm_key azureuser@XX.XX.XX.XX

🎉 DevOps Demo Pipeline Complete!
```

---

## 📞 Need Help?

1. Check pipeline logs in GitHub Actions
2. Review error messages carefully
3. Verify all secrets are configured
4. Ensure Azure subscription is active
5. Check troubleshooting section above

**Ready to deploy! 🚀**
