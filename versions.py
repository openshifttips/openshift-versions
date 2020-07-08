import requests, json, os, re

LATESTVERSION = 5
URL = "https://api.openshift.com/api/upgrades_info/v1/graph"
# https://github.com/openshift/cincinnati-graph-data/tree/master/channels
CHANNELS = ["fast-","stable-","candidate-"]
HEADERS = { "accept": "application/json"}
EMPTYRESPONSE = {'nodes': [], 'edges': []}

versions = {}

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
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

for minor in range(0, LATESTVERSION):
    for channel in CHANNELS:
        params = { "channel": channel+"4."+str(minor) }
        try:
          page = requests.get(URL,params,headers=HEADERS)
          page.raise_for_status()
        except requests.exceptions.HTTPError as err:
          raise SystemExit(err)
        if page.json() != EMPTYRESPONSE:
            versions[channel+"4."+str(minor)] = natural_sort(extract_values(page.json(), 'version'))[-1]
print(json.dumps(versions, indent=4, sort_keys=True))
