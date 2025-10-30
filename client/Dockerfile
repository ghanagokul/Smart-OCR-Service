FROM node:20-alpine as build
WORKDIR /app
COPY package.json package-lock.json* vite.config.js /app/
RUN npm ci --silent
COPY src /app/src
COPY index.html /app/
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist/ /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]