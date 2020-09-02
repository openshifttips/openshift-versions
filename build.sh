#!/bin/bash

echo '=================== Previous versions.json ==================='
readlink -f versions.json
cat versions.json
pwd

pip install -r requirements.txt

# Versions.json and index.html will only be updated if there's a new version, older ones restored from cache

if python ./openshift_versions/cmd/versions.py; then
    echo '=================== New versions.json ==================='
    cat versions.json

    mkdir -p content
    # Copy the resulting file to have a populated web server (even if it's the same)
    cp index.html content/

    echo '=================== Publish to GitHub Pages ==================='
    cd ${SOURCE_FOLDER:=content}
    remote_repo="https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
    remote_branch=${GH_PAGES_BRANCH:=gh-pages}
    git init
    git remote add deploy "$remote_repo"
    git checkout $remote_branch || git checkout --orphan $remote_branch
    git config user.name "${GITHUB_ACTOR}"
    git config user.email "${GITHUB_ACTOR}@users.noreply.github.com"
    git add .
    echo -n 'Files to Commit:' && ls -l | wc -l
    timestamp=$(date +%s%3N)
    git commit -m "Automated deployment to GitHub Pages on $timestamp"
    git push deploy $remote_branch --force
    rm -fr .git
    cd ../
else
    echo "--- versions.json not updated ---"
fi
