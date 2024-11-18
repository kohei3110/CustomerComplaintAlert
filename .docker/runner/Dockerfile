FROM ubuntu:20.04

ARG RUNNER_VERSION="2.320.0"
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update -y && \ 
    apt-get install -y curl expect jq tar git sudo && \
    apt-get upgrade -y && \ 
    useradd -m runner && \
    apt-get install -y libc6 && \
    apt-get install -y libglib2.0-0 && \
    apt-get install -y libnss3 && \
    apt-get install -y libnspr4 && \
    apt-get install -y libdbus-1-3 && \
    apt-get install -y libatk1.0-0 && \
    apt-get install -y libatk-bridge2.0-0 && \
    apt-get install -y libcups2 && \
    apt-get install -y libdrm2 && \
    apt-get install -y libxkbcommon0 && \
    apt-get install -y libxcomposite1 && \
    apt-get install -y libxdamage1 && \
    apt-get install -y libxfixes3 && \
    apt-get install -y libxrandr2 && \
    apt-get install -y libgbm1 && \
    apt-get install -y libpango-1.0-0 && \
    apt-get install -y libcairo2 && \
    apt-get install -y libasound2 && \
    apt-get install -y libatspi2.0-0 && \
    apt-get install -y libx11-xcb1 && \
    apt-get install -y libxcursor1 && \
    apt-get install -y libxi6 && \
    apt-get install -y libgtk-3-0 && \
    apt-get install -y libcairo-gobject2 && \
    apt-get install -y libgdk-pixbuf2.0-0 && \
    apt-get install -y libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxkbcommon-x11-0 libxcomposite1 libxrandr2 libgbm1 libpango-1.0-0 libpangocairo-1.0-0 libasound2 libxshmfence1

RUN curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

RUN apt-get update && \
    apt-get install -y apt-transport-https ca-certificates curl software-properties-common && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
    apt-get update && \
    apt-get install -y docker-ce docker-ce-cli containerd.io

# Add runner user to docker group
RUN getent group docker || groupadd docker && usermod -aG docker runner
RUN usermod -aG sudo runner
RUN echo "runner ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Create a script to start Docker daemon
RUN echo '#!/bin/bash\n\
/usr/bin/dockerd --host=unix:///var/run/docker.sock &' > /usr/local/bin/start-docker.sh && \
    chmod +x /usr/local/bin/start-docker.sh

RUN cd /home/runner && \ 
    mkdir actions-runner && \ 
    cd actions-runner && \
    curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz && \
    ls -l actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz && \
    tar xzf actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz || { echo "Failed to extract tar.gz file"; exit 1; }

RUN chown -R runner ~runner && \ 
    /home/runner/actions-runner/bin/installdependencies.sh

# Install Python 3.12
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.12 python3.12-venv python3.12-dev && \
    apt-get clean

COPY ./Scripts/start.sh start.sh

RUN chmod +x start.sh

USER runner

RUN /home/runner/actions-runner/config.sh --url https://github.com/koheisaito_microsoft/CustomerComplaintAlert --token A42QMQRF6TCVQ6M5XE7PVI3HHKY3C

ENTRYPOINT [ "./start.sh" ]