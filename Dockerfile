# Build frontend
FROM node:20 as build-frontend
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Build backend
FROM python:3.12-slim-bookworm
WORKDIR /app
COPY ./capella_model_explorer ./capella_model_explorer
COPY ./pyproject.toml ./
COPY ./.git ./.git
RUN apt-get update && apt-get install -y git
RUN pip install .
COPY --from=build-frontend /app/dist/ ./frontend/dist/

# Expose the port the app runs in
EXPOSE 8000

# Start the application
CMD ["python", "-m", "capella_model_explorer.backend", "/model", "/templates"]