#!/bin/sh

python -m black src
python -m isort --sl -m 3 src
autoflake --remove-all-unused-imports -i -r src
flake8 src

