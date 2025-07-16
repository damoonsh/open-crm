# Connect to auth_microservice container with interactive shell
podman-compose down -v && podman system prune -af --volumes

podman exec -it auth_microservice /bin/sh

podman exec -it auth_microservice /bin/bash

podman exec -it shared_db psql -U db_user -d shared_db

curl -X POST http://localhost:8000/auth/register \ 
-H "Content-Type: application/json" \
-d '{
    "email": "test@example.com",
    "password": "your_password",
    "username": "testuser"
}'

curl -X POST http://localhost:8000/auth/register \
-H "Content-Type: application/json" \
-d '{"email":"test@example.com","password":"your_password","username":"testuser"}'

curl -X POST http://localhost:8000/auth/login \
-H "Content-Type: application/json" \
-d '{"email":"test@example.com","password":"your_password"}'