import asyncio
import os
from aiohttp import web
from aiohttp import streamer
import jinja2
from tools import sizeof

SERVER = os.getenv('SERVER')
NAME_APP = os.getenv("NAME_APP")
"""==============Envio de el Archivo por HTTP================="""

@streamer
async def file_sender(writer, file_path=None):

    with open(file_path, 'rb') as f:
        chunk = f.read(2 ** 16)
        while chunk:
            await writer.write(chunk)
            chunk = f.read(2 ** 16)

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
    file_name = request.match_info['file_name']
    route = request.match_info['route']

    file_path = os.path.join(route, file_name)
    headers = {
        "Content-disposition": "attachment; filename={file_name}".format(file_name=file_name),
        "Accept-Ranges": "bytes",
        "Content-Type": f'{file_path.split("/")[-1].split(".")[-1]}',
        "Content-Length": str(os.path.getsize(file_path))
    }

    if not os.path.exists(file_path):
        return web.Response(
            body='El Archivo  <{file_name}> No Existe'.format(
                file_name=file_name),
            status=404
        )

    return web.Response(
        body=file_sender(file_path=file_path),
        headers=headers
    )
    
async def submit_handler(request):
    # data = await request.post()  # Obtener los datos enviados mediante POST
    # input_text = data.get('input_text')  # Obtener el valor del campo input_text
    input_text = request.post().get('input_text', '')  # Obtener el valor del campo input_text
    
    # Obtener la URL completa
    url = f"{request.scheme}://{request.host}{request.path}"
    
    # Resto de la lógica de tu aplicación aquí...
    return web.Response(text=f"Texto: {input_text}, URL: {url}")

async def index(request):
    """
    La función `index` lee un archivo de plantilla HTML, le pasa un parámetro, representa la plantilla
    con el parámetro y devuelve el HTML representado como una respuesta web.

    :param request: El objeto de solicitud representa la solicitud HTTP realizada por el cliente.
    Contiene información como el método de solicitud, encabezados y parámetros de URL
    :return: una respuesta web con la plantilla HTML renderizada. El contenido HTML se pasa como el
    parámetro `texto` y el tipo de contenido se establece en "texto/html".
    """
    file_path = './templates/index.html'
    # Envio de Parametros al HTML
    nombre = 'Rey'
    data = {'nombre': nombre,
            'estilos': 'styles.css'}
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
    file_path = './templates/usr.html'

    # Recibiendo el usuario
    user = request.match_info['user']
    # Leyendo los Archivos de la Carpeta del Usuario
    oslist = []
    for i in os.listdir(f'./{user}'):
        oslist.append(
            (i, sizeof(os.path.getsize(f'./{user}/{i}'))))

    # Creando la informaci'on q vamos a enviar al html
    data = {'files': oslist,
            'user': user,
            'Cryptuser': user,
            'enlace': f'https://{NAME_APP}.onrender.com/'}

    # Enviando informacion al html
    with open(file_path, "r") as file:
        template = jinja2.Template(file.read())
        html = template.render(data)
    # Retornan do el html
    return web.Response(text=html, content_type="text/html")
