from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import json
import numpy as np
import cv2
import dlib
from db import get_connection

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

def extract_landmarks(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    for face in faces:
        shape = predictor(gray, face)
        return [(pt.x, pt.y) for pt in shape.parts()]
    return []

@app.route('/usuario', methods=['POST'])
def registrar_usuario():
    data = request.form
    nombre = data['nombre']
    apellido = data['apellido']
    codigo = data['codigo']
    email = data['email']
    requisitoriado = data['requisitoriado'] == 'true'
    image = request.files['imagen']
    
    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    image.save(filepath)

    puntos = extract_landmarks(filepath)
    if not puntos:
        return jsonify({'error': 'No se detectó rostro'}), 400

    vector = []
    for i in range(1, len(puntos)):
        dx = puntos[i][0] - puntos[i-1][0]
        dy = puntos[i][1] - puntos[i-1][1]
        dist = (dx**2 + dy**2)**0.5
        vector.append(dist)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO usuarios (nombre, apellido, codigo_unico, email, requisitoriado, imagen_url, embeddings)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (nombre, apellido, codigo, email, requisitoriado, filepath, json.dumps(vector)))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Usuario registrado correctamente'})

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, apellido, codigo_unico, email, requisitoriado FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return jsonify(usuarios)

@app.route('/usuario/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Usuario eliminado correctamente'})

@app.route('/usuario/<int:id>', methods=['PUT'])
def editar_usuario(id):
    data = request.form
    nombre = data['nombre']
    apellido = data['apellido']
    codigo = data['codigo']
    email = data['email']
    requisitoriado = data['requisitoriado'] == 'true'

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE usuarios
        SET nombre=%s, apellido=%s, codigo_unico=%s, email=%s, requisitoriado=%s
        WHERE id=%s
    """, (nombre, apellido, codigo, email, requisitoriado, id))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Usuario actualizado correctamente'})

def calcular_distancia(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    return np.linalg.norm(v1 - v2)

@app.route('/reconocer', methods=['POST'])
def reconocer_usuario():
    imagen = request.files['imagen']
    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    imagen.save(filepath)

    puntos = extract_landmarks(filepath)
    if not puntos:
        return jsonify({'error': 'No se detectó rostro'}), 400

    vector_nuevo = []
    for i in range(1, len(puntos)):
        dx = puntos[i][0] - puntos[i-1][0]
        dy = puntos[i][1] - puntos[i-1][1]
        dist = (dx**2 + dy**2)**0.5
        vector_nuevo.append(dist)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()

    mejor_usuario = None
    menor_distancia = float('inf')
    umbral = 30.0

    for user in usuarios:
        try:
            emb = json.loads(user['embeddings'])
            distancia = calcular_distancia(vector_nuevo, emb)
            if distancia < menor_distancia and distancia < umbral:
                menor_distancia = distancia
                mejor_usuario = user
        except:
            continue

    if mejor_usuario:
        alerta = ""
        if mejor_usuario['requisitoriado']:
            alerta = "¡ALERTA! Usuario requisitoriado detectado. Notificación enviada (simulada)."
            print(alerta)

        return jsonify({
            'coincidencia': True,
            'usuario': {
                'id': mejor_usuario['id'],
                'nombre': mejor_usuario['nombre'],
                'apellido': mejor_usuario['apellido'],
                'email': mejor_usuario['email'],
                'requisitoriado': mejor_usuario['requisitoriado'],
                'distancia': round(menor_distancia, 2),
                'alerta': alerta
            }
        })

    return jsonify({'coincidencia': False})

if __name__ == '__main__':
    app.run(debug=True)
