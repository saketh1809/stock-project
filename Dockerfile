FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

# Expose Flask's default port
EXPOSE 5000

# Start Flask app
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]