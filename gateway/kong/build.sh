#!/bin/sh

# Source the .env file to load environment variables
if [ -f version.env ]; then
  . version.env
fi

# Check that envvars loaded (EXT_KONG_VERSION and EXT_KONG_IMAGE)
if [ -z "$EXT_KONG_VERSION" ] || [ -z "$EXT_KONG_IMAGE" ]; then
  echo "ERROR: version.env file not found or missing required variables"
  exit 1
fi

# Build the docker-kong-oidc image
cd docker-kong-oidc
./build.sh
cd ..

# Set the Docker image name
DOCKER_IMAGE="local/$EXT_KONG_IMAGE:$EXT_KONG_VERSION"

# Build the local image
docker build -t $DOCKER_IMAGE .

# If repo envvar is set and is not empty, tag and push the image
if [ -n "$EXT_KONG_REPO" ]; then
  docker tag $DOCKER_IMAGE $EXT_REPO/$EXT_KONG_IMAGE:$EXT_KONG_VERSION
  docker push $EXT_REPO/$EXT_KONG_IMAGE:$EXT_KONG_VERSION
fi