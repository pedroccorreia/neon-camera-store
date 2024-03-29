FROM python:3.9-slim


# install basics
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Continue with other script actions if the file exists or the user chose to continue
WORKDIR /app/


# TODO: make it work with arguments for a private github repo
# get source code 
# RUN git clone https://<username>:<personal_access_token>@github.com/pedroccorreia/neon-camera-store.git .
RUN git clone https://github.com/pedroccorreia/neon-camera-store.git .

# Move your yaml file to the deployment folder
COPY config.yaml .

# Upgrade pip and install requirements
RUN pip3 install -U pip
RUN pip3 install -r requirements.txt

# Expose port you want your app on
EXPOSE 8080

# Run
ENTRYPOINT ["streamlit", "run", "Home.py", "--server.port=8080", "--server.address=0.0.0.0"]