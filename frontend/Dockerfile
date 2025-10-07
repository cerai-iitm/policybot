FROM node:20-alpine

ARG MODE=dev
ENV MODE=${MODE}

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy all necessary configuration files
COPY next.config.ts ./
COPY tsconfig.json ./
COPY tailwind.config.ts ./
COPY postcss.config.mjs ./
COPY eslint.config.mjs ./

# Copy source code and public assets
COPY src ./src
COPY public ./public

# Build for production if MODE is prod
RUN if [ "$MODE" = "prod" ]; then npm run build; fi

EXPOSE 3000

# Run appropriate command based on MODE
CMD if [ "$MODE" = "prod" ]; then \
    npm start; \
    else \
    npm run dev; \
    fi

