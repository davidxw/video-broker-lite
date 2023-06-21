# build environment
FROM node:19-alpine as build
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY ./app /app
RUN yarn install && yarn build

# production environment
FROM nginx:1.23-alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]