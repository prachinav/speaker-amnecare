FROM python:3.8.0-buster

# Install dependencies
COPY requirements.txt .
RUN pip install gunicorn

RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential gcc 
                                        libsndfile1
RUN pip install -r requirements.txt

# Copy our source code
COPY . .

# Run the application
CMD ["python", "app.py"]
