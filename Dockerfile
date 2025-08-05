# Ultra simple approach - build locally then copy
FROM node:18 as builder

WORKDIR /app
COPY frontend/package.json ./
RUN npm install --force
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install -r requirements.txt

COPY backend/ backend/
COPY --from=builder /app/build /app/frontend/build

ENV PYTHONPATH=/app

EXPOSE 8001

CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8001"]