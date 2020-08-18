#!/bin/bash

mkdir -p content
pip install -r requirements.txt
python ./openshift_versions/cmd/versions.py
cp index.html content/
