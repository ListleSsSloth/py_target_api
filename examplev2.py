

from target_api_client import TargetApiClient


LEAD_TOKEN = "63d6d1ec-3b8e-40cd-85f5-c9e86eb42f87"
TARGET_TOKEN = 'hUzTEiT00XS42d7PzXjTkkqXmgYHp1hG60UZ4AOGU17InFVXBr2of5tleVQ8DiN19KvsHfFY6Q0rL1OHymxxPxMd0nNruKCQ1sv8LKNOqqNHM3VVBf0ee25zSN7g4ji8ZMygOPOPWCqcVCQbiigvQmOR1twZHWxGLRYKCoVFnJTBOtwvaX9PYYSXm9Zd85jMaVTxgiume46LEde'
SCOPES = ('read_ads', 'read_payments', 'create_ads')

client = TargetApiClient(
    client_id=LEAD_TOKEN,
    client_secret=TARGET_TOKEN,
    base_url="https://target.my.com",
    scopes=SCOPES
)

r = client.get_ok_lead(1)
print(r)
