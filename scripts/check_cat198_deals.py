import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

webhook = "https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm/"

def call_b24(method, params=None):
    url = webhook + method
    if params:
        data = json.dumps(params).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

deals = call_b24("crm.deal.list.json", {
    "filter": {"CATEGORY_ID": 198},
    "order": {"ID": "DESC"},
    "select": ["*"],
    "limit": 3
})

print("Recent deals in Category 198:")
for d in deals.get('result', []):
    print(f"\nDeal ID: {d.get('ID')} - Title: {d.get('TITLE')} - Stage: {d.get('STAGE_ID')}")
    for k, v in d.items():
        if k.startswith('UF_') and v:
            print(f"  {k}: {v}")
