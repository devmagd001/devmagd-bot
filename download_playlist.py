from pytube import Playlist


def descargar_playlist(url, path):
    playlist = Playlist(url)
    count = 0
    for video in playlist.videos:
        count += 1
        video.streams.filter(file_extension="mp4").first().download(output_path=path)
        print(count)


def mostrar_progreso(stream, chunk, bytes_remaining):
    tamaño_total = stream.filesize
    bytes_descargados = tamaño_total - bytes_remaining

    porcentaje_completado = (bytes_descargados / tamaño_total) * 100
    print(f"Descargado {porcentaje_completado}% del video")
