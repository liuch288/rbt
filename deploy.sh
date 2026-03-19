#!/bin/bash

pip uninstall rbt -y
python3 setup.py bdist_wheel
pip install dist/rbt-0.9.2-py3-none-any.whl