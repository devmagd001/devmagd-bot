from requests import get
from user_agent import generate_user_agent

def uptodown(url):
    if url.split('/')[-1] != 'descargar': url += '/descargar'
    r = get(url, headers={'user-agent': generate_user_agent()})
    return r.text.split('data-url=')[1].split('"')[1]