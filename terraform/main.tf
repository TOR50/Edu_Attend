# EduAttend DevOps Demo - Terraform Configuration
# Provisions Azure VM for hosting containerized Django application

terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.80"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.azure_subscription_id
}

# Resource Group
resource "azurerm_resource_group" "eduattend" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
  
  lifecycle {
    prevent_destroy = false
    ignore_changes  = [tags]
  }
}

# Virtual Network
resource "azurerm_virtual_network" "eduattend_vnet" {
  name                = "${var.project_name}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.eduattend.location
  resource_group_name = azurerm_resource_group.eduattend.name
  tags                = var.tags
}

# Subnet
resource "azurerm_subnet" "eduattend_subnet" {
  name                 = "${var.project_name}-subnet"
  resource_group_name  = azurerm_resource_group.eduattend.name
  virtual_network_name = azurerm_virtual_network.eduattend_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Public IP
resource "azurerm_public_ip" "eduattend_public_ip" {
  name                = "${var.project_name}-public-ip"
  location            = azurerm_resource_group.eduattend.location
  resource_group_name = azurerm_resource_group.eduattend.name
  allocation_method   = "Static"
  sku                 = "Standard"
  tags                = var.tags
}

# Network Security Group
resource "azurerm_network_security_group" "eduattend_nsg" {
  name                = "${var.project_name}-nsg"
  location            = azurerm_resource_group.eduattend.location
  resource_group_name = azurerm_resource_group.eduattend.name
  tags                = var.tags

  # SSH Access
  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  # HTTP Access
  security_rule {
    name                       = "HTTP"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  # HTTPS Access
  security_rule {
    name                       = "HTTPS"
    priority                   = 1003
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  # Django App Port
  security_rule {
    name                       = "Django"
    priority                   = 1004
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8000"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  # Nagios Web Interface
  security_rule {
    name                       = "Nagios"
    priority                   = 1005
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8080"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

# Network Interface
resource "azurerm_network_interface" "eduattend_nic" {
  name                = "${var.project_name}-nic"
  location            = azurerm_resource_group.eduattend.location
  resource_group_name = azurerm_resource_group.eduattend.name
  tags                = var.tags

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.eduattend_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.eduattend_public_ip.id
  }
}

# Associate NSG with NIC
resource "azurerm_network_interface_security_group_association" "eduattend_nsg_assoc" {
  network_interface_id      = azurerm_network_interface.eduattend_nic.id
  network_security_group_id = azurerm_network_security_group.eduattend_nsg.id
}

# Virtual Machine
resource "azurerm_linux_virtual_machine" "eduattend_vm" {
  name                = "${var.project_name}-vm"
  resource_group_name = azurerm_resource_group.eduattend.name
  location            = azurerm_resource_group.eduattend.location
  size                = var.vm_size
  admin_username      = var.admin_username
  tags                = var.tags

  network_interface_ids = [
    azurerm_network_interface.eduattend_nic.id,
  ]

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  os_disk {
    name                 = "${var.project_name}-osdisk"
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
    disk_size_gb         = 30
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }

  custom_data = base64encode(templatefile("${path.module}/cloud-init.yaml", {
    admin_username = var.admin_username
  }))
}

# Storage Account for Application Data
resource "azurerm_storage_account" "eduattend_storage" {
  name                     = lower(replace("${var.project_name}storage", "-", ""))
  resource_group_name      = azurerm_resource_group.eduattend.name
  location                 = azurerm_resource_group.eduattend.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  tags                     = var.tags
}

# Storage Container for Backups
resource "azurerm_storage_container" "backups" {
  name                  = "backups"
  storage_account_name  = azurerm_storage_account.eduattend_storage.name
  container_access_type = "private"
}
