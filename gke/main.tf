provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}
data "google_client_config" "provider" {}

resource "google_compute_subnetwork" "custom" {
  name          = "test-subnetwork"
  ip_cidr_range = "10.2.0.0/16"
  region        = var.region
  network       = google_compute_network.custom.id
  secondary_ip_range {
    range_name    = "services-range"
    ip_cidr_range = "172.16.0.0/22"
  }
  secondary_ip_range {
    range_name    = "pod-ranges"
    ip_cidr_range = "192.168.0.0/22"
  }
}

resource "google_compute_network" "custom" {
  name                    = "test-network"
  auto_create_subnetworks = false
}

resource "google_container_cluster" "my_vpc_native_cluster" {
  name               = "my-vpc-native-cluster"
  location           = var.region
  initial_node_count = 1
  
  network    = google_compute_network.custom.id
  subnetwork = google_compute_subnetwork.custom.id
  resource_labels = {}
  ip_allocation_policy {
    cluster_secondary_range_name  = "services-range"
    services_secondary_range_name = google_compute_subnetwork.custom.secondary_ip_range.1.range_name
  }
}

provider "kubernetes" {
  host  = "https://${google_container_cluster.my_vpc_native_cluster.endpoint}"
  token = data.google_client_config.provider.access_token
  cluster_ca_certificate = base64decode(
    google_container_cluster.my_vpc_native_cluster.master_auth[0].cluster_ca_certificate,
  )
}

provider "helm" {
  kubernetes {
    host     = "https://${google_container_cluster.my_vpc_native_cluster.endpoint}"
    token = data.google_client_config.provider.access_token
    cluster_ca_certificate = base64decode(
      google_container_cluster.my_vpc_native_cluster.master_auth[0].cluster_ca_certificate,
  )
  }
}

resource "helm_release" "my-chart" {
  name       = "my-chart"
  chart      = "../eurchart"
  values = ["${file("../eurchart/values.yaml")}"]
}

data "kubernetes_service" "my-chart-eurchart" {
  metadata {
    name = "my-chart-eurchart"
  }
}

