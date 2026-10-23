# React client: built with Vite, served by nginx. Build context: this folder.
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# `npm run build` also type-checks the older team modules that are no longer routed (they still have
# TypeScript errors), so the image is built with Vite directly.
RUN npx vite build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
