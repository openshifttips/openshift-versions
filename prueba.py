import requests, json, os, re

URL = "https://api.openshift.com/api/upgrades_info/v1/graph"
PARAMS = { "channel": "stable-4.4"}
HEADERS = { "accept": "application/json"}

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

try:
  page = requests.get(URL,PARAMS,headers=HEADERS)
  page.raise_for_status()
except requests.exceptions.HTTPError as err:
  raise SystemExit(err)

print(natural_sort(extract_values(page.json(), 'version'))[-1])

# values = page.json()
# latestversion = natural_sort(extract_values(values, 'version'))[-1]
# 
# lv = [v for v in values["nodes"] if v["version"] == latestversion]
# print(lv[-1])
# 
# print(latestversion)