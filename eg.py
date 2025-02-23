import json
import requests
headers = {
    "Content-Type": "application/json",
    "X-Master-Key": "$2a$10$zCxD0eePhaxSpav1iZtzzO41se.8HoND.wMVD5IYqeQpGX3QqYfai"
}

idURL = "https://api.jsonbin.io/v3/b/679255e6e41b4d34e47d86da"

upreq = requests.get(idURL, headers= headers).json()["record"]
print(upreq);
upreq["rc"].append(123)
requests.put(idURL, headers=headers, json=upreq)
upreq = requests.get(idURL, headers= headers).json()["record"]
print(upreq);
# # ele = upreq["rc"].pop(0)
# # print(ele)
# # upreq2 = requests.put(idURL, headers= headers, json = upreq)

# respids = responseof2["ids"]
# respids.append(1235456789)
# print(respids)
# responseof2["ids"] = respids
# print(responseof2)
# response2 = requests.put(idURL, headers= headers, json = responseof2)

