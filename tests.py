import instaloader

# Crea una instancia de Instaloader
L = instaloader.Instaloader()

# Ingresa el enlace del video que deseas descargar
video_url = 'https://www.instagram.com/reel/CvAeIlGADSZ/?igshid=MWZjMTM2ODFkZg=='

# Obtén la información del post
post = instaloader.Post.from_shortcode(L.context, video_url.split('/')[-2])

# Descarga el video
L.download_post(post, target='./')