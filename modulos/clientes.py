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

@clientes_bp.route('/add_cliente', methods=['GET', 'POST'])
def add_cliente():
    if verificar_sesion():
        return verificar_sesion()

    message = None
    error = None
    form_data = {}  # Diccionario para almacenar los valores del formulario

    if request.method == 'POST':
        try:
            # Obtiene los datos del formulario
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            domicilio = request.form['domicilio']
            telefono = request.form['telefono']

            # Validación de los datos del formulario
            if not re.match(r'^[a-zA-Z ]+$', nombre):
                raise ValueError('El nombre solo puede contener letras y espacios.')
            if not re.match(r'^[a-zA-Z ]+$', apellido):
                raise ValueError('El apellido solo puede contener letras y espacios.')
            if not re.match(r'^[a-zA-Z0-9 ]+$', domicilio):
                raise ValueError('El domicilio solo puede contener letras, números y espacios.')
            if not re.match(r'^\d{10}$', telefono):
                raise ValueError('El teléfono debe ser un número de exactamente 10 dígitos.')

            # Inserta los datos en la base de datos
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO Cliente (Nombre, Apellido, Domicilio, Telefono)
                VALUES (%s, %s, %s, %s)
            """, (nombre, apellido, domicilio, telefono))
            conexion.commit()  # Guarda los cambios en la base de datos
            cursor.close()
            conexion.close()

            message = "Cliente agregado correctamente"
            form_data = {}  # Limpia los datos del formulario después de una inserción exitosa
        except mysql.connector.Error as err:
            error = f"Error en la base de datos: {err.msg}"
            form_data = request.form
        except ValueError as ve:
            error = str(ve)
            form_data = request.form
        except Exception as e:
            error = f"Ocurrió un error: {str(e)}"
            form_data = request.form

    return render_template('add_cliente.html', message=message, error=error, form_data=form_data)

# Ruta para ver clientes
@clientes_bp.route('/see_clientes', methods=['GET', 'POST'])
def see_clientes():
    if verificar_sesion():
        return verificar_sesion()

    search_query = ''
    filters = {'nombre': '', 'apellido': '', 'domicilio': '', 'telefono': ''}
    order = request.args.get('order', None)

    if request.method == 'POST':
        search_query = request.form.get('search', '')
        filters['nombre'] = request.form.get('nombre', '')
        filters['apellido'] = request.form.get('apellido', '')
        filters['domicilio'] = request.form.get('domicilio', '')
        filters['telefono'] = request.form.get('telefono', '')

    query = "SELECT * FROM Cliente WHERE 1=1"
    params = []

    if search_query:
        query += " AND (Nombre LIKE %s OR Apellido LIKE %s OR Domicilio LIKE %s OR Telefono LIKE %s)"
        search_pattern = f"%{search_query}%"
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern])

    if filters['nombre']:
        query += " AND Nombre LIKE %s"
        params.append(f"%{filters['nombre']}%")
    if filters['apellido']:
        query += " AND Apellido LIKE %s"
        params.append(f"%{filters['apellido']}%")
    if filters['domicilio']:
        query += " AND Domicilio LIKE %s"
        params.append(f"%{filters['domicilio']}%")
    if filters['telefono']:
        query += " AND Telefono LIKE %s"
        params.append(f"%{filters['telefono']}%")

    if order:
        if order == 'nombre_asc':
            query += " ORDER BY Nombre ASC"
        elif order == 'nombre_desc':
            query += " ORDER BY Nombre DESC"
        elif order == 'apellido_asc':
            query += " ORDER BY Apellido ASC"
        elif order == 'apellido_desc':
            query += " ORDER BY Apellido DESC"
        elif order == 'domicilio_asc':
            query += " ORDER BY Domicilio ASC"
        elif order == 'domicilio_desc':
            query += " ORDER BY Domicilio DESC"

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(query, params)
    clientes = cursor.fetchall()
    cursor.close()
    conexion.close()

    return render_template('see_clientes.html', clientes=clientes, search_query=search_query, filters=filters)

# Ruta para editar un cliente
@clientes_bp.route('/edit_cliente/<int:id>', methods=['GET', 'POST'])
def edit_cliente(id):
    if verificar_sesion():
        return verificar_sesion()

    message = None
    error = None
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            # Obtiene los datos del formulario
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            domicilio = request.form['domicilio']
            telefono = request.form['telefono']
            
            # Verifica reglas de integridad antes de actualizar
            if not re.match(r'^[a-zA-Z ]+$', nombre) or not re.match(r'^[a-zA-Z ]+$', apellido):
                raise ValueError("El nombre y el apellido solo pueden contener letras y espacios")
            if not re.match(r'^[a-zA-Z0-9 ]+$', domicilio):
                raise ValueError("El domicilio solo puede contener letras, números y espacios")
            if not re.match(r'^\d{10}$', telefono):
                raise ValueError("El teléfono debe ser un número de exactamente 10 dígitos")
            
            # Actualiza los datos en la base de datos
            cursor.execute("""
                UPDATE Cliente
                SET Nombre = %s, Apellido = %s, Domicilio = %s, Telefono = %s
                WHERE ClienteID = %s
            """, (nombre, apellido, domicilio, telefono, id))
            conexion.commit()  # Guarda los cambios en la base de datos
            
            message = "Se editó el cliente correctamente"
        except mysql.connector.Error as err:
            error = f"Error en la base de datos: {err.msg}"
        except ValueError as ve:
            error = str(ve)
        except Exception as e:
            error = f"Ocurrió un error: {str(e)}"
    
    # Obtiene los datos del cliente para mostrar en el formulario de edición
    cursor.execute("SELECT * FROM Cliente WHERE ClienteID = %s", (id,))
    cliente = cursor.fetchone()
    cursor.close()
    conexion.close()

    return render_template('edit_cliente.html', cliente=cliente, message=message, error=error)


# Ruta para eliminar un cliente
@clientes_bp.route('/delete_cliente/<int:id>', methods=['POST'])
def delete_cliente(id):
    if verificar_sesion():
        return verificar_sesion()
    
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM Cliente WHERE ClienteID = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    
    flash('Cliente eliminado correctamente')
    return redirect(url_for('clientes.see_clientes'))