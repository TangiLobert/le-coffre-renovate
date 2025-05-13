ARG NODE_ENV=production
ARG NODE_VERSION=20-bullseye-slim

# Use a lightweight and production-optimized Node.js image
FROM node:${NODE_VERSION} AS builder

# Install only the necessary tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy only the necessary files for dependency installation
COPY package*.json /app/

# Install Node.js dependencies in production mode
RUN npm install

# Copy the rest of the application files
COPY . /app/

# Build the application
RUN npm run build

# Production stage
FROM node:${NODE_VERSION} AS runner

# Install only the necessary tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security reasons
RUN useradd -m lecoffreuser

# Create the working directory and set permissions
RUN mkdir -p /app && \
    chown -R lecoffreuser:lecoffreuser /app
WORKDIR /app

# Switch to the non-root user
USER lecoffreuser

# Copy the built application from the builder stage
COPY --from=builder --chown=lecoffreuser:lecoffreuser /app/.output/ /app/
COPY --from=builder --chown=lecoffreuser:lecoffreuser /app/server/database/migrations /app/server/database/migrations

# Copy the entrypoint script
COPY --from=builder --chown=lecoffreuser:lecoffreuser /app/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Expose the port used by the application
EXPOSE 3000

# Define the entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
