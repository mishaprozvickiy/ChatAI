#!/bin/bash

# чтобы при ошибке остановилось выполнение скрипта
set -e

# скачиваем docker, docker compose
sudo apt install ca-certificates curl -y
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y
sudo usermod -aG docker $USER

# деплоим
cd ChatAI
cp backend/.env.example backend/.env
SECRET_KEY=$(openssl rand -hex 32)
sed -i "s/JWT_SECRET_KEY=SECRET_KEY/JWT_SECRET_KEY=${SECRET_KEY}/" backend/.env
docker compose up -d --build