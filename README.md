For converting the library files from venv to requirement.txt:

    venv\Scripts\pip freeze > requirements.txt

To view the website #does not work (the application has database and render doesn't support docker-compose)
>> https://my-stock-dashboard.onrender.com

for activating the venv:
    
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

    .\venv\Scripts\activate

For pulling the docker image and deploying the application:
1. install docker and verify by:

    docker --version
    docker compose version

2. Deployment:
a. docker image pulling:

    docker pull saketh1809/stock-app:latest
    docker run -d \
        -p 5000:5000 \
        -e MONGO_URI="mongodb://localhost:27017/stockdb" \
        --name stock-app-backend \
        saketh1809/stock-app:latest

b. using docker-compose.yaml (complete setup):

    git clone https://github.com/saketh1809/stock-project.git
    cd stock-app
    docker compose up -d

Key Note Points:

1. if requirement.txt has pywin32 then remove or conditionally skip pywin32

2. Switch to the Correct Docker Context, verify it by:

    docker context ls

the output shoud be:

    default             moby
    desktop-linux *     moby

The asterisk * means Docker is now using the correct Linux engine (the same one used by Docker Desktop).

steps implemented:

steps for deploying the docker image:

    docker build -t stock-app-backend .
    docker compose up

