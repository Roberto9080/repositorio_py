from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import mysql.connector
import re

# Crear el Blueprint
clientes_bp = Blueprint('clientes', __name__)

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

# Ruta para agregar clientes
@clientes_bp.route('/add_cliente', methods=['GET', 'POST'])
def add_cliente():
    if verificar_sesion():
        return verificar_sesion()

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        domicilio = request.form['domicilio']
        telefono = request.form['telefono']

        error = None
        
        # Validación de los datos del formulario
        if not re.match(r'^[a-zA-Z ]+$', nombre):
            error = 'El nombre solo puede contener letras y espacios.'
        elif not re.match(r'^[a-zA-Z ]+$', apellido):
            error = 'El apellido solo puede contener letras y espacios.'
        elif not re.match(r'^[a-zA-Z0-9 ]+$', domicilio):
            error = 'El domicilio solo puede contener letras, números y espacios.'
        elif not re.match(r'^\d{10}$', telefono):
            error = 'El teléfono debe ser un número de exactamente 10 dígitos.'
        
        if error:
            flash(error)
            return render_template('add_cliente.html')

        # Si no hay errores, inserta el cliente en la base de datos
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO Cliente (Nombre, Apellido, Domicilio, Telefono)
            VALUES (%s, %s, %s, %s)
        """, (nombre, apellido, domicilio, telefono))
        conexion.commit()
        cursor.close()
        conexion.close()
        flash('Cliente agregado correctamente')
        return redirect(url_for('clientes.add_cliente'))

    return render_template('add_cliente.html')
