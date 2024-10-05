from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import mysql.connector
import re

abonos_bp = Blueprint('abonos', __name__)


# Conexión a la base de datos (ajusta según tu configuración)
def obtener_conexion():
    return mysql.connector.connect(
        user="root",
        password="betoeseto",
        host="localhost",
        database="Proyecto",
        port="3306"
    )

# Función para verificar si el usuario ha iniciado sesión
def verificar_sesion():
    if 'username' not in session:
        return redirect(url_for('login'))