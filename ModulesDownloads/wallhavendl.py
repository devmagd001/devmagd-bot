from time import sleep
from requests import get
from os.path import join


def wallhavendl(url: str, num: int):
    """
    La función `wallhavendl` es una función de Python que toma una URL y un número como entrada y
    devuelve una lista de enlaces de imágenes del sitio web.

    :param url: El parámetro `url` es la URL de un sitio web que contiene fondos de pantalla
    :param num: El parámetro `num` representa la cantidad de enlaces de fondo de pantalla que desea
    recuperar
    :return: La función `wallhavendl` devuelve una lista de enlaces de imágenes.
    """
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'

    if num > 11:
        if 'tag' in url:
            url = "https://wallhaven.cc/search?q=id%3A" + \
                str(url.split('/')[-1]) + "&page=1"

        elif 'search' in url and 'page' not in url:
            url = "https://wallhaven.cc/search?q=id%3A" + \
                str(url.split(':')[-1]) + "&page=1"

    if 'page=' in url and num > 11:
        print(url)
        links = []
        total = int(url.split('page=')[-1]) + int(num) // 11
        for i in range(int(url.split('page=')[-1]), total + 1):
            sleep(3)
            resp = get(url.split('page=')[
                       0] + f'page={i}', headers={'user-agent': user_agent}).text
            for i in resp.split('preview" href="'):
                if i.startswith('http'):
                    imgLink = i.split(' ')[0].replace('"', '')
                    sleep(0.50)
                    imgFile = get(imgLink, headers={
                                  'user-agent': user_agent}).text
                    for i in imgFile.split('wallpaper" src="'):
                        if i.startswith('http'):
                            img = i.split(' ')[0].replace('"', '')
                            links.append(img)
                            if len(links) == num:
                                return links

    else:
        resp = get(url, headers={'user-agent': user_agent}).text
        links = []
        for i in resp.split('preview" href="'):
            if i.startswith('http'):
                imgLink = i.split(' ')[0].replace('"', '')
                imgFile = get(imgLink, headers={
                              'user-agent': user_agent}).text
                for i in imgFile.split('wallpaper" src="'):
                    if i.startswith('http'):
                        img = i.split(' ')[0].replace('"', '')
                        links.append(img)
                        if num > 0:
                            if len(links) == num:
                                return links
        return links
