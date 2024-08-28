from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import json
import openai
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necesario para manejar sesiones

# Cargar el archivo JSON con las fallas
def cargar_fallas():
    if os.path.exists('fallas.JSON'):
        with open('fallas.JSON', encoding='utf-8') as f:
            return json.load(f)
    return []

fallas_data = cargar_fallas()

def obtener_respuesta(pregunta):
    if not pregunta.strip():
        return {"mensaje": "Por favor, ingrese una pregunta válida."}

    # Buscar la pregunta en el JSON de fallas
    for falla in fallas_data:
        if pregunta.lower() in falla['FALLA'].lower():
            # Crear una respuesta conversacional con formato mejorado
            falla_descripcion = falla['FALLA']
            solucion = "\n- ".join(falla['SOLUCION'])
            
            mensaje = (
                f"Problema reportado: {falla_descripcion}.\n\n"
                f"Solución: \n- {solucion}"
            )
            return {"mensaje": mensaje}

    # Si no se encuentra, utilizar OpenAI como respaldo
    ejemplos = ""
    for falla in fallas_data:
        descripcion = falla['FALLA']
        solucion = "\n- ".join(falla['SOLUCION'])

        ejemplos += (
            f"Problema: {descripcion}\n"
            f"Solución:\n- {solucion}\n\n"
        )

    prompt = f"{ejemplos}Pregunta: {pregunta}\nRespuesta:"

    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Actúa como un asistente experto en la resolución de fallas de máquinas. Responde de manera conversacional, estructurada y detallada, evitando respuestas muy extensas o pegadas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        return {"mensaje": respuesta.choices[0].message['content'].strip()}
    except Exception as e:
        return {"mensaje": f"Error al obtener respuesta de OpenAI: {str(e)}"}

@app.route('/coiler')
def coiler():
    return render_template('coiler.html')

@app.route('/ensambladora')
def ensambladora():
    return render_template('ensambladora.html')

@app.route('/perfil')
def perfil():
    if 'username' in session:
        return render_template('perfil.html', usuario=session['username'])
    return redirect(url_for('login'))

@app.route('/agregar_falla')
def agregar_falla():
    if 'username' in session:
        return render_template('agregar_falla.html', usuario=session['username'])
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', usuario=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        with open('usuarios.json', encoding='utf-8') as f:
            usuarios = json.load(f)

        for usuario in usuarios:
            if usuario['username'] == username and usuario['password'] == password:
                session['username'] = username
                return redirect(url_for('index'))

        return "Nombre de usuario o contraseña incorrectos", 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/consultar', methods=['POST'])
def consultar():
    data = request.get_json()
    if not data or 'pregunta' not in data:
        return jsonify({'respuesta': 'Pregunta inválida o no proporcionada'}), 400

    pregunta = data.get('pregunta', '').strip()
    if not pregunta:
        return jsonify({'respuesta': 'Por favor, ingrese una pregunta válida.'}), 400

    respuesta = obtener_respuesta(pregunta)
    return jsonify({'respuesta': respuesta['mensaje']})

@app.route('/guardar_falla', methods=['POST'])
def guardar_falla():
    data = request.get_json()
    falla = data.get('falla')
    solucion = data.get('solucion')

    if not falla or not solucion:
        return jsonify({'error': 'Datos incompletos'}), 400

    # Cargar los datos existentes
    fallas_data = cargar_fallas()

    # Agregar la nueva falla
    fallas_data.append({
        'FALLA': falla,
        'SOLUCION': [solucion]
    })

    # Guardar los datos actualizados
    with open('fallas.JSON', 'w', encoding='utf-8') as file:
        json.dump(fallas_data, file, ensure_ascii=False, indent=4)

    return jsonify({'message': 'Falla guardada correctamente'}), 200

@app.route('/listar_fallas', methods=['GET'])
def listar_fallas():
    fallas_data = cargar_fallas()
    return jsonify(fallas_data)

@app.route('/editar_falla', methods=['POST'])
def editar_falla():
    data = request.get_json()
    if not data or 'index' not in data or 'falla' not in data or 'solucion' not in data:
        return jsonify({'mensaje': 'Datos inválidos'}), 400

    index = data['index']
    falla_nueva = {
        'FALLA': data['falla'],
        'SOLUCION': [data['solucion']]
    }

    fallas_data = cargar_fallas()
    if 0 <= index < len(fallas_data):
        fallas_data[index] = falla_nueva
        with open('fallas.JSON', 'w', encoding='utf-8') as f:
            json.dump(fallas_data, f, indent=4, ensure_ascii=False)
        return jsonify({'mensaje': 'Falla actualizada correctamente'}), 200
    else:
        return jsonify({'mensaje': 'Índice fuera de rango'}), 400

@app.route('/eliminar_falla', methods=['POST'])
def eliminar_falla():
    data = request.get_json()
    if not data or 'index' not in data:
        return jsonify({'mensaje': 'Datos inválidos'}), 400

    index = data['index']

    fallas_data = cargar_fallas()
    if 0 <= index < len(fallas_data):
        fallas_data.pop(index)
        with open('fallas.JSON', 'w', encoding='utf-8') as f:
            json.dump(fallas_data, f, indent=4, ensure_ascii=False)
        return jsonify({'mensaje': 'Falla eliminada correctamente'}), 200
    else:
        return jsonify({'mensaje': 'Índice fuera de rango'}), 400

if __name__ == '__main__':
    app.run(debug=True)

