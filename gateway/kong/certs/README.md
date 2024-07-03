# SSL Certificates

This directory is mounted on the kong docker container under `/usr/local/kong/certs`. By default the certificates are enabled and https is enforced on all endpoints.

## Local Certificates

Generate local ssl certificates to launch this process on a dev machine. The certificates can be configured via the root `.env` file and the following 
envvars:

- **EXT_KONG_CERT_KEY_NAME** - The name of the private key
- **EXT_KONG_CERT_NAME** - The name of the certificate file

### Generating a local certificate on Mac

Use [MKCert](https://github.com/FiloSottile/mkcert) to make it easier. Also, MKCert install a local CA which tricks browsers into accepting the certificates.

1. Install MKCert
    ```bash
    brew install mkcert
    ```

2. Add a local Certificate Authority (do once)
    ```bash
    mkcert --install
    ```

3. Generate a certificate
    ```bash
     mkcert carvantage.host.my "*.host.my" localhost
    ```
    Generates certificates for the following hosts:
    
    - `carvantage.host.my`
    - `*.host.my`
    - `localhost`

## Container Mapping

As can be seen in `gateway/kong/docker-compose.yml`, the `gateway/kong/certs` directory is mapped to a volume inside Kong container at the path: 
```
/usr/local/kong/certs/
```

Configuring the certificate names in the root `.env` file should be sufficient 
for them to be picked up by Kong.