_format_version: "3.0"

services:
  - name: carvantage
    host: $CARVANTAGE_HOST_NAME
    port: $CARVANTAGE_HTTP_PORT
    routes:
      - name: carvantage-main-route
        paths:
          - /carvantage/
        strip_path: true
        methods:
          - GET
          - POST
          - PUT
          - DELETE
        protocols:
          - https
        https_redirect_status_code: 308 # permanent redirect
      - name: logout
        paths:
          - $CARVANTAGE_KONG_LOGOUT_PATH
        strip_path: false
        protocols:
          - https
        https_redirect_status_code: 308

  - name: keycloak-auth-carvantage
    host: keycloak
    port: 8080
    routes:
      - name: realm-route
        paths:
          - /auth
        strip_path: false
        protocols:
          - https
        https_redirect_status_code: 308

plugins:
  - name: oidc
    # https://github.com/revomatico/kong-oidc/blob/master/README.md
    service: carvantage
    config:
      client_id: $CARVANTAGE_KONG_KC_CLIENT_ID
      client_secret: $CARVANTAGE_KONG_KC_CLIENT_SECRET
      unauth_action: auth # deny (to return 401)
      discovery: $CARVANTAGE_KONG_KC_DISCOVERY_URL
      scope: openid

      logout_path: $CARVANTAGE_KONG_LOGOUT_PATH

      # After the plugin clears session (logout), redirect to KC to also clear session
      redirect_after_logout_uri: $CARVANTAGE_KONG_REDIRECT_AFTER_LOGOUT
      # must have redirect_after_logout_uri for this to work. Only "yes" works/
      post_logout_redirect_uri: $CARVANTAGE_KONG_POST_LOGOUT_REDIRECT
      redirect_after_logout_with_id_token_hint: "yes"

      # header_claims:
      #   - email
      #   - email_verified
      
      # These routes are public and don't need authentication
      ignore_auth_filters: /carvantage/assets,~/carvantage/api/(.*)/pub(.*)$

  - name: cors
    # https://docs.konghq.com/hub/kong-inc/cors/configuration/
    service: carvantage
    config: 
      origins:
        - localhost
      methods:
        - GET
        - POST
      headers:
        - Accept
        - Accept-Version
        - Content-Length
        - Content-MD5
        - Content-Type
        - Date
        - X-Auth-Token
      exposed_headers:
        - X-Auth-Token
      credentials: true
      max_age: 3600
      preflight_continue: false

  - name: rate-limiting
    # configuring this globally is not an option. Needs to be set route-by-route
    config:
      # https://docs.konghq.com/hub/kong-inc/rate-limiting/
      second: 1000
      minute: 1000
      hour: 1000
      policy: local
      fault_tolerant: true
      hide_client_headers: false
      redis_ssl: false
      redis_ssl_verify: false

  - name: ip-restriction
    config:
      allow:
        - 127.0.0.0/24
        - 192.168.0.0/16

# check out these plugins
# - bot-detection
# - proxy-cache
# - request-termination