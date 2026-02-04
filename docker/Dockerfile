# Stage 1: Frontend Build
FROM node:20-alpine as frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Backend & Runtime
FROM python:3.10-slim
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends gcc libffi-dev && rm -rf /var/lib/apt/lists/*

# Install python deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend build artifacts
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copy startup script
COPY docker/start.sh .
RUN chmod +x start.sh

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["./start.sh"]
