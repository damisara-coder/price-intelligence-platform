terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  credentials = file("gcp-key.json")
  project     = var.project_id
  region      = var.region
}

resource "google_project_service" "bigquery" {
  service            = "bigquery.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "artifactregistry" {
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_bigquery_dataset" "prices" {
  dataset_id    = "ecommerce_prices"
  friendly_name = "E-commerce Price Intelligence"
  location      = "EU"
  depends_on    = [google_project_service.bigquery]
}

resource "google_bigquery_table" "raw_prices" {
  dataset_id = google_bigquery_dataset.prices.dataset_id
  table_id   = "products"
}

resource "google_artifact_registry_repository" "docker_repo" {
  location      = "europe-west1"
  repository_id = "price-intelligence"
  format        = "DOCKER"
  depends_on    = [google_project_service.artifactregistry]
}