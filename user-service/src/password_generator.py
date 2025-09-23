import random
import string

def generate_random_password(length=8):
    """Genera una contraseña aleatoria de la longitud especificada"""
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password