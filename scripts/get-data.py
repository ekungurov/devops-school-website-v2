import requests
import json
import pickle
import urllib3
import logging

urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

r = requests.get("https://swapi.dev/api/planets/", verify=False)
data_json = r.json()

with open("response.txt", "w") as f:
  f.write(r.text)

with open("response.json", "w") as f:
  f.write(json.dumps(data_json, indent=4))

with open("response.json.serialized", "wb") as f:
  pickle.dump(data_json, f)

print(r.status_code) 
