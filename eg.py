import json
import requests
# headers = {
#     "Content-Type": "application/json",
#     "X-Master-Key": "$2a$10$zCxD0eePhaxSpav1iZtzzO41se.8HoND.wMVD5IYqeQpGX3QqYfai"
# }

# idURL = "https://api.jsonbin.io/v3/b/679255e6e41b4d34e47d86da"

# # upreq = requests.get(idURL, headers= headers).json()["record"]
# # upreq["rc"].append(473)
# # ele = upreq["rc"].pop(0)
# # print(ele)
# # upreq2 = requests.put(idURL, headers= headers, json = upreq)

# respids = responseof2["ids"]
# respids.append(1235456789)
# print(respids)
# responseof2["ids"] = respids
# print(responseof2)
# response2 = requests.put(idURL, headers= headers, json = responseof2)

import requests
import json

def send_referral_data(email, password, referral_code, user_id):
    url = 'http://devapiv4.dealsdray.com/api/v2/user/email/referral'
    
    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        "email": email,
        "password": password,
        "referralCode": referral_code,
        "userId": user_id
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            print("Referral data sent successfully!")
            print("Response:", response.json())  # Print the response if needed
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Exception: {e}")
        return False

# Example usage:
send_referral_data("uhammedrafnasvk@gmail.com", "1234Rafnas", 12345678, "62a833766ec5dafd6780fc85")
