import requests
from my_log import log

host = 'http://127.0.0.1:5000'
r = requests.get(host)
log(r)


