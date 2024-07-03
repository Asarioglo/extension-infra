# SSL Certificates

This directory is mounted on the kong docker container under `/usr/local/kong/certs`. By default the certificates are enabled and https is enforced on all endpoints.

## Local Certificates

Generate local ssl certificates to launch this process on a dev machine. Expected files:

- certificate.pem
- key.pem
