#!/usr/bin/env bats

_test_dir="$(cd "$(dirname "${BATS_TEST_FILENAME}")" && pwd)"
_root_dir="$(cd "$_test_dir/../.." && pwd)"
# config_dir_relative="$TEST_DIR"/../config
# config_dir_full=$(cd $config_dir_relative && pwd)
# echo $config_dir_full
# config_file_template="$config_dir_full"/kong.yml.tpl

@test "Test that the populate script exists" {
    echo "Running test: $_test_dir"
    run ls -la $_test_dir/../populate-config.sh
    [ "$status" -eq 0 ]
}

@test "Test that a proper kong config file is generated form dev envvars" {
    template_path="$_root_dir/gateway/kong/config/kong.yml.tpl"
    env_file="$_root_dir/.env"
    output_file="$_test_dir/kong_out.yml"
    run $_test_dir/../populate-config.sh $template_path $env_file $output_file
    echo $output
    [ "$status" -eq 0 ]
    echo $output
    [ -f $output_file ]
    echo $output

    _correct=$(cat "$_root_dir"/gateway/kong/config/kong.yml)
    _output=$(cat $output_file)
    [ "$_correct" = "$_output" ]
}

teardown() {
    echo "Nothing to teardown"
    # rm -f $output_file
}
