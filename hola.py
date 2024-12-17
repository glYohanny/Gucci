

import bcrypt

# Generar hash para la contraseña "admin123"
password = "admin123"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print("Hash generado:", hashed.decode('utf-8'))