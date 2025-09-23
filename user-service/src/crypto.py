import bcrypt

def hash_password(password):
    """Encripta una contraseña usando bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """Verifica si una contraseña coincide con su hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))