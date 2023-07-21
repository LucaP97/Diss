# Start from a base image
FROM nginx:alpine

# Copy static files to the web directory
COPY . /usr/share/nginx/html

# The port that this container will expose
EXPOSE 80

# Run Nginx (it's started in the base image)
CMD ["nginx", "-g", "daemon off;"]
