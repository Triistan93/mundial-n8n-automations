import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

B24_WEBHOOK = 'https://b24-88dbfb.bitrix24.com.br/rest/61622/05wkhnplgtdtvaxm'
sql_url = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-search'

print("Buscando colaboradores ativos do Bitrix24...")
start = 0
total_synced = 0

while True:
    res = requests.get(f'{B24_WEBHOOK}/user.get', params={'ACTIVE': 'Y', 'start': start}).json()
    users = res.get('result', [])
    if not users:
        break
        
    values = []
    for u in users:
        uid = int(u.get('ID'))
        name = str(u.get('NAME') or '').replace("'", "''")
        last_name = str(u.get('LAST_NAME') or '').replace("'", "''")
        full_name = f"{name} {last_name}".strip().replace("'", "''")
        position = str(u.get('WORK_POSITION') or '').replace("'", "''")
        email = str(u.get('EMAIL') or '').replace("'", "''")
        values.append(f"({uid}, '{name}', '{last_name}', '{full_name}', '{position}', '{email}', NOW())")
        
    if values:
        upsert_sql = f"""
        INSERT INTO bitrix_users_cache (user_id, name, last_name, full_name, work_position, email, updated_at)
        VALUES {', '.join(values)}
        ON CONFLICT (user_id) DO UPDATE SET
            name = EXCLUDED.name,
            last_name = EXCLUDED.last_name,
            full_name = EXCLUDED.full_name,
            work_position = EXCLUDED.work_position,
            email = EXCLUDED.email,
            updated_at = NOW();
        """
        r_db = requests.post(sql_url, json={'query': upsert_sql}).json()
        total_synced += len(values)
        print(f"Sincronizados {total_synced} usuários...")

    if 'next' in res:
        start = res['next']
    else:
        break

print(f"\nTotal de colaboradores sincronizados no PostgreSQL: {total_synced}!")
q_count = "SELECT COUNT(*) as total FROM bitrix_users_cache;"
print("Contagem no banco:", requests.post(sql_url, json={'query': q_count}).json())
