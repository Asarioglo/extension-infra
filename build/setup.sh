#!/usr/bin/env bash

current_dir=$(dirname "${BASH_SOURCE[0]}")
requirements_file="$current_dir"/bash-requirements.txt
dev_requirements_file="$current_dir"/bash-dev-requirements.txt

echo "Processing requirements file $requirements_file..."
cat "$requirements_file"

pkg_manager="apt-get"
if ! command -v "$pkg_manager" &>/dev/null; then
    pkg_manager="brew"
    if ! command -v "$pkg_manager" &>/dev/null; then
        pkg_manager="yum"
        if ! command -v "$pkg_manager" &>/dev/null; then
            echo "ERROR: No package manager found"
            exit 1
        fi
    fi
fi

install() {
    echo "Checking for requirements in $1..."
    while IFS= read -r package; do
        echo "Checking if $package is installed..."
        if ! command -v "$package" &>/dev/null; then
            echo "Installing $package..."
            "$pkg_manager" install "$package"
            # Add installation logic here, e.g., using apt, brew, or yum
        else
            echo "$package is already installed."
        fi
    done < "$1"
}

install "$requirements_file"
install "$dev_requirements_file"