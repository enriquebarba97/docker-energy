FROM node:16

WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn

COPY . .

ENV NODE_ENV=development

#EXPOSE 3000
EXPOSE 3001

#CMD [ "yarn", "dev" ]
CMD [ "yarn", "start:api:watch" ]