# Multi-stage build pour Frontend + Backend
FROM node:18-alpine AS frontend-build

# Build du Frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
COPY frontend/yarn.lock ./
RUN yarn install --frozen-lockfile

COPY frontend/ .
RUN yarn build

# Backend Python
FROM python:3.11-slim AS backend

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Configuration du backend
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code backend
COPY backend/ ./backend/

# Copie du build frontend
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Variables d'environnement par défaut
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Exposition du port
EXPOSE 8001

# Commande de démarrage
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8001"]