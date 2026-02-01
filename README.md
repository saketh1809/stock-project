# Stock Dashboard (Flask + MongoDB + Docker)

This is a **Flask-based backend** application connected to **MongoDB**, containerized using **Docker** for easy deployment and portability. 

**Deployment using Render:**

>> https://my-stock-dashboard.onrender.com

> ❌ The hosted link below **does not work properly**.

The application depends on a database, and **Render does not support Docker Compose**, which is required for this setup.


## Local Development (Using Virtual Environment)

**Activate Virtual Environment (Windows):**

    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    .\venv\Scripts\activate

**Generate requirements.txt:**

    venv\Scripts\pip freeze > requirements.txt

-> If requirements.txt contains pywin32, remove it or conditionally skip it, as it causes issues in Linux/Docker environments.

**Docker Setup & Deployment:**

1. install docker and verify by:

        docker --version
        docker compose version

2. Switch to the Correct Docker Context, verify it by:
   
        docker context ls

the output shoud be:

    default             moby
    desktop-linux *     moby    

## Deployment:
**Option A: Pull and Run Docker Image**

1. docker image pulling:

        docker pull saketh1809/stock-app:latest

2. Run the Container:
   
        docker run -d \
            -p 5000:5000 \
            -e MONGO_URI="mongodb://localhost:27017/stockdb" \
            --name stock-app-backend \
            saketh1809/stock-app:latest

**Option B: Full Setup Using Docker Compose:**

1. Clone the Repository:
   
    git clone https://github.com/saketh1809/stock-project.git
    cd stock-app

2. Start the Application:
   
    docker compose up -d

This will:

- Build the backend image
- Start Flask backend
- Start MongoDB
- Connect all services automatically

**Building the Docker Image (Manual)**

steps for deploying the docker image:

    docker build -t stock-app-backend .
    docker compose up
    
The asterisk * means Docker is now using the correct Linux engine (the same one used by Docker Desktop).

--------------------------------------------------------------------------------------------------------
# Deploying using Google Cloud Services

**Cloud Shell + GKE + Docker + MongoDB**

**1. Clone the Repository:**
   
    git clone https://github.com/saketh1809/stock-project.git
    cd stock-project

**2. GKE Cluster:**

Creating a GKE cluster:

    gcloud container clusters create stock-cluster \
      --zone europe-west1-d \
      --num-nodes 1 \
      --scopes cloud-platform

Connect kubectl:

    gcloud container clusters get-credentials stock-cluster \
      --zone europe-west1-d

Verify:

    kubectl get nodes

**3.  Build & Push Docker Image (Cloud Build):**

Set variables:

    export PROJECT_ID=$(gcloud config get-value project)
    export IMAGE_NAME=stock-app

Build image:

     gcloud builds submit --tag gcr.io/$PROJECT_ID/$IMAGE_NAME

then confirm by:

    gcloud container images list

<img width="1919" height="1199" alt="image" src="https://github.com/user-attachments/assets/f10de17e-3939-42c4-a35f-5ee456dc7b7c" />


**4. Deploying on Kubernetes:**

MongoDB Deployment:

    kubectl apply -f mongo-deployment.yaml

Replace PROJECT_ID variable to your PROJECT_ID:

    sed -i "s/PROJECT_ID/$PROJECT_ID/g" app-deployment.yaml

App Deployment:

    kubectl apply -f app-deployment.yaml

**5. Getting the External IP:**

    kubectl get svc stock-app-service

**6. Verify Everything Is Running:**

    kubectl get pods
    kubectl logs deployment/stock-app
    kubectl logs deployment/mongodb

<img width="1918" height="1138" alt="Screenshot 2026-02-01 172659" src="https://github.com/user-attachments/assets/e323aa06-b2f1-46c6-bcc1-b99c2a3a3884" />

---------------------------------------------------------------------------------------------------------
**Cloud Build + Cloud Run**

Open Cloud Shell & set project:

    gcloud config set project YOUR_PROJECT_ID
    gcloud config set run/region us-central1

Enable required services (one-time):

    gcloud services enable \
      run.googleapis.com \
      artifactregistry.googleapis.com \
      cloudbuild.googleapis.com

Clone your repository:

    git clone https://github.com/saketh1809/stock-project.git
    cd stock-project

Create Artifact Registry (one-time):

    gcloud artifacts repositories create stock-repo \
      --repository-format=docker \
      --location=us-central1 \
      --description="Stock App Docker Repo"

Configure Docker authentication:

    gcloud auth configure-docker us-central1-docker.pkg.dev

Push image to Artifact Registry:

    docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/stock-repo/stock-app:latest

Build Docker image:

    docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/stock-repo/stock-app:latest .
  
Cloud Build:

    gcloud builds submit \
      --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/stock-repo/stock-app:latest



