# Terraform Outputs for EduAttend DevOps Demo

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.eduattend.name
}

output "vm_public_ip" {
  description = "Public IP address of the VM"
  value       = azurerm_public_ip.eduattend_public_ip.ip_address
}

output "vm_name" {
  description = "Name of the virtual machine"
  value       = azurerm_linux_virtual_machine.eduattend_vm.name
}

output "ssh_connection_string" {
  description = "SSH connection command"
  value       = "ssh -i ../.ssh/azure_vm_key ${var.admin_username}@${azurerm_public_ip.eduattend_public_ip.ip_address}"
}

output "application_url" {
  description = "Application URL (after deployment)"
  value       = "http://${azurerm_public_ip.eduattend_public_ip.ip_address}:8000"
}

output "nagios_url" {
  description = "Nagios monitoring URL (after setup)"
  value       = "http://${azurerm_public_ip.eduattend_public_ip.ip_address}:8080/nagios"
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.eduattend_storage.name
}

output "storage_primary_key" {
  description = "Primary access key for storage account"
  value       = azurerm_storage_account.eduattend_storage.primary_access_key
  sensitive   = true
}

output "next_steps" {
  description = "Next steps after Terraform apply"
  value = <<-EOT
    
    ✅ Infrastructure Created Successfully!
    
    Next Steps:
    1. Update Ansible inventory with VM IP: ${azurerm_public_ip.eduattend_public_ip.ip_address}
    2. Run: cd ../ansible && ansible-playbook playbooks/01-setup-vm.yml
    3. Run: ansible-playbook playbooks/02-deploy-app.yml
    4. Run: ansible-playbook playbooks/03-install-nagios.yml
    5. Access your app: http://${azurerm_public_ip.eduattend_public_ip.ip_address}:8000
    6. Access Nagios: http://${azurerm_public_ip.eduattend_public_ip.ip_address}:8080/nagios
    
    SSH Access: ssh -i ../.ssh/azure_vm_key ${var.admin_username}@${azurerm_public_ip.eduattend_public_ip.ip_address}
  EOT
}
