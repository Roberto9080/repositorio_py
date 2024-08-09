from flask import Blueprint, render_template, request, redirect, url_for, session, flash
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

@ventas_bp.route('/see_ventas', methods=['GET', 'POST'])
def see_ventas():
    if verificar_sesion():
        return verificar_sesion()

    search_query = request.args.get('search_query', '')
    filters = {
        'cliente': request.args.get('cliente', ''),
        'producto': request.args.get('producto', ''),
        'color': request.args.get('color', ''),
        'talla': request.args.get('talla', ''),
        'tipo': request.args.get('tipo', ''),
        'fecha': request.args.get('fecha', ''),
        'cantidad': request.args.get('cantidad', ''),
        'total': request.args.get('total', '')
    }
    order_by = request.args.get('order', 'fecha_asc')

    query = """
        SELECT v.VentaID, v.ClienteID, v.ProductoID, v.Cantidad, v.MetodoPago, v.Total, c.Nombre AS cliente_nombre, c.Apellido AS cliente_apellido,
               p.marca, p.modelo, p.color, p.talla, p.imagen_nombre, v.Fecha, p.tipo, p.precio
        FROM Ventas v
        JOIN Cliente c ON v.ClienteID = c.ClienteID
        JOIN Productos p ON v.ProductoID = p.ProductoID
        WHERE 1=1
    """
    params = []

    if request.method == 'POST':
        search_query = request.form.get('search', '').strip()
        filters['cliente'] = request.form.get('cliente', '').strip()
        filters['producto'] = request.form.get('producto', '').strip()
        filters['color'] = request.form.get('color', '').strip()
        filters['talla'] = request.form.get('talla', '').strip()
        filters['tipo'] = request.form.get('tipo', '').strip()
        filters['fecha'] = request.form.get('fecha', '').strip()
        filters['cantidad'] = request.form.get('cantidad', '').strip()
        filters['total'] = request.form.get('total', '').strip()

    if search_query:
        query += " AND (c.Nombre LIKE %s OR c.Apellido LIKE %s OR p.marca LIKE %s OR p.modelo LIKE %s)"
        params.extend(['%' + search_query + '%'] * 4)
    
    if filters['cliente']:
        query += " AND (c.Nombre LIKE %s OR c.Apellido LIKE %s)"
        params.extend(['%' + filters['cliente'] + '%', '%' + filters['cliente'] + '%'])
    if filters['producto']:
        query += " AND (p.marca LIKE %s OR p.modelo LIKE %s)"
        params.extend(['%' + filters['producto'] + '%', '%' + filters['producto'] + '%'])
    if filters['color']:
        query += " AND p.color LIKE %s"
        params.append('%' + filters['color'] + '%')
    if filters['talla']:
        query += " AND p.talla = %s"
        params.append(filters['talla'])
    if filters['tipo']:
        query += " AND p.tipo = %s"
        params.append(filters['tipo'])
    if filters['fecha']:
        query += " AND DATE(v.Fecha) = %s"
        params.append(filters['fecha'])
    if filters['cantidad']:
        query += " AND v.Cantidad = %s"
        params.append(filters['cantidad'])
    if filters['total']:
        query += " AND v.Total = %s"
        params.append(filters['total'])

    if order_by == 'precio_asc':
        query += " ORDER BY p.precio ASC"
    elif order_by == 'precio_desc':
        query += " ORDER BY p.precio DESC"
    elif order_by == 'fecha_asc':
        query += " ORDER BY v.Fecha ASC"
    elif order_by == 'fecha_desc':
        query += " ORDER BY v.Fecha DESC"

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    ventas = cursor.fetchall()
    cursor.close()
    ventas_count = len(ventas)
    conexion.close()

    return render_template('see_ventas.html', ventas=ventas, search_query=search_query, order_by=order_by, filters=filters, ventas_count=ventas_count)


@ventas_bp.route('/delete_venta/<int:venta_id>', methods=['POST'])
def delete_venta(venta_id):
    if verificar_sesion():
        return verificar_sesion()

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("DELETE FROM Ventas WHERE VentaID = %s", (venta_id,))
        conexion.commit()
        flash('Venta eliminada correctamente.', 'success')
    except Exception as e:
        flash(f'Error al eliminar la venta: {e}', 'error')
    finally:
        cursor.close()
        conexion.close()

    return redirect(url_for('ventas.see_ventas'))