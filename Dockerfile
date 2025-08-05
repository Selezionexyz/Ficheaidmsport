# Dockerfile optimisé pour Render
FROM python:3.11-slim

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Installation de Node.js 18 (plus stable avec babel-preset-react-app)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Configuration du répertoire de travail
WORKDIR /app

# Copie et installation des dépendances Python
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code backend
COPY backend/ ./backend/

# Copie du frontend et installation des dépendances
COPY frontend/ ./frontend/
WORKDIR /app/frontend
RUN npm install --legacy-peer-deps
RUN npm run build

# Retour au répertoire principal
WORKDIR /app

# Variables d'environnement
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Exposition du port
EXPOSE 8001

# Commande de démarrage
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8001"]