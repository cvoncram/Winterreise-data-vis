# Two stages: the build needs the whole toolchain — Vite, TypeScript, Verovio,
# the type definitions — while the finished server needs none of it. Keeping
# them apart leaves the runtime image without any of the build dependencies.

FROM node:24-slim AS build

WORKDIR /app

# `npm ci` installs exactly what the lockfile records, which is what makes a
# build reproducible; it needs the dev dependencies, since Vite is one of them.
COPY package.json package-lock.json* .npmrc ./
RUN npm ci

COPY . .
RUN npm run build


FROM node:24-slim

ENV NODE_ENV=production
WORKDIR /app

# adapter-node emits a server that still resolves a few packages at run time,
# so the production dependencies have to be present — but only those.
COPY package.json package-lock.json* .npmrc ./
RUN npm ci --omit=dev && npm cache clean --force

COPY --from=build /app/build ./build

USER node

# adapter-node reads PORT and HOST; binding to all interfaces is required for
# the port to be reachable from outside the container.
ENV PORT=3000 \
    HOST=0.0.0.0
EXPOSE 3000

CMD ["node", "build"]
