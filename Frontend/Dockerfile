#################
###build stage###
#################

FROM node:18-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./

# Install dependencies (including dev dependencies for build)
RUN npm ci

COPY . .

# Set build-time environment variable for API URL (for browser access)
ENV VITE_API_BASE=http://localhost:8000

RUN npm run build

######################
###production stage###
######################

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

COPY <<EOF /etc/nginx/conf.d/default.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
