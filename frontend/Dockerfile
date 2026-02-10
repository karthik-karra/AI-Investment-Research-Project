# --- Stage 1: Build ---
FROM node:lts-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# --- Stage 2: Production ---
FROM nginx:stable-alpine as production-stage
# Copy the built files from Stage 1
COPY --from=build-stage /app/dist /usr/share/nginx/html
# Copy our custom Nginx config (created below)
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]