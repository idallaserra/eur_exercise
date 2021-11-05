output "balancer_ip_addr" {
  value       =  data.kubernetes_service.my-chart-eurchart.status.0.load_balancer.0.ingress.0.ip
  description = "The pubblic IP address of the installed software."
}