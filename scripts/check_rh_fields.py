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

fields = call_b24("crm.deal.userfield.list.json")
print(f"Total deal userfields: {len(fields.get('result', []))}")
for f in fields.get('result', []):
    name = f.get('FIELD_NAME')
    label = f.get('EDIT_FORM_LABEL', {}).get('br', '') if isinstance(f.get('EDIT_FORM_LABEL'), dict) else str(f.get('EDIT_FORM_LABEL'))
    tipo = f.get('USER_TYPE_ID')
    # Filter for fields related to RH, curriculo, vaga, candidato, cidade
    keywords = ['rh', 'vaga', 'candidato', 'curr', 'recrut', 'cidade', 'unidade', 'experi']
    if any(k in name.lower() or k in label.lower() for k in keywords) or '1775845859336' in name:
        print(f"Field: {name} | Label: '{label}' | Type: {tipo}")
        if f.get('LIST'):
            for it in f.get('LIST')[:5]:
                print(f"   Opt {it.get('ID')}: {it.get('VALUE')}")
