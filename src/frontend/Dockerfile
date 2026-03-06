FROM node:20-alpine

WORKDIR /app

COPY package.json .
COPY tsconfig.json .
COPY next.config.ts .
COPY next-env.d.ts .
COPY app ./app
COPY components ./components
COPY lib ./lib

RUN npm install

CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3000"]
