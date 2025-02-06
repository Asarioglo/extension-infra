# extension-infra

Configuration and layout of an application environment deployment. The deployment is meant
to be a fully sufficient environment for a scalable application backend with OAuth2.0
authentication and user management out of the box. Currently this environment is meant to run
on a single machine with Kong as the API gateway and Keycloak as the authentication and use
management. 

## Development

This section contains instructions on setting up a local environment for experimentation
and development.

### Prerequisites

Locally, you will need the following tools to startup this setup and test/develop:

- Unix based host system (linux, macos)
- SSL Certificate generator / manager for Kong
- Docker & docker-compose
- Python with `invoke` installed
    - If you already have Python run `pip install -r requirements.txt`

### Quickstart

Run the following invoke command to configure and start the containers on a 
local dev environment

```bash
invoke dev
```

This will automate the configuration, ssl certs, image builds and container startup for you.
The default behavior will assume the local DNS name, ports, certificates, etc. 
Assumptions can be seen in `.env` file after invoke has run, or 
in `devops/config/dev.env` prior to the first run. 

Note you may still need to take actions after this. Look out for these:

- Install the local CA `mkcert -install` (may require root access)

### 1. Configuration

The difference between a development and production environment is in the 
`.env` file in the root of this repository. If it's missing, create one. 

To see the list of configurations and their defaults refer to `devops/dev.env` file.

### 2. Certificates

Kong API gateway is configured to always use SSL. A development (or non-secure)
option is not implemented in this repository. 

For a development machine where everything is running locally, you will need
to setup a complete chain according to IP and DNS protocols. The following 
should serve as a guide:

1. Select a DNS name for your local deployment `ex. domain.local.my`
1. Generate a self-signed certificate and a private key for this name
    - Use MacOS keychain or ssl tools on linux
1. Register the self signed keychain on your local machine as trusted keys
1. Modify the `Kong SSL Certificates` section of the environment file
1. Add the domain name to your hosts file to point to the ip:port of your
 deployment (in `.env` file)

### Keycloak (KC)

Keycloak configuration happens mostly after the system is already up and 
running, since the configuration is done using the Keycloak admin UI. It
is very important to configure KC properly for the Kong integration to 
work as needed.

To configure Keycloak follow these steps:

- Create a new Keycloak Realm
- 

## Build

