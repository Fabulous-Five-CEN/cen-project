from dotenv import load_dotenv
load_dotenv()
import os
import requests


text = "tengo"
direction = "spanish_to_english"
src, target = ("es", "en")
payload = {"texts": [text], "to": [target], "from": src}

rapidapi_key = os.environ.get("RAPIDAPI_KEY")
if not rapidapi_key:
    raise RuntimeError("RAPIDAPI_KEY environment variable is not set")

rapidapi_host = os.environ.get("RAPIDAPI_HOST", "lecto-translation.p.rapidapi.com")
lecto_translate_url = os.environ.get(
    "LECTO_TRANSLATE_URL",
    "https://lecto-translation.p.rapidapi.com/v1/translate/text",
)

headers = {
    "content-type": "application/json",
    "x-rapidapi-key": rapidapi_key,
    "x-rapidapi-host": rapidapi_host,
    "accept-encoding": "gzip",
}
resp = requests.post(lecto_translate_url, json=payload, headers=headers)
print(resp.json())
