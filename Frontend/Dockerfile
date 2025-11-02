#################
###build stage###
#################

FROM node:18-alpine AS build

WORKDIR /app

# Install Python and build dependencies for native modules
RUN apk add --no-cache python3 make g++

COPY package.json package-lock.json ./

# Install dependencies with platform-specific rebuild
# Force npm to rebuild native modules for Alpine
RUN npm ci --platform=linuxmusl

COPY . .

# No need to set VITE_API_BASE - using relative URLs
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
