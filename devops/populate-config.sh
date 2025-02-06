#!/usr/bin/env bash

if [ -z "$1" ]; then
  echo "Usage: $0 <template-file>"
  exit 1
fi

if [ -z "$2" ]; then
    echo "Usage: $0 <template-file> <env-file>"
    exit 1
fi

_output_file=$(dirname "$1")/kong.yml

if [ -n "$3" ]; then
    _output_file=$3
fi

if [ -n "$2" ]; then
    . $2
    export $(grep -v '^#' "$2" | grep -v '^\s*$' | cut -d= -f1)
fi

if [ -f "$_output_file" ]; then
    echo "Output file $_output_file already exists. Overwriting..."
    rm -f "$_output_file"
fi

envsubst < "$1" > "$_output_file"
