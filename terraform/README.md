# EduAttend - Terraform Configuration

This directory contains Infrastructure as Code (IaC) for provisioning Azure resources for the EduAttend DevOps demonstration.

## 📋 Prerequisites

1. **Azure CLI** - [Install Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. **Terraform** - [Download](https://www.terraform.io/downloads)
3. **Azure Subscription** - Student Pack or Pay-as-you-go

## 🚀 Quick Start

### Step 1: Install Azure CLI and Terraform

**Windows (PowerShell):**
```powershell
# Install Azure CLI
winget install Microsoft.AzureCLI

# Install Terraform
winget install Hashicorp.Terraform

# Verify installations
az --version
terraform --version
```

### Step 2: Login to Azure

```powershell
# Login to Azure
az login

# Verify subscription
az account show

# Set the correct subscription (if you have multiple)
az account set --subscription "a5297a7c-204c-433b-8259-6541e8f2b3d9"
```

### Step 3: Initialize Terraform

```powershell
cd terraform

# Initialize Terraform (downloads Azure provider)
terraform init
```

### Step 4: Plan Infrastructure

```powershell
# Preview what will be created
terraform plan

# Output shows:
# - Resource Group
# - Virtual Network + Subnet
# - Public IP
# - Network Security Group (Firewall rules)
# - Network Interface
# - Linux VM (Ubuntu 22.04)
# - Storage Account
```

### Step 5: Apply Configuration

```powershell
# Create infrastructure
terraform apply

# Type 'yes' when prompted
```

**Expected Output:**
```
Apply complete! Resources: 10 added, 0 changed, 0 destroyed.

Outputs:

application_url = "http://XX.XX.XX.XX:8000"
nagios_url = "http://XX.XX.XX.XX:8080/nagios"
resource_group_name = "eduattend-devops-rg"
ssh_connection_string = "ssh -i ../.ssh/azure_vm_key azureuser@XX.XX.XX.XX"
vm_public_ip = "XX.XX.XX.XX"
```

### Step 6: Verify VM Access

```powershell
# SSH into the VM
ssh -i ../.ssh/azure_vm_key azureuser@<VM_IP>

# Check Docker installation
docker --version
docker ps
```

## 📂 File Structure

```
terraform/
├── main.tf           # Main infrastructure configuration
├── variables.tf      # Configurable variables
├── outputs.tf        # Output values after deployment
├── cloud-init.yaml   # VM initialization script
└── README.md         # This file
```

## 🔧 Configuration Options

Edit `variables.tf` to customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `location` | `eastasia` | Azure region |
| `vm_size` | `Standard_B2s` | VM size (2 vCPU, 4GB RAM) |
| `admin_username` | `azureuser` | SSH username |

## 💰 Cost Estimate

| Resource | Monthly Cost |
|----------|--------------|
| VM (B2s) | ~$30 |
| Storage | ~$2 |
| Bandwidth | ~$3 |
| **Total** | **~$35/month** |

💡 **Tip:** Stop VM when not in use to save costs!

```powershell
# Stop VM (saves money)
az vm deallocate --resource-group eduattend-devops-rg --name eduattend-demo-vm

# Start VM
az vm start --resource-group eduattend-devops-rg --name eduattend-demo-vm
```

## 🎯 What Gets Created

1. **Resource Group**: Container for all resources
2. **Virtual Network**: Isolated network (10.0.0.0/16)
3. **Subnet**: VM subnet (10.0.1.0/24)
4. **Public IP**: Static IP for external access
5. **NSG**: Firewall rules (SSH, HTTP, HTTPS, Django, Nagios)
6. **Network Interface**: VM network connection
7. **Linux VM**: Ubuntu 22.04 with Docker pre-installed
8. **Storage Account**: For backups and data

## 🔒 Security Features

- ✅ SSH key authentication (no passwords)
- ✅ Network Security Group with specific port rules
- ✅ Latest Ubuntu LTS with automatic updates
- ✅ Docker daemon security configurations

## 🧹 Cleanup (Destroy Infrastructure)

```powershell
# WARNING: This deletes ALL resources!
terraform destroy

# Type 'yes' to confirm
```

## 📊 Useful Commands

```powershell
# Show current state
terraform show

# List all resources
terraform state list

# Get specific output
terraform output vm_public_ip

# Format configuration files
terraform fmt

# Validate configuration
terraform validate

# Refresh state
terraform refresh
```

## 🐛 Troubleshooting

### Issue: "Error creating Virtual Machine"

**Solution:** Check Azure quota limits
```powershell
az vm list-usage --location eastasia -o table
```

### Issue: "Subscription not found"

**Solution:** Login again and set subscription
```powershell
az login
az account set --subscription "a5297a7c-204c-433b-8259-6541e8f2b3d9"
```

### Issue: SSH connection refused

**Solution:** Wait 2-3 minutes after `terraform apply` for cloud-init to complete
```powershell
# Check VM status
az vm get-instance-view --resource-group eduattend-devops-rg --name eduattend-demo-vm --query instanceView.statuses
```

## 🔄 Next Steps

After infrastructure is created:

1. ✅ Update Ansible inventory with VM IP
2. ✅ Run Ansible playbooks to deploy application
3. ✅ Configure Nagios monitoring
4. ✅ Test the deployment

👉 **Go to:** `../ansible/README.md` for deployment instructions

## 📚 Additional Resources

- [Azure Virtual Machines](https://azure.microsoft.com/en-us/services/virtual-machines/)
- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure Student Pack](https://azure.microsoft.com/en-us/free/students/)
