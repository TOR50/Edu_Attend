# 🚀 Quick Reference - EduAttend DevOps

## ⚡ One-Page Cheat Sheet

### 🔑 Essential Credentials

```
Azure Subscription ID: a5297a7c-204c-433b-8259-6541e8f2b3d9
Azure Region: eastasia
SSH Key Location: .ssh/azure_vm_key
Nagios Username: nagiosadmin
Nagios Password: nagiosadmin123
Email: rauhan.official@gmail.com
```

### 📦 Installation (One-Time)

```powershell
# Install all tools
winget install Microsoft.AzureCLI
winget install Hashicorp.Terraform
pip install ansible

# Verify
az --version && terraform --version && ansible --version
```

### 🚀 Deployment (5 Commands)

```powershell
# 1. Azure Login
az login
az account set --subscription "a5297a7c-204c-433b-8259-6541e8f2b3d9"

# 2. Deploy Infrastructure
cd terraform
terraform init && terraform apply -auto-approve

# 3. Get VM IP
$vmIp = terraform output -raw vm_public_ip

# 4. Update Inventory
cd ../ansible
(Get-Content inventory/azure_hosts.yml) -replace 'REPLACE_WITH_VM_IP', $vmIp | Set-Content inventory/azure_hosts.yml

# 5. Deploy Everything
ansible-playbook playbooks/01-setup-vm.yml playbooks/02-deploy-app.yml playbooks/03-install-nagios.yml
```

### 🌐 Access URLs

```
Production:  https://edu-attend.onrender.com
Azure App:   http://<VM_IP>:8000
Nagios:      http://<VM_IP>:8080/nagios
SSH:         ssh -i .ssh/azure_vm_key azureuser@<VM_IP>
```

### 🔧 Common Commands

```powershell
# Stop VM (save money)
az vm deallocate --resource-group eduattend-devops-rg --name eduattend-demo-vm

# Start VM
az vm start --resource-group eduattend-devops-rg --name eduattend-demo-vm

# Check VM status
az vm show --resource-group eduattend-devops-rg --name eduattend-demo-vm --show-details

# Redeploy app
cd ansible
ansible-playbook playbooks/02-deploy-app.yml

# Check app logs
ssh -i .ssh/azure_vm_key azureuser@<VM_IP>
docker logs eduattend-app

# Restart Nagios
ssh -i .ssh/azure_vm_key azureuser@<VM_IP>
sudo systemctl restart nagios
```

### 🐛 Quick Fixes

**Can't connect to VM?**
```powershell
# Check VM is running
az vm show --resource-group eduattend-devops-rg --name eduattend-demo-vm --query "powerState"
```

**App not loading?**
```bash
ssh -i .ssh/azure_vm_key azureuser@<VM_IP>
docker restart eduattend-app
```

**Nagios not working?**
```bash
ssh -i .ssh/azure_vm_key azureuser@<VM_IP>
sudo systemctl restart apache2 nagios
```

### 🗑️ Cleanup (Destroy All)

```powershell
cd terraform
terraform destroy -auto-approve
```

### 📊 GitHub Secrets Needed

| Secret | Value |
|--------|-------|
| `AZURE_CLIENT_ID` | From: `az ad sp create-for-rbac` |
| `AZURE_CLIENT_SECRET` | From: `az ad sp create-for-rbac` |
| `AZURE_SUBSCRIPTION_ID` | `a5297a7c-204c-433b-8259-6541e8f2b3d9` |
| `AZURE_TENANT_ID` | From: `az ad sp create-for-rbac` |
| `AZURE_VM_SSH_KEY` | Content of `.ssh/azure_vm_key` |
| `GHCR_USERNAME` | `TOR50` |
| `GHCR_TOKEN` | GitHub PAT (packages scope) |
| `DATABASE_URL` | Neon PostgreSQL URL |
| `CLOUDINARY_URL` | Cloudinary API URL |
| `DJANGO_SECRET_KEY` | Generate with Django |

### 🎓 Demo Talking Points

1. **Terraform**: "Infrastructure defined in code, version-controlled, reproducible"
2. **Ansible**: "Automated deployment, no manual server configuration"
3. **Nagios**: "Monitors both production and demo, sends alerts"
4. **Docker**: "Consistent environment across development and production"
5. **GitHub Actions**: "Automated testing and deployment pipeline"

### 📞 Emergency Contacts

- Azure Support: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade
- GitHub Support: https://support.github.com/
- Email: rauhan.official@gmail.com

### ✅ Pre-Demo Checklist

- [ ] Azure CLI logged in
- [ ] VM is running
- [ ] App accessible on port 8000
- [ ] Nagios accessible on port 8080
- [ ] All services GREEN in Nagios
- [ ] Production app still working
- [ ] Screenshots/recordings ready
- [ ] Presentation slides prepared

### 💰 Cost Reminder

**Daily Cost:** ~$1.17  
**Weekly Cost:** ~$8.19  
**Monthly Cost:** ~$35  

**Stop VM when not demoing to save money!**

---

For detailed instructions, see: `docs/DEVOPS_SETUP_GUIDE.md`
