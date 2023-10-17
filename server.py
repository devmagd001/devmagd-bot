import asyncio
import os
from aiohttp import web
from aiohttp import streamer
import jinja2
from tools import sizeof
from variables_globales import *
from os import mkdir
from queue import Queue as cola
from download_url import descargar_archivos_url, download_queues_url


SERVER = os.getenv("SERVER")
NAME_APP = os.getenv("NAME_APP")
"""==============Envio de el Archivo por HTTP================="""


@streamer
async def file_sender(writer, file_path=None):
    with open(file_path, "rb") as f:
        chunk = f.read(2**16)
        while chunk:
            await writer.write(chunk)
            chunk = f.read(2**16)


"""===============Servicio de Recepcion de la Peticion GET==================="""


async def download_file(request):
    """
    La función `download_file` es una función asíncrona que descarga un archivo especificado por los
    parámetros `file_name` y `route` y lo devuelve como una respuesta web.

    :param request: El parámetro `request` es un objeto que representa la solicitud HTTP realizada por
    el cliente. Contiene información como el método de solicitud, encabezados, parámetros de URL y el
    cuerpo de la solicitud. En este fragmento de código, se utiliza para extraer `file_name` y `route`
    de la ruta URL
    :return: un objeto web.Response.
    """
    file_name = request.match_info["file_name"]
    route = request.match_info["route"]

    file_path = os.path.join(route, file_name)
    headers = {
        "Content-disposition": "attachment; filename={file_name}".format(
            file_name=file_name
        ),
        "Accept-Ranges": "bytes",
        "Content-Type": f'{file_path.split("/")[-1].split(".")[-1]}',
        "Content-Length": str(os.path.getsize(file_path)),
    }

    if not os.path.exists(file_path):
        return web.Response(
            body="El Archivo  <{file_name}> No Existe".format(file_name=file_name),
            status=404,
        )

    return web.Response(body=file_sender(file_path=file_path), headers=headers)


# =====================================================================================================


async def submit_handler(request):
    global saved_messages
    global download_queues
    global CHOSE_FORMAT

    data = await request.post()
    url = data["fname"]
    if url.startswith("http"):
        msg_id = await app.get_users(BOT_USER)

        try:
            mkdir(BOT_USER)
        except:
            pass

        file_info = (msg_id.id, url, BOT_USER, BOT_USER, None)
        if BOT_USER in download_queues_url:
            download_queues_url[BOT_USER].put(file_info)
        else:
            queue = cola()
            queue.put(file_info)
            download_queues_url[BOT_USER] = queue
            await descargar_archivos_url(BOT_USER)

    oslist = []
    for i in os.listdir(f"./{BOT_USER}"):
        oslist.append((i, sizeof(os.path.getsize(f"./{BOT_USER}/{i}"))))

    data = {
        "files": oslist,
        "user": BOT_USER,
        "Cryptuser": BOT_USER,
        "enlace": f"https://{NAME_APP}.onrender.com/",
    }

    with open("./templates/usr.html", "r") as file:
        template = jinja2.Template(file.read())
        html = template.render(data)

    return web.Response(text=html, content_type="text/html")


# =====================================================================================================


async def index(request):
    """
    La función `index` lee un archivo de plantilla HTML, le pasa un parámetro, representa la plantilla
    con el parámetro y devuelve el HTML representado como una respuesta web.

    :param request: El objeto de solicitud representa la solicitud HTTP realizada por el cliente.
    Contiene información como el método de solicitud, encabezados y parámetros de URL
    :return: una respuesta web con la plantilla HTML renderizada. El contenido HTML se pasa como el
    parámetro `texto` y el tipo de contenido se establece en "texto/html".
    """
    file_path = "./templates/index.html"
    # Envio de Parametros al HTML
    nombre = "Rey"
    data = {"nombre": nombre, "estilos": "styles.css"}
    with open(file_path, "r") as file:
        template = jinja2.Template(file.read())
        html = template.render(data)
    return web.Response(text=html, content_type="text/html")


async def usr_path(request):
    """
    La función `usr_path` lee los archivos en la carpeta de un usuario y presenta una plantilla HTML con
    la información del archivo.

    :param request: El parámetro `request` es un objeto que representa la solicitud HTTP realizada por
    el cliente. Contiene información como el método de solicitud, encabezados, parámetros de URL y el
    cuerpo de la solicitud
    :return: una respuesta web con el contenido HTML renderizado.
    """

    # Recibiendo el usuario
    user = request.match_info["user"]
    # Leyendo los Archivos de la Carpeta del Usuario
    oslist = []
    for i in os.listdir(f"./{user}"):
        oslist.append((i, sizeof(os.path.getsize(f"./{user}/{i}"))))

    # Creando la informaci'on q vamos a enviar al html
    data = {
        "files": oslist,
        "user": user,
        "Cryptuser": user,
        "enlace": f"https://{NAME_APP}.onrender.com/",
    }

    # Enviando informacion al html
    with open("./templates/usr.html", "r") as file:
        template = jinja2.Template(file.read())
        html = template.render(data)
    # Retornan do el html
    return web.Response(text=html, content_type="text/html")
