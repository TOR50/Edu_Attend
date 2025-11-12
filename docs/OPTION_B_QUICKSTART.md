# 🚀 Option B: Automated GitHub Actions - Quick Start

**Deploy everything with a single click using GitHub Actions!**

---

## ⚡ Super Quick Start (3 Steps)

### Step 1: Collect Secret Values (10 minutes)

**Run the automated script:**
```powershell
cd "d:\Edu Attend app\Django App"
.\collect-github-secrets.ps1
```

This script will:
- ✅ Create Azure Service Principal automatically
- ✅ Extract SSH private key
- ✅ Generate Django secret key
- ✅ Save everything to a text file
- ⚠️ Ask you to manually get: GitHub token, Database URL, Cloudinary URL

### Step 2: Add Secrets to GitHub (5 minutes)

1. Go to: **https://github.com/TOR50/TOR50-Capstone_KC739_CSE399/settings/secrets/actions**
2. Click **"New repository secret"** for each value from the script output
3. Add all 11 secrets (names must match exactly!)

### Step 3: Trigger Deployment (1 minute)

1. Go to: **https://github.com/TOR50/TOR50-Capstone_KC739_CSE399/actions**
2. Click **"DevOps Demo Pipeline"**
3. Click **"Run workflow"**
4. Configure:
   - Terraform action: **apply**
   - Deploy application: ✅
   - Setup monitoring: ✅
5. Click **"Run workflow"**
6. ☕ Wait 25-35 minutes

---

## 📋 Required GitHub Secrets

| # | Secret Name | How to Get |
|---|-------------|-----------|
| 1 | `AZURE_CREDENTIALS` | Run script (auto) |
| 2 | `AZURE_CLIENT_ID` | Run script (auto) |
| 3 | `AZURE_CLIENT_SECRET` | Run script (auto) |
| 4 | `AZURE_SUBSCRIPTION_ID` | `a5297a7c-204c-433b-8259-6541e8f2b3d9` |
| 5 | `AZURE_TENANT_ID` | Run script (auto) |
| 6 | `AZURE_VM_SSH_KEY` | Run script (auto) |
| 7 | `GHCR_USERNAME` | `TOR50` |
| 8 | `GHCR_TOKEN` | [Create manually](https://github.com/settings/tokens) |
| 9 | `DATABASE_URL` | [Neon Dashboard](https://neon.tech/) |
| 10 | `CLOUDINARY_URL` | [Cloudinary Console](https://cloudinary.com/console) |
| 11 | `DJANGO_SECRET_KEY` | Run script (auto) |

---

## 🔑 Manual Values Needed

### 1. GitHub Personal Access Token (GHCR_TOKEN)

1. Go to: **https://github.com/settings/tokens**
2. Click **"Generate new token (classic)"**
3. Select scopes:
   - ✅ `repo`
   - ✅ `read:packages`
   - ✅ `write:packages`
4. Click **"Generate token"**
5. **Copy immediately!** (Format: `ghp_xxxxx...`)

### 2. Database URL (DATABASE_URL)

1. Go to: **https://neon.tech/**
2. Login → Your Project → Dashboard
3. Click **"Connection String"**
4. Copy the PostgreSQL URL
5. Format: `postgresql://user:pass@host.neon.tech/dbname?sslmode=require`

### 3. Cloudinary URL (CLOUDINARY_URL)

1. Go to: **https://cloudinary.com/console**
2. Login → Dashboard
3. Find **"API Environment variable"**
4. Copy the complete URL
5. Format: `cloudinary://api_key:api_secret@cloud_name`

---

## 🎬 What Happens During Deployment

### Phase 1: Terraform (5-7 minutes)
```
✅ Login to Azure
✅ Initialize Terraform
✅ Validate configuration
✅ Create infrastructure plan
✅ Apply changes:
   - Create Resource Group
   - Create Virtual Network
   - Create Public IP
   - Create Network Security Group
   - Create Network Interface
   - Create Linux VM (Ubuntu 22.04)
   - Create Storage Account
✅ Output VM IP address
```

### Phase 2: Ansible Deploy (10-15 minutes)
```
✅ Connect to VM via SSH
✅ Setup VM:
   - Install Docker
   - Configure firewall
   - Create app directory
✅ Deploy Application:
   - Login to GitHub Container Registry
   - Pull latest Docker image
   - Create environment file
   - Start application container
   - Health check on port 8000
```

### Phase 3: Ansible Monitoring (10-15 minutes)
```
✅ Connect to VM
✅ Install Nagios:
   - Install dependencies
   - Compile Nagios Core
   - Install plugins
   - Configure Apache (port 8080)
✅ Configure Monitoring:
   - Add Render app check
   - Add Azure app check
   - Setup email alerts
   - Start services
```

### Phase 4: Summary
```
✅ Display access URLs
✅ Show deployment status
✅ Generate summary report
```

---

## 🌐 After Deployment

### Access Your Deployment

**From GitHub Actions output:**
```
🌐 Application: http://XX.XX.XX.XX:8000
📊 Nagios:     http://XX.XX.XX.XX:8080/nagios
🔐 SSH:        ssh -i .ssh/azure_vm_key azureuser@XX.XX.XX.XX
```

**Nagios Login:**
- Username: `nagiosadmin`
- Password: `nagiosadmin123`

### Verify Everything Works

1. ✅ Open application URL → Should show login page
2. ✅ Open Nagios URL → Login with credentials
3. ✅ Check all services are GREEN
4. ✅ Verify both Render and Azure are monitored

---

## 🔄 Common Operations

### Redeploy Application Only

**When:** After code changes

1. Go to: **Actions** → **DevOps Demo Pipeline**
2. Click **"Run workflow"**
3. Configure:
   - Terraform action: **plan** (or skip)
   - Deploy application: ✅
   - Setup monitoring: ❌
4. Time: ~10 minutes

### Update Monitoring Only

**When:** Change monitoring configuration

1. Go to: **Actions** → **DevOps Demo Pipeline**
2. Click **"Run workflow"**
3. Configure:
   - Terraform action: **plan**
   - Deploy application: ❌
   - Setup monitoring: ✅
4. Time: ~15 minutes

### Destroy Infrastructure

**When:** Demo complete, save money

1. Go to: **Actions** → **DevOps Demo Pipeline**
2. Click **"Run workflow"**
3. Configure:
   - Terraform action: **destroy**
   - Deploy application: ❌
   - Setup monitoring: ❌
4. Type: `yes` when prompted
5. Time: ~5 minutes

---

## 🐛 Troubleshooting Pipeline

### Pipeline Fails at Terraform

**Check:**
- [ ] Azure CLI secrets are correct
- [ ] Service principal has permissions
- [ ] Azure subscription is active
- [ ] No quota limits reached

**Fix:** Review Terraform logs in Actions

### Pipeline Fails at Ansible

**Check:**
- [ ] SSH key is complete (including BEGIN/END lines)
- [ ] VM has finished booting (wait 2-3 min)
- [ ] Network security group allows SSH

**Fix:** Wait and retry

### Pipeline Fails at Docker Pull

**Check:**
- [ ] GHCR_TOKEN has correct scopes
- [ ] GHCR_USERNAME is `TOR50`
- [ ] Container image exists in registry

**Fix:** Regenerate GitHub token

### Application Won't Start

**Check:**
- [ ] DATABASE_URL is correct
- [ ] CLOUDINARY_URL is correct
- [ ] DJANGO_SECRET_KEY is set
- [ ] Container image is valid

**Fix:** Check Docker logs in pipeline output

---

## 💰 Cost Reminder

**Running Costs:**
- VM (B2s): ~$1.17/day
- Storage: ~$0.07/day
- **Total:** ~$1.24/day

**To Save Money:**
```powershell
# Stop VM (keeps configuration, stops billing)
az vm deallocate --resource-group eduattend-devops-rg --name eduattend-demo-vm

# Start when needed
az vm start --resource-group eduattend-devops-rg --name eduattend-demo-vm
```

**Or destroy everything:**
- Use pipeline with **Terraform action: destroy**

---

## ✅ Pre-Deployment Checklist

Before triggering the pipeline:

- [ ] Azure CLI installed (script will check)
- [ ] Logged into Azure (script will check)
- [ ] Script completed successfully
- [ ] All 11 GitHub Secrets added
- [ ] Secret names match exactly (case-sensitive)
- [ ] GitHub token has correct scopes
- [ ] Database and Cloudinary URLs are valid
- [ ] Repository Actions are enabled

---

## 🎯 Expected Timeline

| Step | Duration | Cumulative |
|------|----------|------------|
| Collect secrets | 10 min | 10 min |
| Add to GitHub | 5 min | 15 min |
| Trigger workflow | 1 min | 16 min |
| Terraform | 7 min | 23 min |
| Ansible Deploy | 12 min | 35 min |
| Ansible Monitoring | 15 min | 50 min |
| Verification | 5 min | 55 min |

**Total:** ~1 hour (45 min automated + 10 min manual)

---

## 📚 Detailed Documentation

For more details, see:
- **Complete Guide:** `docs/GITHUB_SECRETS_SETUP.md`
- **Terraform Guide:** `terraform/README.md`
- **Ansible Guide:** `ansible/README.md`
- **Nagios Guide:** `nagios/README.md`

---

## 🎉 Success!

**After successful deployment, you'll have:**

✅ Azure VM running your application  
✅ Application accessible on port 8000  
✅ Nagios monitoring both Render and Azure  
✅ Complete CI/CD pipeline  
✅ Infrastructure as Code  
✅ Automated configuration management  
✅ College project ready to demonstrate!  

**Ready to impress your professors! 🎓🚀**
