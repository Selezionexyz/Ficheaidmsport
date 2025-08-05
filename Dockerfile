# Dockerfile FINAL pour Render - Version Node 20 + Optimisations
FROM python:3.11-slim

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Installation de Node.js 20 LTS (compatible avec react-scripts)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Vérification des versions
RUN echo "Node version:" && node --version && echo "NPM version:" && npm --version

# Configuration du répertoire de travail
WORKDIR /app

# ÉTAPE 1: Build du Frontend avec optimisations
COPY frontend/package.json frontend/package.json
WORKDIR /app/frontend

# Installation avec optimisation mémoire
ENV NODE_OPTIONS="--max-old-space-size=4096"
RUN npm install --legacy-peer-deps

# Variables d'environnement pour build stable
ENV CI=false
ENV GENERATE_SOURCEMAP=false

# Copie du code frontend et build
COPY frontend/ .
RUN npm run build

# Vérification du build
RUN ls -la build/ && echo "✅ Frontend build réussi"

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

# Script de démarrage avec diagnostic détaillé
RUN echo '#!/bin/bash\n\
echo "🚀 Démarrage de l'\''application Product Sheets Generator..."\n\
echo "📋 Diagnostic du système:"\n\
echo "  - Node.js version: $(node --version)"\n\
echo "  - Python version: $(python --version)"\n\
echo "  - Répertoire courant: $(pwd)"\n\
echo "📁 Vérification des fichiers:"\n\
if [ -d "/app/frontend/build" ]; then\n\
    echo "  ✅ Build frontend présent ($(ls -1 /app/frontend/build | wc -l) fichiers)"\n\
    ls -la /app/frontend/build/static/\n\
else\n\
    echo "  ❌ Build frontend manquant"\n\
    exit 1\n\
fi\n\
if [ -f "/app/backend/server.py" ]; then\n\
    echo "  ✅ Backend server.py présent"\n\
else\n\
    echo "  ❌ Backend server.py manquant"\n\
    exit 1\n\
fi\n\
echo "🔧 Variables d'\''environnement:"\n\
echo "  - MONGO_URL: ${MONGO_URL:0:20}..."\n\
echo "  - OPENAI_API_KEY: ${OPENAI_API_KEY:0:10}..."\n\
echo "  - GOOGLE_SEARCH_API_KEY: ${GOOGLE_SEARCH_API_KEY:0:10}..."\n\
echo "🌐 Démarrage du serveur FastAPI sur port 8001..."\n\
exec uvicorn backend.server:app --host 0.0.0.0 --port 8001 --log-level info\n\
' > /app/start.sh && chmod +x /app/start.sh

# Commande de démarrage
CMD ["/app/start.sh"]