variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "px4-cloud-sim"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

variable "controller_vm_size" {
  description = "Size of the controller VM"
  type        = string
  default     = "Standard_B2s"
}

variable "agent_vm_size" {
  description = "Size of the agent VMs"
  type        = string
  default     = "Standard_B4ms"
}

variable "agent_count" {
  description = "Number of agent VMs"
  type        = number
  default     = 2
}

variable "admin_username" {
  description = "Admin username for VMs"
  type        = string
  default     = "azureuser"
}

variable "ssh_public_key" {
  description = "SSH public key for VM access"
  type        = string
}

variable "controller_domain" {
  description = "Domain name for the controller (optional)"
  type        = string
  default     = ""
}

variable "ssl_certificate_path" {
  description = "Path to SSL certificate file (optional)"
  type        = string
  default     = ""
}

variable "ssl_private_key_path" {
  description = "Path to SSL private key file (optional)"
  type        = string
  default     = ""
}
