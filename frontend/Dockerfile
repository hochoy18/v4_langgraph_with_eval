FROM node:20-slim

WORKDIR /app

COPY package.json ./
RUN npm install --no-audit --no-fund

COPY . .

ENV NODE_ENV=development
EXPOSE 5173

CMD ["npm", "run", "dev"]