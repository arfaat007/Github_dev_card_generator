FROM nginx:alpine

# Copy the index.html as a template
COPY index.html /etc/nginx/templates/index.html.template

# Default environment variable
ENV BACKEND_URL=http://localhost:8080

# Nginx automatically processes templates in /etc/nginx/templates/ and outputs to /usr/share/nginx/html/
# It will replace ${BACKEND_URL} with the environment variable value.
EXPOSE 80
