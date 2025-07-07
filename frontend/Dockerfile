# Stage 1: Build the React/Vite app
FROM node:20-slim AS builder

WORKDIR /app
COPY . .

RUN npm install
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy build output from previous stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Replace default nginx config
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

