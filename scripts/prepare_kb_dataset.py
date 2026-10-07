# -*- coding: utf-8 -*-
import os
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

KB_DIR = r"C:\Users\anali\Downloads\files"
docs = []

for fname in sorted(os.listdir(KB_DIR)):
    if fname.startswith("KB-") and fname.endswith(".md"):
        fpath = os.path.join(KB_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse YAML frontmatter if present
        title = fname
        kb_id = fname[:6]
        keywords = []
        systems = []
        
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                body = parts[2].strip()
                
                # Extract fields
                for line in frontmatter.split("\n"):
                    line = line.strip()
                    if line.startswith("titulo:"):
                        title = line.split(":", 1)[1].strip().strip('"').strip("'")
                    elif line.startswith("id:"):
                        kb_id = line.split(":", 1)[1].strip().strip('"').strip("'")
                    elif line.startswith("palavras_chave:"):
                        raw_kw = line.split(":", 1)[1].strip()
                        keywords = re.findall(r'["\']([^"\']+)["\']', raw_kw)
                    elif line.startswith("sistemas:"):
                        raw_sys = line.split(":", 1)[1].strip()
                        systems = re.findall(r'["\']([^"\']+)["\']', raw_sys)
            else:
                body = content
        else:
            body = content

        # Construct full searchable text with title and context header
        header_text = f"# {kb_id} - {title}\nSistemas: {', '.join(systems)}\nPalavras-chave: {', '.join(keywords)}\n\n"
        full_text = header_text + body
        
        docs.append({
            "kb_id": kb_id,
            "title": title,
            "systems": ", ".join(systems),
            "keywords": ", ".join(keywords),
            "source": fname,
            "text": full_text
        })

print(f"Total de documentos processados: {len(docs)}")
for d in docs:
    print(f"  [{d['kb_id']}] {d['title']} ({len(d['text'])} chars)")

out_json = r"C:\mundial-n8n-automations\scripts\kb_docs_for_ingestion.json"
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(docs, f, ensure_ascii=False, indent=2)
print(f"Dataset gravado em: {out_json}")
