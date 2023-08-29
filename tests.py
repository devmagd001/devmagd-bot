from requests import post, get

LINK = 'https://t.me/File_Master2Bot'

Short = get(
    f'https://shrinkme.io/api?api=61f51cc3ad79c044e0c86525f31a7b5a30d6c49f&url={LINK}&format=text').text
