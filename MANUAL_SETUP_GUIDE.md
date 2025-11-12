# 🚀 MANUAL SETUP GUIDE - GitHub Secrets

Since Azure CLI is not installed yet, follow these steps to set up GitHub Secrets manually.

---

## ✅ **Step 1: Install Azure CLI** (5 minutes)

**Open PowerShell as Administrator and run:**

```powershell
# Install Azure CLI
winget install -e --id Microsoft.AzureCLI

# After installation, close PowerShell and open a new one
# Then verify installation:
az --version
```

**Alternative download:** https://aka.ms/installazurecliwindows

---

## ✅ **Step 2: Login to Azure** (2 minutes)

```powershell
# Login to Azure
az login

# Browser will open - login with your credentials

# Set your subscription
az account set --subscription "a5297a7c-204c-433b-8259-6541e8f2b3d9"

# Verify
az account show
```

---

## ✅ **Step 3: Create Azure Service Principal** (3 minutes)

```powershell
# Create service principal
az ad sp create-for-rbac --name "eduattend-github-$(Get-Date -Format 'yyyyMMdd')" --role Contributor --scopes /subscriptions/a5297a7c-204c-433b-8259-6541e8f2b3d9 --sdk-auth
```

**SAVE THE ENTIRE OUTPUT!** It looks like this:

```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "subscriptionId": "a5297a7c-204c-433b-8259-6541e8f2b3d9",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  ...
}
```

---

## ✅ **Step 4: Get SSH Private Key**

```powershell
# Display SSH private key
Get-Content ".ssh\azure_vm_key"
```

**Copy the ENTIRE output** (including BEGIN and END lines)

---

## ✅ **Step 5: Generate Django Secret Key**

```powershell
# Generate secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Copy the output**

---

## ✅ **Step 6: Get GitHub Token**

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Name: `eduattend-devops`
4. Select scopes:
   - ✅ `repo`
   - ✅ `read:packages`
   - ✅ `write:packages`
5. Click **"Generate token"**
6. **COPY IMMEDIATELY!** Format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## ✅ **Step 7: Get Database URL**

1. Go to: https://neon.tech/
2. Login → Your Project → Dashboard
3. Click **"Connection String"**
4. Copy the PostgreSQL URL
5. Should look like: `postgresql://user:pass@host.neon.tech/dbname?sslmode=require`

---

## ✅ **Step 8: Get Cloudinary URL**

1. Go to: https://cloudinary.com/console
2. Login → Dashboard
3. Find **"API Environment variable"**
4. Copy the complete URL
5. Should look like: `cloudinary://api_key:api_secret@cloud_name`

---

## ✅ **Step 9: Add Secrets to GitHub** (5 minutes)

### Go to Repository Secrets

https://github.com/TOR50/TOR50-Capstone_KC739_CSE399/settings/secrets/actions

### Add These 11 Secrets

Click **"New repository secret"** for each:

#### 1. AZURE_CREDENTIALS
**Value:** Entire JSON output from Step 3
```json
{
  "clientId": "...",
  "clientSecret": "...",
  ...
}
```

#### 2. AZURE_CLIENT_ID
**Value:** Just the `clientId` value from the JSON (no quotes)
```
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

#### 3. AZURE_CLIENT_SECRET
**Value:** Just the `clientSecret` value from the JSON
```
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

#### 4. AZURE_SUBSCRIPTION_ID
**Value:**
```
a5297a7c-204c-433b-8259-6541e8f2b3d9
```

#### 5. AZURE_TENANT_ID
**Value:** Just the `tenantId` value from the JSON
```
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

#### 6. AZURE_VM_SSH_KEY
**Value:** Complete SSH private key from Step 4
```
-----BEGIN OPENSSH PRIVATE KEY-----
...entire key...
-----END OPENSSH PRIVATE KEY-----
```

#### 7. GHCR_USERNAME
**Value:**
```
TOR50
```

#### 8. GHCR_TOKEN
**Value:** Token from Step 6
```
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 9. DATABASE_URL
**Value:** Your Neon PostgreSQL URL from Step 7
```
postgresql://user:pass@host.neon.tech/dbname?sslmode=require
```

#### 10. CLOUDINARY_URL
**Value:** Your Cloudinary URL from Step 8
```
cloudinary://api_key:api_secret@cloud_name
```

#### 11. DJANGO_SECRET_KEY
**Value:** Generated key from Step 5
```
django-insecure-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## ✅ **Step 10: Trigger GitHub Actions** (1 minute)

1. Go to: https://github.com/TOR50/TOR50-Capstone_KC739_CSE399/actions

2. Click **"DevOps Demo Pipeline"**

3. Click **"Run workflow"** dropdown

4. Configure:
   - Branch: `main`
   - Terraform action: `apply`
   - Deploy application: ✅ (checked)
   - Setup monitoring: ✅ (checked)

5. Click **"Run workflow"** button

6. Wait ~30 minutes for completion

---

## ✅ **Verification**

After pipeline completes:

1. Check **Actions** tab for green checkmark ✅
2. Click on the workflow run
3. Expand **"Summary"** job
4. You'll see:
   ```
   Application: http://XX.XX.XX.XX:8000
   Nagios: http://XX.XX.XX.XX:8080/nagios
   ```

5. Open both URLs and verify they work!

---

## 🎉 **Success!**

Your DevOps pipeline is now fully automated and ready to use!

---

## 📝 Quick Command Reference

```powershell
# Install Azure CLI
winget install Microsoft.AzureCLI

# Login
az login
az account set --subscription "a5297a7c-204c-433b-8259-6541e8f2b3d9"

# Create Service Principal
az ad sp create-for-rbac --name "eduattend-github" --role Contributor --scopes /subscriptions/a5297a7c-204c-433b-8259-6541e8f2b3d9 --sdk-auth

# Get SSH Key
Get-Content ".ssh\azure_vm_key"

# Generate Django Key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Stop VM (save money)
az vm deallocate --resource-group eduattend-devops-rg --name eduattend-demo-vm

# Start VM
az vm start --resource-group eduattend-devops-rg --name eduattend-demo-vm
```

---

## 🆘 Need Help?

- **Azure CLI Issues:** https://docs.microsoft.com/cli/azure/install-azure-cli-windows
- **GitHub Tokens:** https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- **Neon Database:** https://neon.tech/docs/get-started-with-neon/signing-up
- **Cloudinary:** https://cloudinary.com/documentation/how_to_integrate_cloudinary

Good luck! 🚀
