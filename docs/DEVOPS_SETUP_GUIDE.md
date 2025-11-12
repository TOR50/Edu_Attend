# 🚀 EduAttend DevOps Implementation Guide

Complete implementation of **Terraform**, **Ansible**, and **Nagios** for college project demonstration.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Quick Start](#quick-start)
5. [Detailed Setup](#detailed-setup)
6. [GitHub Secrets Configuration](#github-secrets)
7. [Troubleshooting](#troubleshooting)
8. [College Presentation Tips](#college-presentation)

---

## 🎯 Overview

This DevOps setup demonstrates:
- ✅ **Infrastructure as Code** (Terraform) - Azure VM provisioning
- ✅ **Configuration Management** (Ansible) - Automated deployment
- ✅ **Monitoring** (Nagios) - Uptime monitoring for Render + Azure
- ✅ **CI/CD** (GitHub Actions) - Automated pipeline

### What's Been Created

```
Production:  Render (https://edu-attend.onrender.com) ← Already working
                ↓
DevOps Demo: Azure VM (http://<your-ip>:8000)      ← New deployment
                ↓
Monitoring:  Nagios (http://<your-ip>:8080/nagios) ← Monitors both
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                        │
│                                                              │
│  Code Push → GitHub Actions CI/CD                           │
│              ├─ Build & Test                                │
│              ├─ Security Scan                               │
│              └─ Deploy to Render (Production)               │
└──────────────────────┬──────────────────────────────────────┘
                       │
         Manual Trigger: DevOps Demo Pipeline
                       │
           ┌───────────┴───────────┐
           │                       │
    ┌──────▼──────┐         ┌─────▼──────┐
    │  Terraform  │         │  Ansible   │
    │  (Infra)    │────────>│  (Deploy)  │
    └─────────────┘         └────────────┘
           │                       │
           ▼                       ▼
    ┌────────────────────────────────────────┐
    │         Azure Virtual Machine          │
    │                                        │
    │  ┌──────────┐      ┌──────────┐      │
    │  │  Docker  │      │  Nagios  │      │
    │  │   App    │      │ Monitor  │      │
    │  │  :8000   │      │  :8080   │      │
    │  └──────────┘      └──────────┘      │
    └────────────────────────────────────────┘
                    │
                    ├─ Monitors Render
                    └─ Monitors Azure
```

---

## 📦 Prerequisites

### Required Software

| Tool | Version | Installation |
|------|---------|-------------|
| Azure CLI | Latest | `winget install Microsoft.AzureCLI` |
| Terraform | 1.0+ | `winget install Hashicorp.Terraform` |
| Ansible | 2.9+ | `pip install ansible` |
| Python | 3.8+ | `winget install Python.Python.3.11` |
| Git | Latest | Already installed |

### Azure Requirements

- ✅ Azure Student Subscription (ID: `a5297a7c-204c-433b-8259-6541e8f2b3d9`)
- ✅ $100 Azure credits available
- ✅ Access to Azure Portal

### GitHub Requirements

- ✅ Repository access (TOR50/TOR50-Capstone_KC739_CSE399)
- ✅ Ability to create GitHub Secrets
- ✅ GitHub Personal Access Token (for GHCR)

---

## 🚀 Quick Start (5 Steps)

### Step 1: Install Tools (5 minutes)

```powershell
# Install Azure CLI
winget install Microsoft.AzureCLI

# Install Terraform
winget install Hashicorp.Terraform

# Install Python packages
pip install ansible

# Verify installations
az --version
terraform --version
ansible --version
```

### Step 2: Azure Login (2 minutes)

```powershell
# Login to Azure
az login

# Set subscription
az account set --subscription "a5297a7c-204c-433b-8259-6541e8f2b3d9"

# Verify
az account show
```

### Step 3: Deploy Infrastructure (5 minutes)

```powershell
# Navigate to project
cd "d:\Edu Attend app\Django App"

# Initialize Terraform
cd terraform
terraform init

# Preview changes
terraform plan

# Deploy!
terraform apply
# Type 'yes' when prompted

# Save the VM IP shown in output
```

### Step 4: Deploy Application (10 minutes)

```powershell
# Navigate to Ansible
cd ../ansible

# Update inventory with VM IP (from Step 3)
# Edit: inventory/azure_hosts.yml
# Replace: REPLACE_WITH_VM_IP with actual IP

# Set environment variables
$env:GHCR_USERNAME = "TOR50"
$env:GHCR_TOKEN = "your_github_token"  # Get from GitHub settings
$env:DATABASE_URL = "your_neon_postgres_url"
$env:CLOUDINARY_URL = "your_cloudinary_url"

# Run playbooks
ansible-playbook playbooks/01-setup-vm.yml
ansible-playbook playbooks/02-deploy-app.yml
ansible-playbook playbooks/03-install-nagios.yml
```

### Step 5: Access Your Deployment (1 minute)

```
🌐 Application: http://<your-vm-ip>:8000
📊 Nagios:     http://<your-vm-ip>:8080/nagios
🔑 SSH:        ssh -i .ssh/azure_vm_key azureuser@<your-vm-ip>
```

**Nagios Credentials:**
- Username: `nagiosadmin`
- Password: `nagiosadmin123`

---

## 📝 Detailed Setup

### A. Azure Configuration

#### 1. Get Azure Credentials

```powershell
# Get subscription details
az account show

# Create service principal for Terraform
az ad sp create-for-rbac --name "eduattend-terraform" --role Contributor --scopes /subscriptions/a5297a7c-204c-433b-8259-6541e8f2b3d9
```

Save the output (you'll need it for GitHub Secrets):
```json
{
  "appId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "displayName": "eduattend-terraform",
  "password": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenant": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

#### 2. Configure Terraform Variables

The default values are already set in `terraform/variables.tf`:
- Subscription ID: `a5297a7c-204c-433b-8259-6541e8f2b3d9`
- Region: `eastasia`
- SSH Key: Auto-generated in `.ssh/azure_vm_key`

**To customize:**
```powershell
cd terraform
cp variables.tf terraform.tfvars
# Edit terraform.tfvars with your preferences
```

### B. GitHub Configuration

#### 1. Get GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Select scopes:
   - ✅ `repo` (Full control of repositories)
   - ✅ `read:packages`
   - ✅ `write:packages`
4. Click **"Generate token"**
5. **COPY THE TOKEN** (you can't see it again!)

#### 2. Configure GitHub Secrets

Go to: `https://github.com/TOR50/TOR50-Capstone_KC739_CSE399/settings/secrets/actions`

Add these secrets:

| Secret Name | Value | Where to Get It |
|------------|-------|-----------------|
| `AZURE_CLIENT_ID` | appId from service principal | Azure CLI output |
| `AZURE_CLIENT_SECRET` | password from service principal | Azure CLI output |
| `AZURE_SUBSCRIPTION_ID` | `a5297a7c-204c-433b-8259-6541e8f2b3d9` | Known |
| `AZURE_TENANT_ID` | tenant from service principal | Azure CLI output |
| `AZURE_VM_SSH_KEY` | Content of `.ssh/azure_vm_key` | Generated file |
| `GHCR_USERNAME` | `TOR50` | Your GitHub username |
| `GHCR_TOKEN` | Your PAT | Step B.1 above |
| `DATABASE_URL` | Your Neon PostgreSQL URL | Neon dashboard |
| `CLOUDINARY_URL` | Your Cloudinary URL | Cloudinary dashboard |
| `DJANGO_SECRET_KEY` | Generate new key | Use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |

#### 3. Copy SSH Private Key

```powershell
# Display private key content
Get-Content ".ssh\azure_vm_key"

# Copy the entire output (including BEGIN and END lines)
# Paste into AZURE_VM_SSH_KEY secret in GitHub
```

### C. Manual Deployment Steps

#### 1. Terraform Deployment

```powershell
cd terraform

# Initialize
terraform init

# Plan (preview changes)
terraform plan

# Apply (create resources)
terraform apply

# Get outputs
terraform output vm_public_ip
terraform output ssh_connection_string
```

**Expected time:** 5-7 minutes

#### 2. Ansible Deployment

```powershell
cd ../ansible

# Get VM IP from Terraform
$vmIp = (cd ../terraform; terraform output -raw vm_public_ip)
echo "VM IP: $vmIp"

# Update inventory
(Get-Content inventory/azure_hosts.yml) -replace 'REPLACE_WITH_VM_IP', $vmIp | Set-Content inventory/azure_hosts.yml

# Test connection
ansible all -m ping

# Setup VM
ansible-playbook playbooks/01-setup-vm.yml

# Deploy application
ansible-playbook playbooks/02-deploy-app.yml

# Install Nagios
ansible-playbook playbooks/03-install-nagios.yml
```

**Expected time:** 15-20 minutes total

### D. Automated CI/CD Pipeline

#### 1. Trigger Pipeline

1. Go to: `https://github.com/TOR50/TOR50-Capstone_KC739_CSE399/actions`
2. Select **"DevOps Demo Pipeline"**
3. Click **"Run workflow"**
4. Configure options:
   - Terraform action: `apply`
   - Deploy application: ✅
   - Setup monitoring: ✅
5. Click **"Run workflow"**

#### 2. Monitor Execution

Watch the pipeline execute:
- ✅ Terraform provisions infrastructure
- ✅ Ansible deploys application
- ✅ Nagios monitoring configured
- ✅ Summary generated

**Expected time:** 20-25 minutes

---

## 🔐 GitHub Secrets Configuration

### Quick Reference

```powershell
# Generate Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Get SSH private key
Get-Content ".ssh\azure_vm_key"

# Get Azure service principal
az ad sp create-for-rbac --name "eduattend-terraform" --role Contributor --scopes /subscriptions/a5297a7c-204c-433b-8259-6541e8f2b3d9
```

### Azure Credentials Format

```json
{
  "clientId": "<AZURE_CLIENT_ID>",
  "clientSecret": "<AZURE_CLIENT_SECRET>",
  "subscriptionId": "a5297a7c-204c-433b-8259-6541e8f2b3d9",
  "tenantId": "<AZURE_TENANT_ID>"
}
```

---

## 🐛 Troubleshooting

### Issue 1: Terraform "Unauthorized" Error

**Error:**
```
Error: building account: could not acquire access token
```

**Solution:**
```powershell
# Re-login to Azure
az login

# Set subscription
az account set --subscription "a5297a7c-204c-433b-8259-6541e8f2b3d9"

# Try again
terraform apply
```

### Issue 2: Ansible "Permission Denied"

**Error:**
```
Permission denied (publickey)
```

**Solution:**
```powershell
# Check key permissions
icacls ".ssh\azure_vm_key"

# Fix permissions (Windows)
icacls ".ssh\azure_vm_key" /inheritance:r
icacls ".ssh\azure_vm_key" /grant:r "%USERNAME%:F"

# Test SSH manually
ssh -i .ssh/azure_vm_key azureuser@<vm-ip>
```

### Issue 3: Application Not Accessible

**Error:** Can't access http://<vm-ip>:8000

**Solution:**
```powershell
# SSH into VM
ssh -i .ssh/azure_vm_key azureuser@<vm-ip>

# Check Docker status
docker ps

# Check logs
docker logs eduattend-app

# Restart container if needed
docker restart eduattend-app
```

### Issue 4: Nagios Not Loading

**Error:** Can't access Nagios web interface

**Solution:**
```bash
# SSH into VM
sudo systemctl status apache2
sudo systemctl status nagios

# Restart services
sudo systemctl restart apache2
sudo systemctl restart nagios

# Check logs
sudo tail -f /usr/local/nagios/var/nagios.log
```

### Issue 5: GitHub Actions Failing

**Error:** Workflow fails at various steps

**Solution:**
1. Check all GitHub Secrets are configured
2. Verify secret names match exactly
3. Ensure Azure subscription is active
4. Check Azure credit balance
5. Review workflow logs for specific errors

---

## 🎓 College Presentation Tips

### Demo Flow (10 minutes)

1. **Introduction (2 min)**
   - Explain DevOps and its importance
   - Show current Render deployment (working)

2. **Infrastructure as Code (2 min)**
   - Open `terraform/main.tf`
   - Explain resources being created
   - Show `terraform plan` output
   - Run `terraform apply` (or show video)

3. **Configuration Management (3 min)**
   - Open `ansible/playbooks/02-deploy-app.yml`
   - Explain automation benefits
   - Show Ansible execution logs
   - Access deployed application on Azure

4. **Monitoring (2 min)**
   - Open Nagios dashboard
   - Show both Render and Azure monitoring
   - Explain uptime checks
   - Demonstrate alert configuration

5. **CI/CD Pipeline (1 min)**
   - Show GitHub Actions workflow
   - Explain automation pipeline
   - Display successful run

### Key Points to Highlight

✅ **Automation:** "No manual server configuration needed"  
✅ **Reproducibility:** "Same infrastructure every time"  
✅ **Multi-Cloud:** "Works on Azure, can adapt to AWS/GCP"  
✅ **Monitoring:** "Proactive issue detection"  
✅ **Version Control:** "Infrastructure in Git"  

### Questions to Prepare For

**Q: Why use Terraform instead of Azure Portal?**
> A: Infrastructure as Code enables version control, automation, reproducibility, and collaboration. Manual portal changes can't be tracked or replicated.

**Q: What's the advantage of Ansible over shell scripts?**
> A: Ansible is idempotent (safe to run multiple times), has built-in modules for common tasks, and uses declarative syntax that's easier to maintain.

**Q: How does Nagios compare to modern monitoring tools?**
> A: For this demo, Nagios shows fundamental monitoring concepts. In production, we might use Prometheus, Grafana, or cloud-native solutions, but the principles are the same.

**Q: What happens if the VM goes down?**
> A: Nagios detects downtime, sends alerts, and logs the incident. We can then investigate and use Terraform to rebuild if needed.

**Q: Is this production-ready?**
> A: This demonstrates core DevOps concepts. For production, we'd add: HTTPS, backup strategies, scaling, security hardening, logging aggregation, and disaster recovery.

### Architecture Diagram for Presentation

Include this in your slides:

```
┌─────────────────────────────────────────┐
│         Developer Workflow              │
│  Git Push → GitHub Actions CI/CD        │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼──────┐    ┌─────▼──────┐
│Production│    │DevOps Demo │
│ (Render) │    │  (Azure)   │
└─────┬────┘    └──────┬─────┘
      │                │
      └────┬───────────┘
           │
      ┌────▼─────┐
      │  Nagios  │
      │ Monitor  │
      └──────────┘
```

---

## 📊 Cost Management

### Monthly Costs

| Resource | Cost | Control |
|----------|------|---------|
| Azure VM (B2s) | ~$30 | Stop when not needed |
| Storage | ~$2 | Minimal usage |
| Bandwidth | ~$3 | Normal usage |
| **Total** | **~$35** | |

### Stop VM to Save Money

```powershell
# Stop VM (keeps disk, stops compute billing)
az vm deallocate --resource-group eduattend-devops-rg --name eduattend-demo-vm

# Start VM when needed
az vm start --resource-group eduattend-devops-rg --name eduattend-demo-vm
```

### Complete Cleanup

```powershell
# Destroy all resources
cd terraform
terraform destroy

# Type 'yes' to confirm
```

---

## 📚 Additional Resources

### Documentation
- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Ansible Documentation](https://docs.ansible.com/)
- [Nagios Core](https://www.nagios.org/documentation/)
- [Azure Student Resources](https://azure.microsoft.com/en-us/free/students/)

### Learning Resources
- [Terraform Tutorials](https://learn.hashicorp.com/terraform)
- [Ansible Getting Started](https://docs.ansible.com/ansible/latest/getting_started/index.html)
- [DevOps Roadmap](https://roadmap.sh/devops)

---

## ✅ Success Checklist

Before your presentation, verify:

- [ ] Azure VM is running
- [ ] Application accessible on port 8000
- [ ] Nagios accessible on port 8080
- [ ] All Nagios services show GREEN
- [ ] Render app still working (production)
- [ ] GitHub Actions workflow runs successfully
- [ ] SSH access works
- [ ] Can explain each component
- [ ] Screenshots/recordings prepared
- [ ] Cost tracking enabled

---

## 🎯 Summary

You now have:

1. ✅ **Infrastructure as Code** - Azure VM provisioned with Terraform
2. ✅ **Automated Deployment** - Application deployed with Ansible
3. ✅ **Monitoring** - Nagios tracking Render + Azure uptime
4. ✅ **CI/CD Pipeline** - GitHub Actions automation
5. ✅ **Multi-Cloud** - Production on Render, Demo on Azure
6. ✅ **Complete Documentation** - Setup guides and troubleshooting

**Total Setup Time:** ~45 minutes  
**Monthly Cost:** ~$35 (with $100 Azure credits)  
**Demo Value:** ⭐⭐⭐⭐⭐

---

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review logs (Terraform, Ansible, Docker, Nagios)
3. Verify all prerequisites are installed
4. Ensure Azure subscription is active
5. Check GitHub Secrets are configured correctly

**Good luck with your college project! 🚀**
