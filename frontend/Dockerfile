# Build stage: Build the Vite (React) application
FROM node:20-slim AS build-stage

WORKDIR /app

# Copy package management files
COPY package*.json ./

# Install Node.js dependencies
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Build the production files into the 'dist' folder
RUN npm run build

# Production stage: Serve the static files
FROM node:20-slim

WORKDIR /app

# We use the 'serve' utility to serve the built static content
RUN npm install -g serve

# Only copy over the production dist folder from the build-stage
COPY --from=build-stage /app/dist /app/dist

# Expose the frontend port (Vite default is often 5173)
EXPOSE 5173

# Serve the static build with history sub-directory support enabled (-s)
CMD ["serve", "-s", "dist", "-l", "5173"]
