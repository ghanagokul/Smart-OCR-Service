# -----------------------------
# 1. Build React App with Vite
# -----------------------------
    FROM node:20-alpine AS build
    WORKDIR /app
    
    # Copy dependency definitions
    COPY package.json package-lock.json vite.config.js ./
    RUN npm ci --silent
    
    # Copy application source
    COPY src ./src
    COPY index.html ./
    
    # Build the app
    RUN npm run build
    
    # -----------------------------
    # 2. Serve with NGINX
    # -----------------------------
    FROM nginx:1.27-alpine
    
    # Copy built static files
    COPY --from=build /app/dist/ /usr/share/nginx/html/
    
    # Expose HTTP port
    EXPOSE 80
    
    # Start NGINX
    CMD ["nginx", "-g", "daemon off;"]
    