# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def run_sql(query):
    url = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-search'
    r = requests.post(url, json={'query': query})
    if r.status_code == 200:
        return r.json()
    else:
        print(f"Error {r.status_code}: {r.text}")
        return None

if __name__ == '__main__':
    q = sys.argv[1] if len(sys.argv) > 1 else "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
    res = run_sql(q)
    print(json.dumps(res, indent=2, ensure_ascii=False))
