import json
import jwt  # PyJWT
import time
import requests

# ==== CHANGE THESE TO YOUR VALUES ====
integration_key = "33cafb67-e100-4cdd-92bb-694c38487083"
user_id = "a28302dc-e1cf-4cac-a4d8-083c1003e28e"
account_id = "4f0e0b88-1b27-4ae6-85c1-ca158fb449ae"
private_key_file = "private.key"  # file where you saved your DocuSign private key
auth_server = "account-d.docusign.com"  # sandbox
# =====================================

# Read your private key
with open(private_key_file, "r") as key_file:
    private_key = key_file.read()

# Create a JWT (JSON Web Token)
current_time = int(time.time())
expiry_time = current_time + 3600  # token valid for 1 hour

jwt_payload = {
    "iss": integration_key,
    "sub": user_id,
    "aud": auth_server,
    "iat": current_time,
    "exp": expiry_time,
    "scope": "signature impersonation"
}

jwt_token = jwt.encode(jwt_payload, private_key, algorithm="RS256")

# Step 1: Ask DocuSign for an access token
url = f"https://{auth_server}/oauth/token"
headers = {"Content-Type": "application/x-www-form-urlencoded"}
body = {
    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
    "assertion": jwt_token
}

response = requests.post(url, data=body, headers=headers)

if response.status_code == 200:
    access_token = response.json()["access_token"]
    print("\nYour ACCESS TOKEN is:\n")
    print(access_token)
    print("\nCopy this into your .env file as ACCESS_TOKEN.")
else:
    print("Error getting token:")
    print(response.text)
