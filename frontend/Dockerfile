FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build the application
ARG REACT_APP_API_URL=/api
ENV REACT_APP_API_URL=${REACT_APP_API_URL}
ENV NODE_ENV=production
RUN npm run build

# Production stage using NGINX
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy NGINX configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start NGINX
CMD ["nginx", "-g", "daemon off;"]
