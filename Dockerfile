# For more information, please refer to:
# 1. https://xaviervasques.medium.com/quick-install-and-first-use-of-docker-327e88ef88c7 
# 2. https://aka.ms/vscode-docker-python
# 3. https://github.com/docker-library/python/blob/33751272d8171cece37c59180c049ab77cf9c837/3.9/buster/slim/Dockerfile

# THE DOCKERFILE 
# -------------------- #

# FROM: Specifies the base image. 
# You can browse base images on Docker Hub.
FROM python:3.9-slim-buster

# ENV: Specifies the environment variables 
# which are specific to services. 

# Keeps Python from generating .pyc files in the container
# python-dont-write-by-the-code
ENV PYTHONDONTWRITEBYTECODE=1  

# Turns off buffering for easier container logging
# python-unbuffered 
ENV PYTHONUNBUFFERED=1

# COPY: Adds specified files.
# RUN: Runs a command in terminal inside the image.

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# WORKDIR: Creates and changes and the directory within
# the image to this specified path.
WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and 
# adds permission to access the /app folder
# For more info, please refer to: 
# https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# CMD: Takes the arguments for running the application.
# During debugging, this entry point will be overridden. 
# For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "-m", "python"]
