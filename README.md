# Reconocimiento Facial - Backend Flask

Este es el backend de una aplicación de reconocimiento facial para control de acceso y seguridad. Está hecho con Python, Flask y MySQL. Permite registrar usuarios con imagen, detectar rostros y verificar si un usuario está marcado como requisitoriado.

## Funcionalidades

- Registro de usuarios con imagen facial
- Extracción de características (landmarks) usando dlib
- Comparación de rostros
- Alerta si el usuario está requisitoriado
- Listar, editar y eliminar usuarios

## Requisitos

- Python 3.9
- MySQL
- Librerías: Flask, OpenCV, dlib, numpy, mysql-connector-python

## Cómo ejecutar

```bash
git clone https://github.com/Agape-exe/reconocimiento-facial-app.git
cd AppReconocimiento
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
cd backend
python app.py
