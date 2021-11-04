import psutil
import platform
import mariadb
import json
import os

from datetime import datetime
from flask import Flask

config = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT')),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWD')
}

def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, World!"

@app.route("/hostinfo")
def hostinfo():
    # get the memory details
    svmem = psutil.virtual_memory()
    # get the platform details
    uname = platform.uname()
    return f"Total CPU Usage: {psutil.cpu_percent()}%, Ram: Total - {get_size(svmem.total)}, Available - {get_size(svmem.available)}, Used - {get_size(svmem.used)}, Percentage - {svmem.percent}%, System: {uname.system}, Node Name: {uname.node},  Release: {uname.release}, Version: {uname.version}, Machine: {uname.machine}, Processor: {uname.processor}"

# route to return all people
@app.route('/dbinfo', methods=['GET'])
def dbinfo():
   # connection for MariaDB
   conn = mariadb.connect(**config)
   # create a connection cursor
   cur = conn.cursor()
   
   # execute a SQL statement
   cur.execute("select version ()")

   # serialize results into JSON
   row_headers=[x[0] for x in cur.description]
   rv = cur.fetchall()
   json_data=[]
   for result in rv:
        json_data.append(dict(zip(row_headers,result)))

   # execute a SQL statement
   cur.execute("show databases")

   # serialize results into JSON
   row_headers=[x[0] for x in cur.description]
   rv = cur.fetchall()
   json_data1=[]
   for result in rv:
        json_data1.append(dict(zip(row_headers,result)))

   # return the results!
   return f"{json.dumps(json_data)},{json.dumps(json_data1)}"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

