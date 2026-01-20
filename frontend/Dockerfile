# Production Dockerfile (НЕ РАБОТАЕТ)
# FROM node:20-alpine AS builder
# WORKDIR /app
# COPY package*.json ./
# RUN npm ci
# COPY . .
# RUN npm run build

# FROM node:20-alpine AS runner
# WORKDIR /app
# ENV NODE_ENV production

# # 🔥 КОПИРУЕМ VOLUME ПЕРЕМЕННО
# COPY --from=builder /app/public ./public
# COPY --from=builder /app/.next ./.next
# COPY --from=builder /app/package.json ./
# RUN npm i next  # Для npm start

# EXPOSE 3000
# CMD ["npm", "start"]

FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
