import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Let's test with the RH webhook: https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/
webhook = 'https://b24-88dbfb.bitrix24.com.br/rest/244936/1jw82ol2jaf0ivve/'

def test_im_notify():
    url = f"{webhook}im.notify.system.add.json"
    payload = {
        "USER_ID": 32598,
        "MESSAGE": "🔔 [TESTE AGENTE RH] Teste de notificação de sistema para Eduardo Alaminos."
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            print("im.notify.system.add response:", resp.read().decode('utf-8'))
    except Exception as e:
        print("im.notify.system.add error:", e)

def test_im_message():
    url = f"{webhook}im.message.add.json"
    payload = {
        "DIALOG_ID": 32598,
        "MESSAGE": "🔔 [TESTE AGENTE RH] Teste de mensagem direta no chat privado para Eduardo Alaminos."
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            print("im.message.add response:", resp.read().decode('utf-8'))
    except Exception as e:
        print("im.message.add error:", e)

print("Testing notification delivery with RH Webhook user (244936)...")
test_im_notify()
test_im_message()
