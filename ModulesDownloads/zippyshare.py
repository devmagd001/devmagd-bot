from requests import get
from user_agent import generate_user_agent

def uptodown(url):
    TEXT = str(get(url, headers={'user-agent': generate_user_agent()}).content)
    

    for i in TEXT.split(r"document.getElementById(\'dlbutton\').href    = "):
        if '.rar' in i:
            DIRECT_LINK = 'https://www67.zippyshare.com' + i.split(r'";\n')[0]
            
            print(DIRECT_LINK)
            
    print(TEXT.index('67967'))

uptodown('https://www72.zippyshare.com/v/TFNHMsZP/file.html')