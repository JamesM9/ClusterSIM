output "controller_public_ip" {
  description = "Public IP address of the controller"
  value       = azurerm_public_ip.controller.ip_address
}

output "controller_private_ip" {
  description = "Private IP address of the controller"
  value       = azurerm_network_interface.controller.private_ip_address
}

output "agent_private_ips" {
  description = "Private IP addresses of the agent VMs"
  value       = azurerm_network_interface.agents[*].private_ip_address
}

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "controller_ssh_command" {
  description = "SSH command to connect to the controller"
  value       = "ssh ${var.admin_username}@${azurerm_public_ip.controller.ip_address}"
}

output "web_interface_url" {
  description = "URL of the web interface"
  value       = "http://${azurerm_public_ip.controller.ip_address}"
}

output "api_url" {
  description = "URL of the API"
  value       = "http://${azurerm_public_ip.controller.ip_address}:8000"
}
