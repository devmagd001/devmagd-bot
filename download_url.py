from variables_globales import download_queues_url, app, userbot, OPTIONS
from os import mkdir
from Downloads import DownloadFiles


def descargar_archivos_url(username):
    global saved_messages
    global download_queues
    queue = download_queues_url[username]
    try:
        mkdir(username)
    except:
        pass

    while not queue.empty():
        message_id, url, username, directory, format = queue.get()
        try:
            DownloadFiles(
                app,
                userbot,
                message_id,
                url,
                username,
                directory,
                format,
                queue.qsize(),
                OPTIONS,
            )
        except Exception as x:
            app.send_message(message_id, x)

        queue.task_done()

    del download_queues_url[username]
