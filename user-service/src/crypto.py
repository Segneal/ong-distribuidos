import bcrypt

def hash_password(password):
    """Encripta una contraseña usando bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """Verifica si una contraseña coincide con su hash"""
    # Verificar si es hash bcrypt (empieza con $2b$)
    if hashed_password.startswith('$2b$'):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    else:
        # Asumir que es SHA256 (usuarios nuevos)
        import hashlib
        sha256_hash = hashlib.sha256(password.encode()).hexdigest()
        return sha256_hash == hashed_password