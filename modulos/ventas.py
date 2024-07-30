from flask import Blueprint, render_template, request, redirect, url_for, session
import mysql.connector

ventas_bp = Blueprint('ventas', __name__)

def obtener_conexion():
    return mysql.connector.connect(
        user="root",
        password="betoeseto",
        host="localhost",
        database="Proyecto",
        port="3306"
    )

def verificar_sesion():
    if 'username' not in session:
        return redirect(url_for('login'))
    


@ventas_bp.route('/escoger_cliente/<int:producto_id>', methods=['GET', 'POST'])
def escoger_cliente(producto_id):
    # Verificar la sesión del usuario
    if verificar_sesion():
        return verificar_sesion()

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    # Obtener los datos del producto seleccionado usando el producto_id
    cursor.execute("SELECT * FROM Productos WHERE ProductoID = %s", (producto_id,))
    producto = cursor.fetchone()

    # Inicializar variables para búsqueda y filtros
    search_query = ''
    filters = {'nombre': '', 'apellido': '', 'domicilio': '', 'telefono': ''}
    order = request.args.get('order', None)  # Obtener el parámetro de ordenamiento de la URL

    # Manejar la solicitud POST para obtener los datos del formulario
    if request.method == 'POST':
        search_query = request.form.get('search', '')  # Obtener el término de búsqueda
        filters['nombre'] = request.form.get('nombre', '')  # Obtener filtros de nombre
        filters['apellido'] = request.form.get('apellido', '')  # Obtener filtros de apellido
        filters['domicilio'] = request.form.get('domicilio', '')  # Obtener filtros de domicilio
        filters['telefono'] = request.form.get('telefono', '')  # Obtener filtros de teléfono

    # Construir la consulta SQL con filtros y búsqueda
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

    # Añadir ordenamiento a la consulta si se especifica
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

    # Ejecutar la consulta y obtener los resultados
    cursor.execute(query, params)
    clientes = cursor.fetchall()
    cursor.close()
    conexion.close()

    # Renderizar la plantilla con los clientes y los parámetros de búsqueda y filtro
    return render_template('escoger_cliente.html', clientes=clientes, producto_id=producto_id, search_query=search_query, filters=filters)

@ventas_bp.route('/realizar_venta/<int:producto_id>/<int:cliente_id>', methods=['GET', 'POST'])
def realizar_venta(producto_id, cliente_id):
    if verificar_sesion():
        return verificar_sesion()

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    # Obtener los datos del producto y del cliente
    cursor.execute("SELECT * FROM Productos WHERE ProductoID = %s", (producto_id,))
    producto = cursor.fetchone()
    cursor.execute("SELECT * FROM Cliente WHERE ClienteID = %s", (cliente_id,))
    cliente = cursor.fetchone()

    if request.method == 'POST':
        cantidad = int(request.form['cantidad'])
        pago = request.form['pago']
        
        # Verificar que la cantidad no exceda las existencias
        if cantidad > producto['existencias']:
            error = "La cantidad solicitada excede las existencias disponibles."
            return render_template('realizar_venta.html', producto=producto, cliente=cliente, producto_id=producto_id, cliente_id=cliente_id, error=error)
        
        # Actualizar las existencias del producto
        nuevas_existencias = producto['existencias'] - cantidad
        cursor.execute("UPDATE Productos SET existencias = %s WHERE ProductoID = %s", (nuevas_existencias, producto_id))
        
        # Insertar la venta en la base de datos
        cursor.execute("""
            INSERT INTO ventas (producto, cliente, cantidad, metodo_pago)
            VALUES (%s, %s, %s, %s)
        """, (producto_id, cliente_id, cantidad, pago))
        conexion.commit()
        
        cursor.close()
        conexion.close()
        
        return redirect(url_for('productos.see_products'))
    
    return render_template('realizar_venta.html', producto=producto, cliente=cliente, producto_id=producto_id, cliente_id=cliente_id)
