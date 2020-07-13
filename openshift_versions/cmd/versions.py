# Copyright 2020 Eduardo Minguez.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import re
import requests
import sys

import jinja2


URL = "https://api.openshift.com/api/upgrades_info/v1/graph"
# https://github.com/openshift/cincinnati-graph-data/tree/master/channels
CHANNELS = ["fast-4.", "stable-4.", "candidate-4."]
HEADERS = {"accept": "application/json"}
EMPTYRESPONSE = {'nodes': [], 'edges': []}

TITLE = "OpenShift 4 latest versions per channel"
DISCLAIMER = """
<p>This is an unofficial source</p>
<p>Please visit <a href="https://www.openshift.com/">the official site</a> to get more information and latest news about OpenShift</p>
"""


# https://hackersandslackers.com/extract-data-from-complex-json-python/
def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results


# https://stackoverflow.com/a/4836734/491522
def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def get_versions():
    versions = {}
    failed = 0
    minor = 1
    # If 3 empty responses, meaning, no channels for the minor release
    while failed < len(CHANNELS):
        failed = 0
        for channel in CHANNELS:
            params = {"channel": channel + str(minor)}
            try:
                page = requests.get(URL, params, headers=HEADERS)
                page.raise_for_status()
            except requests.exceptions.HTTPError as err:
                raise SystemExit(err)
            if page.json() != EMPTYRESPONSE:
                versions[channel + str(minor)] = natural_sort(extract_values(page.json(), 'version'))[-1]
            else:
                failed += 1
        minor += 1
    return dict(sorted(versions.items(), key=lambda kv: kv[0]))


def main():
    # Open the previous json data
    try:
        with open('versions.json') as json_file:
            previous = json.load(json_file)
    except Exception:
        previous = {}

    currentvers = get_versions()

    # If the results are the same, do nothing
    if previous == currentvers:
        sys.exit("Dupe")
    # Otherwise, save the file for next execution and continue
    else:
        with open('versions.json', 'w') as json_file:
            json_file.write(json.dumps(currentvers, sort_keys=True))

    templates_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
    file_loader = jinja2.FileSystemLoader(templates_dir)
    env = jinja2.Environment(loader=file_loader)
    template = env.get_template('index.template')

    latest = currentvers[list({k: v for k, v in currentvers.items() if k.startswith('fast-')})[-1]]

    with open('index.html', 'w') as output_file:
        output_file.write(template.render(title=TITLE, versions=currentvers, latest=latest, disclaimer=DISCLAIMER))


if __name__ == "__main__":
    main()
