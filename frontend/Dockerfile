# build stage
FROM node:24-slim AS build

WORKDIR /app

# install all dependencies before source
COPY package.json package-lock.json* .npmrc ./
RUN npm ci

COPY . .
RUN npm run build

# runtime stage
FROM node:24-slim

ENV NODE_ENV=production
WORKDIR /app

# install runtime dependencies only
COPY package.json package-lock.json* .npmrc ./
RUN npm ci --omit=dev && npm cache clean --force

# built app from the build stage
COPY --from=build /app/build ./build

USER node

ENV PORT=3000 \
    HOST=0.0.0.0
EXPOSE 3000

CMD ["node", "build"]
