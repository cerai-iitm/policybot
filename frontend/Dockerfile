FROM node:20-alpine

ARG MODE=dev
ENV MODE=${MODE}

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code and config files
COPY src ./src
COPY public ./public
COPY next.config.ts ./
COPY tsconfig.json ./
COPY tailwind.config.js ./

# If production, build the app
RUN if [ "$MODE" = "prod" ]; then npm run build; fi

EXPOSE 3000

# Run the appropriate command based on MODE
CMD if [ "$MODE" = "prod" ]; then npm start; else npm run dev; fi
