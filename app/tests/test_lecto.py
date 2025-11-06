import os
import requests


text = "tengo"
direction = "spanish_to_english"
src, target = ("es", "en")
payload = {"texts":[text], "to":[target], "from":src}
headers = {
    "content-type": "application/json",
    "x-rapidapi-key": "ce9fb4a224msh34e58574b6597f9p10b93fjsnfa28bbb8ebb4",
    "x-rapidapi-host": "lecto-translation.p.rapidapi.com",
    "accept-encoding": "gzip"
}
resp = requests.post("https://lecto-translation.p.rapidapi.com/v1/translate/text", json=payload, headers=headers)
print(resp.json())
