FROM python:3.9-slim

WORKDIR app/

# install basics
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# get source code
RUN git clone https://github.com/pedroccorreia/neon-camera-store.git .

# Upgrade pip and install requirements
RUN pip3 install -U pip
RUN pip3 install -r requirements.txt

# Expose port you want your app on
EXPOSE 8080

# Run
ENTRYPOINT ["streamlit", "run", "Home.py", "--server.port=8080", "--server.address=0.0.0.0"]