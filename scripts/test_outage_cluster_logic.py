# -*- coding: utf-8 -*-
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

url_db = 'https://sophia-n8nsophia.timft8.easypanel.host/webhook/kb-ti-search'

# 1. Insert 2 events for Mogi Guacu within last 10 minutes
q1 = """
INSERT INTO store_outage_events (store_name, category_theme, deal_id, created_at)
VALUES 
  ('Mogi Guaçu', 'CONNECTIVITY_NETWORK', 1403001, NOW() - INTERVAL '15 MINUTES'),
  ('Mogi Guaçu', 'CONNECTIVITY_NETWORK', 1403002, NOW() - INTERVAL '5 MINUTES');
"""
r1 = requests.post(url_db, json={'query': q1})
print("Insert status:", r1.status_code)

# 2. Test the exact Outage Cluster query used in n8n
q2 = """
WITH recent_events AS (
    SELECT COUNT(*) AS count_recent
    FROM store_outage_events
    WHERE store_name = 'Mogi Guaçu'
      AND category_theme = 'CONNECTIVITY_NETWORK'
      AND created_at >= NOW() - INTERVAL '30 MINUTES'
)
SELECT recent_events.count_recent,
       'Mogi Guaçu' AS store_name,
       'CONNECTIVITY_NETWORK' AS category_theme,
       1403468 AS deal_id
FROM recent_events;
"""
r2 = requests.post(url_db, json={'query': q2})
print("Cluster query status:", r2.status_code)
print("Result:", json.dumps(r2.json(), indent=2, ensure_ascii=False))

# 3. Clean up the test events
q3 = "DELETE FROM store_outage_events WHERE deal_id IN (1403001, 1403002);"
r3 = requests.post(url_db, json={'query': q3})
print("Cleanup status:", r3.status_code)
