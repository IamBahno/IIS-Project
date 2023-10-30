#!/usr/bin/env bash

function check_cmd {
    if ! command -v $1 &> /dev/null; then
        echo "$1 not found"
        exit 1
    fi
}

check_cmd python3
check_cmd pip

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

echo "Setup successful"
