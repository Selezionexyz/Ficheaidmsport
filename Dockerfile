# Dockerfile pour déploiement Render
# Multi-stage build : Frontend React + Backend FastAPI

# ===== ÉTAPE 1: Build du Frontend React =====
FROM node:20-alpine AS frontend-build

# Installation des dépendances système pour le build
RUN apk add --no-cache python3 make g++

# Configuration du répertoire de travail
WORKDIR /app/frontend

# Copie des fichiers de configuration des dépendances
COPY frontend/package.json ./package.json
COPY frontend/yarn.lock ./yarn.lock

# Installation des dépendances Node.js avec timeout étendu
RUN yarn install --network-timeout 600000

# Copie du code source frontend
COPY frontend/ ./

# Build de production React
RUN yarn build

# ===== ÉTAPE 2: Setup Backend Python =====
FROM python:3.11-slim AS backend

# Installation des dépendances système pour Python
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Configuration du répertoire de travail
WORKDIR /app

# Copie et installation des dépendances Python
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source backend
COPY backend/ ./backend/

# Copie du build frontend depuis l'étape précédente
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Configuration des variables d'environnement
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8001

# Exposition du port
EXPOSE 8001

# Commande de démarrage pour Render
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8001"]