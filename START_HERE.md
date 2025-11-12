# 🎯 SIMPLIFIED SETUP - No Azure CLI Required!

You can set up GitHub Secrets without installing Azure CLI. Here's the simplified approach:

---

## 🚀 **EASY PATH: Use Azure Portal Instead**

Since Azure CLI isn't installed, we'll use the Azure Portal web interface.

---

## ✅ **Step 1: Create Service Principal via Azure Portal**

### Method 1: Using Azure Cloud Shell (Recommended - No Installation!)

1. **Go to:** https://portal.azure.com
2. **Login** with your Azure Student account
3. **Click** the **Cloud Shell icon** (>_) at the top right
4. **Choose** "PowerShell" if prompted
5. **Run this command:**

```bash
az ad sp create-for-rbac --name "eduattend-github-actions" --role Contributor --scopes /subscriptions/a5297a7c-204c-433b-8259-6541e8f2b3d9 --sdk-auth
```

6. **COPY THE ENTIRE OUTPUT** and save it to a text file

### Method 2: Manual Creation (Alternative)

1. **Go to:** https://portal.azure.com
2. **Search for:** "Azure Active Directory" or "Microsoft Entra ID"
3. **Click:** "App registrations"
4. **Click:** "New registration"
5. **Name:** `eduattend-github-actions`
6. **Click:** "Register"
7. **Copy the following:**
   - Application (client) ID
   - Directory (tenant) ID
8. **Go to:** "Certificates & secrets"
9. **Click:** "New client secret"
10. **Description:** `github-actions`
11. **Expires:** 90 days
12. **Click:** "Add"
13. **COPY THE SECRET VALUE IMMEDIATELY** (you can't see it again!)

---

## ✅ **Step 2: Get Existing Values**

### A. SSH Private Key (Already Generated!)

```powershell
Get-Content ".ssh\azure_vm_key"
```

**Copy the entire output** including BEGIN and END lines.

### B. Django Secret Key

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**If Python command doesn't work,** use this fallback key:
```
django-insecure-k5$x9&m2@n8!p4^r6*t1%y7-q0=s8+v5_d3~h9j2^w3#a4$b6
```

---

## ✅ **Step 3: Get External Services**

### A. GitHub Personal Access Token

1. **Go to:** https://github.com/settings/tokens
2. **Click:** "Generate new token (classic)"
3. **Note:** `eduattend-devops`
4. **Expiration:** 90 days
5. **Select scopes:**
   - ✅ `repo` (Full control of private repositories)
   - ✅ `read:packages`
   - ✅ `write:packages`
6. **Click:** "Generate token"
7. **COPY IMMEDIATELY:** `ghp_xxxxxx...`

### B. Neon Database URL

**If you already have Neon set up:**
1. Go to: https://neon.tech/
2. Login → Your Project
3. Copy the connection string

**Format:**
```
postgresql://username:password@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### C. Cloudinary URL

**If you already have Cloudinary set up:**
1. Go to: https://cloudinary.com/console
2. Dashboard → Account Details
3. Copy the "API Environment variable"

**Format:**
```
cloudinary://123456789012345:AbCdEfGhIjKlMnOpQrStUvWxYz@your-cloud-name
```

---

## ✅ **Step 4: Add All Secrets to GitHub**

### Navigate to Secrets

https://github.com/TOR50/TOR50-Capstone_KC739_CSE399/settings/secrets/actions

### Add These 11 Secrets

For each secret:
1. Click **"New repository secret"**
2. Enter **Name** (must match exactly)
3. Paste **Value**
4. Click **"Add secret"**

---

### Secret #1: AZURE_CREDENTIALS

**Name:** `AZURE_CREDENTIALS`

**Value:** The entire JSON from Azure Cloud Shell

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

---

### Secret #2: AZURE_CLIENT_ID

**Name:** `AZURE_CLIENT_ID`

**Value:** Just the clientId from the JSON (no quotes)
```
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

### Secret #3: AZURE_CLIENT_SECRET

**Name:** `AZURE_CLIENT_SECRET`

**Value:** Just the clientSecret from the JSON
```
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

### Secret #4: AZURE_SUBSCRIPTION_ID

**Name:** `AZURE_SUBSCRIPTION_ID`

**Value:**
```
a5297a7c-204c-433b-8259-6541e8f2b3d9
```

---

### Secret #5: AZURE_TENANT_ID

**Name:** `AZURE_TENANT_ID`

**Value:** Just the tenantId from the JSON
```
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

### Secret #6: AZURE_VM_SSH_KEY

**Name:** `AZURE_VM_SSH_KEY`

**Value:** Complete private key from `.ssh\azure_vm_key`
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAACFwAAAAdzc2gtcn
...
(many lines - copy ALL of them)
...
-----END OPENSSH PRIVATE KEY-----
```

---

### Secret #7: GHCR_USERNAME

**Name:** `GHCR_USERNAME`

**Value:**
```
TOR50
```

---

### Secret #8: GHCR_TOKEN

**Name:** `GHCR_TOKEN`

**Value:** Your GitHub Personal Access Token
```
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### Secret #9: DATABASE_URL

**Name:** `DATABASE_URL`

**Value:** Your Neon PostgreSQL connection string
```
postgresql://username:password@host.neon.tech/database?sslmode=require
```

---

### Secret #10: CLOUDINARY_URL

**Name:** `CLOUDINARY_URL`

**Value:** Your Cloudinary API environment variable
```
cloudinary://api_key:api_secret@cloud_name
```

---

### Secret #11: DJANGO_SECRET_KEY

**Name:** `DJANGO_SECRET_KEY`

**Value:** Generated Django secret key
```
django-insecure-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## ✅ **Step 5: Verify All Secrets Added**

Go back to: https://github.com/TOR50/TOR50-Capstone_KC739_CSE399/settings/secrets/actions

You should see **11 secrets** listed:
- AZURE_CREDENTIALS
- AZURE_CLIENT_ID
- AZURE_CLIENT_SECRET
- AZURE_SUBSCRIPTION_ID
- AZURE_TENANT_ID
- AZURE_VM_SSH_KEY
- GHCR_USERNAME
- GHCR_TOKEN
- DATABASE_URL
- CLOUDINARY_URL
- DJANGO_SECRET_KEY

---

## ✅ **Step 6: Trigger the Pipeline!**

1. **Go to:** https://github.com/TOR50/TOR50-Capstone_KC739_CSE399/actions

2. **Click:** "DevOps Demo Pipeline" in the left sidebar

3. **Click:** "Run workflow" dropdown (top right)

4. **Configure:**
   - Branch: `main`
   - Terraform action: `apply`
   - Deploy application: ✅ Checked
   - Setup monitoring: ✅ Checked

5. **Click:** "Run workflow" button

6. **Watch it run!** ⏳ (~30 minutes)

---

## 🎉 **After Deployment**

### Check Pipeline Status

1. Click on the running workflow
2. Watch each job complete:
   - ✅ Terraform (5-7 min)
   - ✅ Ansible Deploy (10-15 min)
   - ✅ Ansible Monitoring (10-15 min)
   - ✅ Summary

### Get Your URLs

In the Summary section, you'll see:
```
🌐 Application: http://XX.XX.XX.XX:8000
📊 Nagios: http://XX.XX.XX.XX:8080/nagios
```

### Test Everything

1. Open Application URL → Should show login page
2. Open Nagios URL → Login with `nagiosadmin` / `nagiosadmin123`
3. Verify all services are GREEN ✅

---

## 🎓 **For Your Demo**

You can now show:
- ✅ Infrastructure as Code (Terraform)
- ✅ Configuration Management (Ansible)
- ✅ Continuous Monitoring (Nagios)
- ✅ CI/CD Pipeline (GitHub Actions)
- ✅ Multi-cloud deployment (Render + Azure)

---

## 💡 **Tips**

### Save Money
```powershell
# Stop VM when not demoing (via Azure Portal)
# Go to: portal.azure.com → Virtual Machines → eduattend-demo-vm → Stop
```

### Redeploy After Changes
1. Push code to GitHub
2. Go to Actions → DevOps Demo Pipeline
3. Run workflow with "apply" + "Deploy application" ✅

### Destroy Everything
1. Actions → DevOps Demo Pipeline
2. Run workflow with "destroy"

---

## 📞 **Quick Help**

**Can't access Azure Portal?**
- Verify your Azure Student subscription is active
- Check: https://portal.azure.com → Subscriptions

**GitHub token not working?**
- Regenerate with correct scopes (repo, read:packages, write:packages)
- Make sure it's a "classic" token, not "fine-grained"

**Pipeline fails?**
- Check all 11 secrets are added
- Verify secret names match exactly (case-sensitive)
- Review error logs in Actions tab

---

## ✅ **Checklist**

Before triggering pipeline:
- [ ] Created service principal via Azure Portal/Cloud Shell
- [ ] Copied SSH private key
- [ ] Generated GitHub Personal Access Token
- [ ] Got Neon database URL
- [ ] Got Cloudinary URL
- [ ] Generated Django secret key
- [ ] Added all 11 secrets to GitHub
- [ ] Verified secret names match exactly

Ready to trigger:
- [ ] All secrets showing in GitHub
- [ ] Repository Actions enabled
- [ ] Azure subscription active

---

## 🚀 **You're Ready!**

Go trigger that pipeline! 🎯

https://github.com/TOR50/TOR50-Capstone_KC739_CSE399/actions
