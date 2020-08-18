#!/bin/bash

mkdir -p content
pip install -r requirements.txt

# Versions.json and index.html will only be updated if there's a new version, older ones restored from cache
python ./openshift_versions/cmd/versions.py

# Always copy the resulting file to have a populated web server (even if it's the same)
cp index.html content/
[-f CNAME] && cp CNAME content/
