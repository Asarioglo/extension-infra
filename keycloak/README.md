# Keycloak Server Configuration

## Configure behind Proxy

1. Change Realm frontend url to 
    ```
    <https>://<public hostname>/<proxy_path>
    ```
    For example, in my local development setup
    ```
    https://carvantage.host.my/auth
    ```