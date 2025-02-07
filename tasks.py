#!/usr/bin/env python3

from invoke import task, MockContext
from contextlib import contextmanager
import sys
import os
import pytest

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
KONG_CONFIG_DIR = os.path.join(PROJECT_ROOT, "gateway/kong/kong.yml")
DEVOPS_DIR = os.path.join(PROJECT_ROOT, "devops")
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")
VERBOSE = True

def debug(log: str):
    if VERBOSE:
        print(f"\n")
        print(log)

def get_python_executable():
    return sys.executable

def get_version():
    with open(os.path.join(PROJECT_ROOT, "VERSION.txt")) as f:
        return f.read().strip()
    
def copy_if_not_exists(c, source, dest):
    """Parameters are relative paths"""

    dest_path = os.path.join(PROJECT_ROOT, dest)
    source_path = os.path.join(PROJECT_ROOT, source)
    if not os.path.exists(source_path):
        raise Exception(f"Source file {source_path} not found.")
    
    if not os.path.exists(dest_path):
        c.run(f"cp {source_path} {dest_path}")
        
def get_env(varname: str):
    debug(f"Retrieving config: {varname}")
    with open(ENV_FILE) as f:
        line = f.readline()
        while line:
            parts=line.split("=")
            if parts[0] == varname:
                return parts[1].strip()
            line = f.readline()
    
    return None

def test_get_env():
    envvar = "EXT_KONG_IMAGE_NAME"
    val = get_env(envvar)
    assert val == "local/bosca-infra/kong"

    
def get_envs(envfile_path: str):
    """Env file path is relative to root directory"""
    debug("loading an env file")

    vars = {}
    with open(os.path.join(PROJECT_ROOT, envfile_path)) as f:
        line = f.readline()
        while line:
            parts = line.split("=")
            if len(parts) == 2:
               vars[parts[0]] = parts[2]
            
    return vars
    
@contextmanager
def change_dir(new_dir):
    old_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(old_dir)

@contextmanager
def replace_kong_config(env_file: str, c):
    c.run(f"cp {KONG_CONFIG_DIR}/kong.yml {KONG_CONFIG_DIR}/kong.yml.bak")
    c.run("chmod +x ./devops/populate-config.sh")
    try:
        c.run("rm -f {KONG_CONFIG_DIR}/kong.yml")
        c.run((
            "./devops/populate-config.sh "
            f"{KONG_CONFIG_DIR}/kong.yml.tpl "
            f"{env_file} "
            f"{KONG_CONFIG_DIR}/kong.yml"
        ))
        yield
    finally:
        c.run(f"cp {KONG_CONFIG_DIR}/kong.yml.bak {KONG_CONFIG_DIR}/kong.yml")
        
@contextmanager
def compile_env(src_env_file: str, dynamic_params: dict):
    with open(src_env_file) as f:
        env_text = f.read()

    env_text += "\n\n"

    for key, value in dynamic_params.items():
        if key in env_text:
            env_text = env_text.replace(f"{key}=", f"{key}={value}")
        else:
            env_text += f"{key}={value}\n"
        
    tmp_file_name = src_env_file + ".tmp"
    try:
        with open(tmp_file_name, "w") as f:
            f.write(env_text)
        yield tmp_file_name
    finally:
        os.remove(tmp_file_name)
        # print("Removing: ", tmp_file_name)


# @task
# def test_compile(c):
#     with compile_env("devops/config/dev.env", {"FOO": "bar", "EXT_KONG_IMAGE_TAG": "test"}) as env_file:
#         with open(env_file) as f:
#             print(f.read())

            
@task
def copy_dev_env(c):    
    copy_if_not_exists(c, "devops/config/dev.env", ".env")
    
@task
def dev(c):
    copy_if_not_exists(c, "devops/config/dev.env", ".env")

    # Let's generate some certificates, if we need the ofc.
    key_name = get_env("EXT_KONG_CERT_KEY_NAME") 
    cert_name = get_env("EXT_KONG_CERT_NAME")
    hostname = get_env("EXT_HOSTNAME")
    file_location = get_env("EXT_KONG_HOST_CERT_DIR")
    
    if None in [file_location, cert_name, key_name, hostname]:
        raise Exception((
            "Config file misformed. Do you have EXT_KONG_CERT_KEY_NAME, "
            "EXT_KONG_CERT_NAME, EXT_KONG_HOST_CERT_DIR, and EXT_HOSTNAME "
            "in it?"
        ))

    file_location = os.path.join(PROJECT_ROOT, "gateway/kong", file_location)
    key_location = os.path.join(file_location, key_name)
    cert_location = os.path.join(file_location, cert_name) 

    if not os.path.exists(file_location):
        os.mkdir(file_location)
    
    if not os.path.exists(cert_location) or not os.path.exists(key_location):
        debug("Certificate and key not found, attempting to create them")
        try:
            debug("Checking if mkcert is installed")
            c.run("command mkcert")
            debug(f"mkcert exists, creating certificate for {hostname} at\n{key_location}\nand {cert_location}")
            debug(f"mkcert {hostname} -cert-file {cert_location} -key-file {key_location}")
            c.run(f"mkcert -cert-file {cert_location} -key-file {key_location} {hostname}")
            print("Certificates generated successfully!")
        except Exception as e:
            print((
                "\nCan not proceed without certificates. "
                "Tried to generate them for you using mkcert, but it is not "
                "installed, requires super user access, or some other issue (above) \n"
                "Either fix the issue and run this again, or generate your "
                "own certificates and run this again. Note that certificate "
                "and key names should match the .env configuration.\n" 
            ))
    else:
        print(f"Using certificates in {file_location}")
        
    c.run("cp devops/config/dev.env .env")
    c.run("docker-compose up --build --force-recreate -d")
    c.run("my")
    c.run("my echo 3006")
    
# @task
# def test(c):
#     c.run(os.path.join(DEVOPS_DIR, "__tests__/populate-config.test.sh"))
# ask
