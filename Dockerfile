# Dockerfile final pour Render - SOLUTION COMPLÈTE
FROM python:3.11-slim

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Installation de Node.js 18 LTS (stable)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Configuration du répertoire de travail
WORKDIR /app

# ÉTAPE 1: Build du Frontend
COPY frontend/package.json frontend/package.json
WORKDIR /app/frontend
RUN npm install --legacy-peer-deps

# Copie du code frontend et build
COPY frontend/ .
RUN npm run build

# ÉTAPE 2: Setup Backend
WORKDIR /app
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code backend
COPY backend/ backend/

# Variables d'environnement pour production
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

# Exposition du port Render
EXPOSE 8001

# Script de démarrage avec gestion des erreurs
RUN echo '#!/bin/bash\n\
echo "🚀 Démarrage de l\'application..."\n\
echo "📁 Vérification des fichiers:"\n\
ls -la /app/frontend/build/ || echo "❌ Build frontend manquant"\n\
ls -la /app/backend/ || echo "❌ Backend manquant"\n\
echo "🌐 Démarrage du serveur sur port 8001..."\n\
exec uvicorn backend.server:app --host 0.0.0.0 --port 8001\n\
' > /app/start.sh && chmod +x /app/start.sh

# Commande de démarrage
CMD ["/app/start.sh"]