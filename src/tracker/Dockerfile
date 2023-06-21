FROM python:3.7-slim-buster

RUN pip install -U pip
COPY requirements.txt .

RUN pip install -r requirements.txt

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 dnsutils -y

COPY app/ /app

# Set the working directory
WORKDIR /app

# Run the app.py with 
CMD ["python", "-u", "app.py"]