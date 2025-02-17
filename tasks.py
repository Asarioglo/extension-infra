#!/usr/bin/env python3

from invoke import task, run
from collections.abc import Mapping
from contextlib import contextmanager
import sys
import os
import yaml
import dotenv

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
KONG_DIR = os.path.join(PROJECT_ROOT, "src/components/gateway/kong")
KONG_CONFIG_DIR = os.path.join(KONG_DIR, "config")
DEVOPS_DIR = os.path.join(PROJECT_ROOT, "devops")
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")
VERBOSE = True

def apps():
    appsdir = to_abs("apps")
    for approot in os.scandir(appsdir):
        if approot.is_dir():
            yield approot.path

def load_env(environment: str = "dev"):
    # Let's join all envvars from apps into one big-ass envvar. 
    # These envvars will come from the environment on prod
    app_env_file = None
    envfiles = [to_abs("devops/config/constants.env")]
    match environment:
        case "dev":
            envfiles.append(to_abs("devops/config/dev.env"))
            app_env_file = "dev.env"
        case "vm":
            envfiles.append(to_abs("devops/config/vm.env"))
            app_env_file = "vm.env"
        case _:
            raise Exception(f"Invalid environment: {environment}")
    for appdir in apps():
        envfiles.append(os.path.join(appdir, app_env_file))
 
    print(f"Concatenating {str(envfiles)}")
    join_files(envfiles, ".env")

    dotenv.load_dotenv()

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
    if varname in os.environ:
        return os.environ[varname]
    
    return None

def test__get_env():
    os.environ["TEST_GET_ENV_1"] = "test_variable_1"
    os.environ["TEST_GET_ENV_2"] = "!@#$%^&*()"
    
    assert get_env("TEST_GET_ENV_1") == "test_variable_1"
    assert get_env("TEST_GET_ENV_2") == "!@#$%^&*()"

def deep_merge_yaml(d1, d2):
    """
    Ok, maybe deep merge is a bit drastic
    """
    merged = {}
    keys_to_merge = ["services", "plugins", "_format_version"]

    for key in keys_to_merge:
        if key in d1 and key in d2:
            if isinstance(d1[key], Mapping) and isinstance(d2[key], Mapping):
                # Deep merge dictionaries
                merged[key] = deep_merge_dicts(d1[key], d2[key], keys_to_merge)
            elif isinstance(d1[key], list) and isinstance(d2[key], list):
                # Append lists (not merging dicts inside lists)
                merged[key] = d1[key] + d2[key]
            else:
                # Replace scalar values
                merged[key] = d2[key]
        elif key in d1:
            merged[key] = d1[key]
        elif key in d2:
            merged[key] = d2[key]

    return merged

def join_yaml_files(yml_paths: list):
    result = None
    for fpath in yml_paths:
        fpath_abs = to_abs(fpath)
        if os.path.exists(fpath_abs):
            with open(fpath_abs, 'r') as f:
                yml = yaml.safe_load(f)
                if result is None:
                    result = yml
                else:
                    result = deep_merge_yaml(result, yml)
    
    return result

def compile_kong_config():
    kong_files = [os.path.join(KONG_CONFIG_DIR, "root.yml")]
    for appdir in apps():
        if(os.path.exists(os.path.join(appdir, "kong.yml"))):
            kong_files.append(os.path.join(appdir, "kong.yml"))
    
    out = join_yaml_files(kong_files)
    out = replace_envs_in_string(yaml.dump(out, default_flow_style=False, sort_keys=False, indent=4))
    with open(os.path.join(KONG_CONFIG_DIR, "kong.yml"), 'w') as f:
        f.write(out)
        f.close()

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
    
def replace_envs_in_string(string: str):
    for key, value in os.environ.items():
        string = string.replace(f"${{{key}}}", value)
        
    return string

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

def setup_env(c, environment: str = "dev"):
    # Setup the environmental variables. 
    load_env(environment)

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

    file_location = os.path.join(KONG_DIR, file_location)
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

    compile_kong_config()
    
@task
def dev(c):
    setup_env(c, "dev")
    c.run("docker compose --profile dev up --build --force-recreate -d")
    with change_dir("src/api"):
        c.run("python manage.py runserver")

@task
def vm(c):
    setup_env(c, "vm")
    c.run("sudo docker compose --profile vm up --build --force-recreate -d", pty=True)
    
@task
def cleanup(c):
    dotenv.load_dotenv()
    if get_env("EXT_ENVIRONMENT") == "dev":
        c.run("docker compose --profile dev down")
    elif get_env("EXT_ENVIRONMENT") == "vm":
        c.run("sudo docker compose --profile vm down")
    else:
        raise Exception(f"Invalid environment: {get_env('EXT_ENVIRONMENT')}")

    datadir = get_env("KEYCLOAK_DB_DATA_DIR")
    # Let's not delete the root dir
    if os.path.exists(datadir) and len(datadir.split("/")) > 1:
        print(f"Deleting {datadir}")
        c.run(f"rm -rf {datadir}")

# @task
# def test(c):
#     c.run(os.path.join(DEVOPS_DIR, "__tests__/populate-config.test.sh"))
# ask
if __name__ == "__main__":
    pass

