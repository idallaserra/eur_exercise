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
    # let's print CPU information
    print("="*40, "CPU Info", "="*40)
    # number of cores
    print("Physical cores:", psutil.cpu_count(logical=False))
    print("Total cores:", psutil.cpu_count(logical=True))
    # CPU frequencies
    cpufreq = psutil.cpu_freq()
    print(f"Max Frequency: {cpufreq.max:.2f}Mhz")
    print(f"Min Frequency: {cpufreq.min:.2f}Mhz")
    print(f"Current Frequency: {cpufreq.current:.2f}Mhz")
    # CPU usage
    print("CPU Usage Per Core:")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        print(f"Core {i}: {percentage}%")
    #return f"Total CPU Usage: {psutil.cpu_percent()}% \n Test"
    print("="*40, "Memory Information", "="*40)
    # get the memory details
    svmem = psutil.virtual_memory()
    print(f"Total: {get_size(svmem.total)}")
    print(f"Available: {get_size(svmem.available)}")
    print(f"Used: {get_size(svmem.used)}")
    print(f"Percentage: {svmem.percent}%") 
    print("="*20, "SWAP", "="*20)
    # get the swap memory details (if exists)
    #swap = psutil.swap_memory()
    #print(f"Total: {get_size(swap.total)}")
    #print(f"Free: {get_size(swap.free)}")
    #print(f"Used: {get_size(swap.used)}")
    #print(f"Percentage: {swap.percent}%")
    print("="*40, "System Information", "="*40)
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

