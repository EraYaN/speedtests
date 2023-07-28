from fastapi import FastAPI, HTTPException

import mysql.connector
import os

from typing import Union

app = FastAPI()

dbconfig = {
    "host": os.getenv("MYSQL_HOST", "percona"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "testpassword"),
    "database": os.getenv("MYSQL_DATABASE", "speedtest"),
    "port": os.getenv("MYSQL_PORT", "33306"),
}

dbpool = mysql.connector.pooling.MySQLConnectionPool(pool_name = "speedtest",
                                                      pool_size = 20, # docker file has 5 workers, 100 connections in total
                                                      **dbconfig)

@app.get("")
async def root():
    return "This is an API server, please use the correct client."
        
@app.get("/barcode/lookup")
async def scan(barcode: Union[str, None] = None):
    with dbpool.get_connection() as cnx, cnx.cursor(buffered=True) as cur:        
        cur.execute("select barcode_id as id, barcode as code, status as status from barcodes where barcode = %s", (barcode,))
        obj = cur.fetchone()
        if obj is not None:
            return {"id":obj[0],"code":obj[1],"status":obj[2]}
        else:
            raise HTTPException(status_code=404, detail="Barcode not found")

