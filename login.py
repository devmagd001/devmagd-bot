from pydrive2.auth import GoogleAuth




def login():
    gauth = GoogleAuth(settings_file='./conf.yaml')
    gauth.LocalWebserverAuth(launch_browser=True)


login()










