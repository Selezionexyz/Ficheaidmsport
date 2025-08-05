# Multi-stage Dockerfile for Render deployment
FROM node:20-alpine as frontend-builder

# Set working directory for frontend build
WORKDIR /app/frontend

# Copy package files and install dependencies
COPY frontend/package.json frontend/yarn.lock ./

# Enable corepack (built-in package manager for Node.js 20)
RUN corepack enable
RUN yarn install --frozen-lockfile --production=false

# Copy frontend source code
COPY frontend/ ./

# Set production environment variables
ENV NODE_ENV=production
ENV CI=false
ENV GENERATE_SOURCEMAP=false

# Build the frontend
RUN yarn build

# Python backend stage
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements and install dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ backend/

# Copy built frontend from the frontend-builder stage
COPY --from=frontend-builder /app/frontend/build /app/frontend/build

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

# Expose port
EXPOSE 8001

# Health check
RUN echo '#!/bin/bash\n\
echo "🚀 Starting Product Sheets Generator..."\n\
echo "📋 System check:"\n\
echo "  - Python version: $(python --version)"\n\
echo "  - Current directory: $(pwd)"\n\
echo "📁 File verification:"\n\
if [ -d "/app/frontend/build" ]; then\n\
    echo "  ✅ Frontend build present ($(ls -1 /app/frontend/build | wc -l) files)"\n\
else\n\
    echo "  ❌ Frontend build missing"\n\
    exit 1\n\
fi\n\
if [ -f "/app/backend/server.py" ]; then\n\
    echo "  ✅ Backend server.py present"\n\
else\n\
    echo "  ❌ Backend server.py missing"\n\
    exit 1\n\
fi\n\
echo "🌐 Starting FastAPI server on port 8001..."\n\
exec uvicorn backend.server:app --host 0.0.0.0 --port 8001 --log-level info\n\
' > /app/start.sh && chmod +x /app/start.sh

# Start the application
CMD ["/app/start.sh"]