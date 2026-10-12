# ==============================================================================
# DevOps Task Manager - Dockerfile
# Rubric 4.3 Demonstration: FROM, WORKDIR, COPY, RUN, EXPOSE, CMD
# ==============================================================================

# 1. Base Image: Lightweight Node.js Alpine image for optimized container size
FROM node:18-alpine

# 2. Set working directory inside the container
WORKDIR /app

# 3. Copy package definitions first to leverage Docker layer caching
COPY package*.json ./

# 4. Install production dependencies inside the container image
RUN npm install --production

# 5. Copy the rest of the application source code and assets
COPY . .

# 6. Expose port 3000 where our Node.js HTTP server listens
EXPOSE 3000

# 7. Default command executed when container starts
CMD ["node", "app.js"]
