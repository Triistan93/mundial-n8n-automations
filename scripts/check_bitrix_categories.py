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

# List Categories
cats = call_b24("crm.dealcategory.list.json")
print("=== DEAL CATEGORIES ===")
for c in cats.get('result', []):
    print(f"ID: {c.get('ID')} | Name: {c.get('NAME')}")

# Check stages for 198 and 152
for cat_id in [198, 152]:
    try:
        stages = call_b24("crm.dealcategory.stage.list.json", {"id": cat_id})
        print(f"\n=== STAGES FOR CATEGORY {cat_id} ===")
        for s in stages.get('result', []):
            print(f"  Stage ID: {s.get('STATUS_ID')} | Name: {s.get('NAME')}")
    except Exception as e:
        print(f"\nFailed to get stages for {cat_id}: {e}")

# Check deal userfields
fields = call_b24("crm.deal.userfield.list.json", {"filter": {"FIELD_NAME": "UF_CRM_1775845859336"}})
print("\n=== FIELD UF_CRM_1775845859336 ===")
for f in fields.get('result', []):
    print(f"ID: {f.get('ID')} | Label: {f.get('EDIT_FORM_LABEL')} | Type: {f.get('USER_TYPE_ID')}")
    if f.get('LIST'):
        for item in f.get('LIST', []):
            print(f"   Option ID: {item.get('ID')} | Value: {item.get('VALUE')}")

