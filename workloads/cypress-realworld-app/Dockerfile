FROM node:16

WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn install

COPY . .

ENV NODE_ENV=development

RUN yarn db:seed:dev && \
    yarn predev:cognito:ci


#EXPOSE 3000
EXPOSE 3001

#CMD [ "yarn", "dev" ]
CMD [ "yarn", "start:api:watch" ]