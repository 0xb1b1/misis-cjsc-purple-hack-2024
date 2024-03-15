FROM node:18-alpine

WORKDIR /app

COPY . /app

# hadolint ignore=DL3016
RUN npm install -g pnpm --global-dir=/usr/local/lib/pnpm && \
    pnpm install && \
    pnpm run build && \
    npm add serve -g

EXPOSE 3000

CMD ["npm", "run", "serve"]
