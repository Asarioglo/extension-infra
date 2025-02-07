#!/usr/bin/env python3

from invoke import task, MockContext
from contextlib import contextmanager
import sys
import os
import pytest
import shutil

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
KONG_CONFIG_DIR = os.path.join(PROJECT_ROOT, "gateway/kong/kong.yml")
DEVOPS_DIR = os.path.join(PROJECT_ROOT, "devops")
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")
VERBOSE = True

@contextmanager
def tmp_file(path: str, content: str):
    """
    Creates a tmp file, yields, then removes it
    Expects relative paths
    """
    path = os.path.join(PROJECT_ROOT, path)
    debug(f"Creating a temporary file at {path}")
    try:
        with open(path, 'w') as f:
            f.write(content)
            f.close()
        debug("file created, yielding")
        yield
    finally:
        debug(f"Cleaning up file {path}")
        try: os.remove(path)
        except Exception: pass
        
def to_abs(path: str):
    return os.path.join(PROJECT_ROOT, path)
        
@contextmanager
def repl_file(path: str, content: str):
    """
    Replaces the contents of the file, yields, then brings them back
    Expects relative path
    """
    debug(f"Replacing contents of file at {path} with \n{content}")
    path = os.path.join(PROJECT_ROOT, path)
    orig_content = None
    try:
        with open(path, 'r+') as f:
            orig_content = f.read()
            f.truncate(0)
            f.write(content)
            f.close()
        yield
    finally:
        if orig_content is not None:
            with open(path, 'w') as f:
                f.truncate(0)
                f.write(orig_content)
                f.close()
        

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
    test_envs = (
        "# This is a test comment\n"
        "TEST_GET_ENV_1=test_variable_1\n"
        "# another test comment\n"
        "TEST_GET_ENV_2=!@#$%^&*()\n"
    )
    with repl_file(".env", test_envs):
        assert get_env("TEST_GET_ENV_1") == "test_variable_1"
        assert get_env("TEST_GET_ENV_2") == "!@#$%^&*()"

def join_files(paths: list, out_file_path: str):
    content = ""
    for path in paths:
        abs_path = os.path.join(PROJECT_ROOT, path)
        with open(abs_path, 'r') as f:
            content += f.read()
            content += "\n"
            f.close()
        
    abs_out_path = to_abs(out_file_path)
    with open(abs_out_path, 'w') as f:
        f.truncate(0)
        f.write(content)
        f.close()
        
def test_join_files():
    f1 = "Content line 1\nContent Line 2"
    f2 = "CONTENT line 3\nContent Line 4"
    try:
        with tmp_file("__tmp1", f1):
            with tmp_file("__tmp2", f2):
                join_files(["__tmp1", "__tmp2"], "__tmp3") 
                assert os.path.exists(to_abs("__tmp3"))
                # With override
                join_files(["__tmp1", "__tmp2"], "__tmp3")
                with open(to_abs("__tmp3")) as f:
                    actual = f.read()
                    expected = f"{f1}\n{f2}\n"
                    debug(f"Comparing {actual} WITH {expected}")
                    assert actual == expected 
    finally:
        os.remove("__tmp3")

    
def get_envs(envfile_path: str):
    """Env file path is relative to root directory"""
    debug("loading an env file")

    vars = {}
    with open(os.path.join(PROJECT_ROOT, envfile_path)) as f:
        line = f.readline().strip()
        while line:
            parts = line.split("=")
            if len(parts) == 2:
               vars[parts[0]] = parts[1].strip()
            line = f.readline()
            
    return vars

def test_get_envs():
    test_envs = (
        "# This is a test comment\n"
        "TEST_GET_ENV_1=test_variable_1\n"
        "# another test comment\n"
        "TEST_GET_ENV_2=!@#$%^&*()\n"
    )
    debug("Sterting test test_get_envs. Creating temp file")
    with tmp_file("__test_envs.env", test_envs):
        debug("Temp file created, reading envs")
        envs = get_envs("__test_envs.env")
        assert envs["TEST_GET_ENV_1"] == "test_variable_1"
        assert envs["TEST_GET_ENV_2"] == "!@#$%^&*()"
    
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
