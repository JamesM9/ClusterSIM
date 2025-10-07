# Configure the Azure Provider
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Variables
variable "resource_group_name" {
  description = "Name of the resource group"
  default     = "px4-cloud-sim"
}

variable "location" {
  description = "Azure region"
  default     = "East US"
}

variable "controller_vm_size" {
  description = "Size of the controller VM"
  default     = "Standard_B2s"
}

variable "agent_vm_size" {
  description = "Size of the agent VMs"
  default     = "Standard_B4ms"
}

variable "agent_count" {
  description = "Number of agent VMs"
  default     = 2
}

variable "admin_username" {
  description = "Admin username for VMs"
  default     = "azureuser"
}

variable "ssh_public_key" {
  description = "SSH public key for VM access"
  type        = string
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    Environment = "PX4 Cloud Simulator"
  }
}

# Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "px4-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

# Subnet
resource "azurerm_subnet" "main" {
  name                 = "px4-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Network Security Group
resource "azurerm_network_security_group" "main" {
  name                = "px4-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  # Allow SSH
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

  # Allow HTTP
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

  # Allow HTTPS
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

  # Allow Controller API
  security_rule {
    name                       = "ControllerAPI"
    priority                   = 1004
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8000"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  # Allow Agent API (only from controller subnet)
  security_rule {
    name                       = "AgentAPI"
    priority                   = 1005
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8443"
    source_address_prefix      = "10.0.1.0/24"
    destination_address_prefix = "*"
  }

  # Allow MAVLink UDP ports
  security_rule {
    name                       = "MAVLinkUDP"
    priority                   = 1006
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Udp"
    source_port_range          = "*"
    destination_port_range     = "14560-14570"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

# Associate NSG with subnet
resource "azurerm_subnet_network_security_group_association" "main" {
  subnet_id                 = azurerm_subnet.main.id
  network_security_group_id = azurerm_network_security_group.main.id
}

# Public IP for Controller
resource "azurerm_public_ip" "controller" {
  name                = "controller-public-ip"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = {
    Environment = "Controller"
  }
}

# Network Interface for Controller
resource "azurerm_network_interface" "controller" {
  name                = "controller-nic"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.controller.id
  }
}

# Controller VM
resource "azurerm_linux_virtual_machine" "controller" {
  name                = "px4-controller"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.controller_vm_size
  admin_username      = var.admin_username

  network_interface_ids = [
    azurerm_network_interface.controller.id,
  ]

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts-gen2"
    version   = "latest"
  }

  custom_data = base64encode(templatefile("${path.module}/controller-setup.yml", {
    controller_ip = azurerm_public_ip.controller.ip_address
  }))

  tags = {
    Environment = "Controller"
  }
}

# Agent VMs
resource "azurerm_network_interface" "agents" {
  count               = var.agent_count
  name                = "agent-${count.index}-nic"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_linux_virtual_machine" "agents" {
  count               = var.agent_count
  name                = "px4-agent-${count.index}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = var.agent_vm_size
  admin_username      = var.admin_username

  network_interface_ids = [
    azurerm_network_interface.agents[count.index].id,
  ]

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts-gen2"
    version   = "latest"
  }

  custom_data = base64encode(templatefile("${path.module}/agent-setup.yml", {
    controller_ip = azurerm_public_ip.controller.ip_address
    agent_index   = count.index
  }))

  tags = {
    Environment = "Agent"
    Index       = count.index
  }
}

# Outputs
output "controller_public_ip" {
  value = azurerm_public_ip.controller.ip_address
}

output "controller_private_ip" {
  value = azurerm_network_interface.controller.private_ip_address
}

output "agent_private_ips" {
  value = azurerm_network_interface.agents[*].private_ip_address
}

output "resource_group_name" {
  value = azurerm_resource_group.main.name
}
