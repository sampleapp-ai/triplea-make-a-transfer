import requests

BASE_URL = "https://api.uat.triple-a.io/api/fiat-payout/v1"
API_TOKEN = "triplea_api_token"  # replace
HEADERS = {"Accept": "application/json", "Authorization": f"Bearer {API_TOKEN}"}

# -----------------------------
# 1) Get supported banks / wallets
# -----------------------------
banks = requests.get(
    f"{BASE_URL}/banks",
    headers=HEADERS,
    params={"page": 1, "per_page": 1000},
).json()

# pick receiving_institution_id from banks response
# (adjust based on actual response shape)
bank_id = None
if isinstance(banks, dict) and "data" in banks and banks["data"]:
    bank_id = banks["data"][0]["id"]
elif isinstance(banks, list) and banks:
    bank_id = banks[0]["id"]

# -----------------------------
# 2) Create sender (individual)
# -----------------------------
sender_payload = {
    "external_id": "sender_external_id_001",
    "gender": "female",
    "last_name": "Zhang",
    "first_name": "James",
    "email": "jamse.zhang@example.com",
    "country_code": "USA",
    "province_state": "New York",
    "city": "New York City",
    "address": "1 Falcon Ave, California",
    "zip_code": "12345",
    "date_of_birth": "2019-08-24",
    "mobile_number": "+198766234",
    "identification_type": "RESIDENT_CARD",
    "identification_number": "S98765433X",
    "identification_issuer": "string",
    "identification_issue_date": "2022-01-01",
    "identification_expiry_date": "2022-09-01",
    "nationality": "SGP",
    "occupation": "FREELANCER",
    "remarks": "string",
    "role": "sender",
}
sender = requests.post(
    f"{BASE_URL}/individuals",
    headers={**HEADERS, "Content-Type": "application/json"},
    json=sender_payload,
)
sender.raise_for_status()
sender = sender.json()

sender_id = sender["id"]  # -> used later

# -----------------------------
# 3) Upload KYC doc (optional / conditional)
# -----------------------------
# If required, set file_path + uncomment.
file_path = "./PassportDoc"
doc_data = {
    "external_id": "kyc_external_id_001",
    "owner_id": sender_id,     # <- from Step 2
    "transfer_id": "",         # <- if you already have transfer_id
    "category": "identity_verification",
    "document_type": "passport",
}
with open(file_path, "rb") as f:
    doc = requests.post(
        f"{BASE_URL}/documents",
        headers=HEADERS,
        data=doc_data,
        files={"file": f},
    )
doc.raise_for_status()
doc = doc.json()

# -----------------------------
# 4) Create recipient (if different from sender)
# -----------------------------
recipient_payload = {
    **sender_payload,
    "external_id": "recipient_external_id_001",
    "role": "recipient",
}
recipient = requests.post(
    f"{BASE_URL}/individuals",
    headers={**HEADERS, "Content-Type": "application/json"},
    json=recipient_payload,
)
recipient.raise_for_status()
recipient = recipient.json()

recipient_id = recipient["id"]  # -> used later

# -----------------------------
# 5) Add destination account
# -----------------------------
destination_payload = {
    "type": "bank_account",
    "owner_id": recipient_id,                 # <- from Step 4
    "external_id": "dest_acct_external_001",
    "receiving_institution_id": bank_id,      # <- from Step 1
    "currency": "USD",
    "country_code": "USA",
    "alias": "Account 1",
    "account": {
        "recipient_name": "James Zhang",
        "recipient_identification_type": "NATIONAL_ID",
        "recipient_identification_number": "S98765433X",
        "recipient_nationality": "SGP",
        "recipient_address": "1 Falcon Ave, California",
        "recipient_province_state": "New York",
        "recipient_city": "New York City",
        "recipient_email": "jamse.zhang@example.com",
        "recipient_date_of_birth": "2019-08-24",
        "recipient_identification_issuer": "City hall",
        "recipient_identification_issue_date": "2019-08-24",
        "recipient_identification_expiry_date": "2025-08-24",
        "recipient_gender": "female",
        "recipient_zip_code": "12345",
        "mobile_number": "string",
        "account_name": "John Zuckerberg",
        "account_number": "9876543201",
        "account_type": "IBAN",
        "bank_account_type": "SAVINGS",
        "routing_type": "SWIFT-BIC",
        "routing_code": "string",
        "branch_code": "string",
        "bank_name": "string",
        "network": "network:local",
    },
    "intermediary_bank_details": {
        "routing_code_type": "SWIFT-BIC",
        "routing_code_value": "BKENGB2LXXX",
        "bank_name": "Bank of England",
        "address": {
            "address_line_1": "1600 Amphitheatre Parkway",
            "address_line_2": "Building 43",
            "city": "Mountain View",
            "state": "California",
            "zip_code": "94043",
            "country_code": "USA",
        },
    },
}
destination = requests.post(
    f"{BASE_URL}/destination-accounts",
    headers={**HEADERS, "Content-Type": "application/json"},
    json=destination_payload,
)
destination.raise_for_status()
destination = destination.json()

destination_account_id = destination["id"]  # -> used later

# -----------------------------
# 6) Prepare transfer (quotation)
# -----------------------------
transfer_payload = {
    "external_id": "transfer_external_001",
    "sender_id": sender_id,                       # <- from Step 3
    "recipient_id": recipient_id,                 # <- from Step 4
    "destination_account_id": destination_account_id,  # <- from Step 5
    "mode": "sending",
    "fee_mode": "excluded",
    "sending_amount": 0.01,
    "sending_currency": "BTC",
    "receiving_amount": 57.15,
    "receiving_currency": "USD",
    "purpose_of_remittance": "OTHER_FEES",
    "source_of_funds": "GIFT",
    "relationship": "FAMILY",
    "remarks": "string",
    "charge_type": "OUR",
}
transfer = requests.post(
    f"{BASE_URL}/transfers",
    headers={**HEADERS, "Content-Type": "application/json"},
    json=transfer_payload,
)
transfer.raise_for_status()
transfer = transfer.json()

transfer_id = transfer["id"]  # -> used later

# -----------------------------
# 7) Confirm transfer
# -----------------------------
confirm_payload = {
    "payment_method": "crypto_page",
    "success_url": "string",
    "cancel_url": "string",
    "amount_to_pay": 100,
    "cryptocurrency": "BTC",
    "card_id": "66f6e46c-f6a1-4af8-a1bd-49666bc01304",
}
confirmed = requests.post(
    f"{BASE_URL}/transfers/{transfer_id}/confirm",   # <- from Step 6
    headers={**HEADERS, "Content-Type": "application/json"},
    json=confirm_payload,
)
confirmed.raise_for_status()
confirmed = confirmed.json()

# -----------------------------
# Get transfer status (poll)
# -----------------------------
status = requests.get(
    f"{BASE_URL}/transfers/{transfer_id}",           # <- from Step 6
    headers=HEADERS,
)
status.raise_for_status()
status = status.json()

print("transfer_id:", transfer_id)
print("status:", status.get("status"), "sub_status:", status.get("sub_status"))
