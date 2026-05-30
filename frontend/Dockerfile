# Stage 1: Build stage using Node
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package descriptors
COPY package*.json ./

# Install packages clean
RUN npm ci

# Copy the rest of the application source code
COPY . .

# Embed Vite build-time environment variables
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Build client production bundles
RUN npm run build

# Stage 2: Serve stage using Nginx
FROM nginx:1.25-alpine

# Copy built artifacts to Nginx docroot
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom server configuration for SPA routing fallback
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
