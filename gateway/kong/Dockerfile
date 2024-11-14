FROM local/docker-kong-oidc:3.4.0-2

USER root

RUN apt-get update && apt-get install -y gettext

RUN mkdir -p /usr/local/kong/declarative/ && \
    chown -R kong:kong /usr/local/kong/declarative/

USER kong

# Copy configuration template and entrypoint script
COPY config/kong-template.yml /usr/local/kong/declarative/kong-template.yml
COPY config/kong.yml /usr/local/kong/declarative/kong.yml

COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# Switch to root to set the executable permission on entrypoint.sh
USER root
RUN chmod +x /usr/local/bin/entrypoint.sh

# Switch back to kong user
USER kong
