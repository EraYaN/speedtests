from fastapi import FastAPI, HTTPException, Request

import mysql.connector
import os
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from typing import Union

app = FastAPI()

dbconfig = {
    "host": os.getenv("MYSQL_HOST", "server.e.dehaan.family"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "testpassword"),
    "database": os.getenv("MYSQL_DATABASE", "speedtest"),
    "port": os.getenv("MYSQL_PORT", "33306"),
}

dbpool = mysql.connector.pooling.MySQLConnectionPool(pool_name = "speedtest",
                                                      pool_size = 20, # docker file has 5 workers, 100 connections in total
                                                      **dbconfig)

templates = Jinja2Templates(directory="templates")

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
        
@app.get("/barcode/template", response_class=HTMLResponse)
async def scan(request: Request, barcode: Union[str, None] = None):
    with dbpool.get_connection() as cnx, cnx.cursor(buffered=True) as cur:        
        cur.execute("select barcode_id as id, barcode as code, status as status from barcodes where barcode = %s", (barcode,))
        obj = cur.fetchone()
        if obj is not None:
            return templates.TemplateResponse("barcode.html.j2", {"request": request, "barcode": {"id":obj[0],"code":obj[1],"status":obj[2]}})
        else:
            return templates.TemplateResponse("not-found.html.j2", {"request": request, "err": "no such barcode"})

