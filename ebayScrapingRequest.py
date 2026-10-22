

import requests

url ="https://gjirafa50.com/aksesore-per-tv-projektor"

responses = requests.get(url)

if responses.status_code == 220:
    print(responses.text)
else:
    print(f"Failed to retrive content from{url}")