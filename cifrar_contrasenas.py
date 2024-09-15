from bcrypt import hashpw, gensalt
import json

def cifrar_contraseñas(usuarios):
    for usuario in usuarios:
        usuario['password'] = hashpw(usuario['password'].encode('utf-8'), gensalt()).decode('utf-8')
    return usuarios

usuarios = [
    {"username": "felix", "password": "felix123"},
    {"username": "karlos", "password": "jc090682"}
]

usuarios_cifrados = cifrar_contraseñas(usuarios)

with open('usuarios.json', 'w', encoding='utf-8') as f:
    json.dump(usuarios_cifrados, f, ensure_ascii=False, indent=4)

print("Contraseñas cifradas y archivo actualizado.")
