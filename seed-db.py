
from datetime import datetime
import json
from pprint import pprint
import random
from zoneinfo import ZoneInfo
import mysql.connector
import os


dbconfig = {
    "host": os.getenv("MYSQL_HOST", "percona"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "testpassword"),
    "database": os.getenv("MYSQL_DATABASE", "speedtest"),
    "port": os.getenv("MYSQL_PORT", "33306"),
}

# for every 24 normal tickets maybe a couple of others
types= ['normal'] * 24 + ['guest','crew','vip']

# distribution for the start of an evening
statusses= ['created'] * 5 + ['downloaded'] * 20 + ['used'] * 2 + ['returned', 'expired']

RECORDS = 250_000
BLOCK_SIZE = 10000

drop = "drop table if exists barcodes;"

ddl= """
CREATE TABLE `barcodes` (
  `barcode_id` int unsigned NOT NULL AUTO_INCREMENT,
  `batch_id` int unsigned NOT NULL,
  `barcode` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `type` enum('normal','guest','crew','vip') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'normal',
  `status` enum('created','downloaded','used','returned','expired') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'created',
  `UsedOn` datetime DEFAULT NULL,
  `UsedOnTZ` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CreateTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `UpdateTime` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`barcode_id`),
  UNIQUE KEY `barcodes` (`barcode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
"""

def get_type():
    return random.choice(types)

def get_status():
    return random.choice(statusses)

def get_barcode(size = 6):
    return bytearray(random.getrandbits(8) for _ in range(size)).hex()

query = 'INSERT INTO barcodes (batch_id,barcode,type,status,UsedOn,UsedOnTZ) VALUES(%s, %s, %s, %s, %s, %s)'

barcodes=[]


with mysql.connector.connect(**dbconfig) as cnx, cnx.cursor() as cur:
    print("Dropping table...")
    cur.execute(drop)
    print("Creating table...")
    cur.execute(ddl)
    data = []
    batch_id = 1
    idx = 0
    done = 0
    current_batch_size = 1
    for item in range(RECORDS):
        status = get_status()
        barcode= get_barcode()
        barcodes.append(barcode)
        if status in ['used','returned']:
            date = datetime.now(tz=ZoneInfo("Europe/Amsterdam"))
            data.append((batch_id, barcode, get_type(), status, date,"Europe/Amsterdam"))
        else:
            data.append((batch_id, barcode, get_type(), status, None, None))
        idx += 1
        if idx == current_batch_size:
            idx = 0
            current_batch_size = random.randint(1,6)
            batch_id +=1

        if len(data) >= BLOCK_SIZE:
            done += len(data)
            print(f"Inserting block with {len(data)} items (cumulative {done})...")
            cur.executemany(query, data)
            data=[]
            
            print(f"Generating next block...")
    
    # final block
    if len(data) >= BLOCK_SIZE:
        done += len(data)
        print(f"Inserting final block with {len(data)} items (cumulative {done})...")
        cur.executemany(query, data)
    print(f"Committing transaction...")
    cnx.commit()
    

print("Writing barcodes to 'k6/shared/barcodes.json'")
with open('k6/shared/barcodes.json', 'w') as barcode_file:
    json.dump(barcodes, barcode_file)
