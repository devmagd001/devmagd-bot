from cryptography.fernet import Fernet
clave = Fernet.generate_key()
cipher_suite = Fernet(clave)


class cryptoKey():
    def __init__(self):
        self.cipher_suite = cipher_suite

    def encriptar(self, texto: str):
        """
        La función "encriptar" toma una cadena como entrada y la encripta usando un conjunto de cifrado.

        :param texto: El parámetro "texto" es una cadena que representa el texto que desea cifrar
        :type texto: str
        :return: la versión cifrada del texto de entrada.
        """
        return self.cipher_suite.encrypt(texto.encode()).decode()

    def desencriptar(self, texto: str):
        """
        La función "desencriptar" toma una cadena como entrada y devuelve la versión descifrada de la
        cadena.

        :param texto: El parámetro "texto" es una cadena que representa el texto cifrado que debe
        descifrarse
        :type texto: str
        :return: la versión descifrada del texto de entrada.
        """
        return self.cipher_suite.decrypt(texto).decode()
