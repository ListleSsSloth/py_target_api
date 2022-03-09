

from target_api_client import TargetApiClient


LEAD_TOKEN = "63d6d1ec-3b8e-40cd-85f5-c9e86eb42f87"
TARGET_TOKEN = '...'
SCOPES = ('read_ads', 'read_payments', 'create_ads')

client = TargetApiClient(
    client_id=LEAD_TOKEN,
    client_secret=TARGET_TOKEN,
    base_url="https://target.my.com",
    scopes=SCOPES,
    token=TARGET_TOKEN
)

r = client.get_ok_lead(1)
print(r)
