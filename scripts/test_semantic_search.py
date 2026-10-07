# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-search"

queries = [
    "minha impressora não está imprimindo, ficou presa na fila",
    "o microwork travou e não consigo abrir a tela de faturamento",
    "preciso gerar intenção de venda no renave de uma moto vendida"
]

for q in queries:
    print("\n" + "="*70)
    print(f"QUERY: '{q}'")
    print("="*70)
    r = requests.post(url, json={"query": q})
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        results = r.json()
        print(f"Resultados retornados: {len(results) if isinstance(results, list) else 1}")
        if isinstance(results, list):
            for i, res in enumerate(results):
                doc = res.get("document", {}) or res
                meta = doc.get("metadata", {})
                page_content = doc.get("pageContent") or res.get("text") or ""
                print(f"  [Item {i+1}] KB: {meta.get('kb_id')} | Titulo: {meta.get('title')}")
                print(f"    Snippet: {page_content[:200].strip()}...")
        else:
            print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print("Erro:", r.text)
