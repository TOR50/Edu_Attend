# Terraform Variables for EduAttend DevOps Demo

variable "azure_subscription_id" {
  description = "Azure Subscription ID"
  type        = string
  default     = "a5297a7c-204c-433b-8259-6541e8f2b3d9"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastasia"  # Can use "centralindia" as alternative
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "eduattend-devops-rg"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "eduattend-demo"
}

variable "vm_size" {
  description = "Azure VM size"
  type        = string
  default     = "Standard_B2s"  # 2 vCPU, 4 GB RAM (~$30/month)
}

variable "admin_username" {
  description = "Admin username for the VM"
  type        = string
  default     = "azureuser"
}

variable "ssh_public_key" {
  description = "SSH public key for VM access"
  type        = string
  default     = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDPewOGwzSgDQ3P4SVhxqDVpVhXfm4LrbbNLZu2CqGeHjYlzv0FqlBCMXDVFNDENV6yU7TZdW+9NNtjVuzeA0SFAvwkjBzPidhCCFfpotUDj8VErv5wBKxpTa3M2PKiSt6tjSZF2SKeZL2kibzyghLr4/V3gau10Mzjgmo7yM4CJefLNkcIj3bWD8jLyy6Tob5HZDjnNLUITan0W78ZNQya9vboI16XheCjQXrkepncuZY4uo8m6D7vuMkkt+dDG2kpQypLuK94oALBpJUsRW8bGXzndsQa1qx1BsgsT9VEBN6Yes8Ymbarfv/dH9GeLcOdq9/SsjobTp4hOyK/Lp3OPwRKrFoiYX9VIPIVZMtyXZyHrTrxYo94qsRjd+THJKA6pterOQzgNR3ZpGK4tQU1+NdjEFp73flLwRYlE0bWdgZfCwZQwmg3M7OO0ievrrmB1tUXRXP3n+vNGTtSOPNATGljyVKZ9yU1qBKZb/WjqHtENcqQKVj/e7NOEejDlfqhSSTDMEoCmavXaWNxVs0Wauh42kdIADQejclWeH5Lvj7drHTzZPCj9tmk5MnI0sK4wab55fzrdmJAwG7fwGEl1eA60IR5HfaB+gZwsLA0vDUkKwNi2iH/yP/AGfZ/59wQvTPcr/fu08eSSVoMCzVz3+ZSfNQVjBlu+M0U037+fw== eduattend-azure-vm"
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "EduAttend"
    Environment = "DevOps-Demo"
    ManagedBy   = "Terraform"
    Purpose     = "College-Project"
  }
}
