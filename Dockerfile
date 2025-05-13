ARG NODE_ENV=production
ARG NODE_VERSION=20-bullseye-slim

# Utiliser une image Node.js légère et optimisée pour la production
FROM node:${NODE_VERSION} AS builder

# Installer uniquement les outils nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier uniquement les fichiers nécessaires pour l'installation des dépendances
COPY package*.json /app/

# Installer les dépendances Node.js en mode production
RUN npm install

# Copier le reste des fichiers de l'application
COPY . /app/

# Construire l'application
RUN npm run build

# Étape de production
FROM node:${NODE_VERSION} AS runner

# Installer uniquement les outils nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Définir l'utilisateur non-root pour des raisons de sécurité
RUN useradd -m lecoffreuser

# Définir le répertoire de travail
RUN mkdir -p /app && \
    chown -R lecoffreuser:lecoffreuser /app
WORKDIR /app

USER lecoffreuser

COPY --from=builder --chown=lecoffreuser:lecoffreuser /app/.output/ /app/

# Copier le script d'entrée
COPY --from=builder --chown=lecoffreuser:lecoffreuser /app/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Exposer le port utilisé par l'application
EXPOSE 3000

# Définir le point d'entrée
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
