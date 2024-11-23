from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector

abonos_bp = Blueprint('abonos', __name__)

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

@abonos_bp.route('/see_abonos', methods=['GET', 'POST'])
def see_abonos():
    if verificar_sesion():
        return verificar_sesion()

    search_query = request.args.get('search_query', '')

    # Consulta para obtener solo el nombre, apellido y la fecha del último abono
    query = """
    SELECT c.ClienteID, c.Nombre AS cliente_nombre, c.Apellido AS cliente_apellido, 
           MAX(a.Fecha) AS ultima_fecha_abono
    FROM Cliente c
    JOIN Ventas v ON c.ClienteID = v.ClienteID
    LEFT JOIN Abonos a ON v.VentaID = a.VentaID
    WHERE v.MetodoPago = 'Abonos'
    GROUP BY c.ClienteID
    HAVING ultima_fecha_abono IS NOT NULL
    """

    params = []

    if request.method == 'POST':
        search_query = request.form.get('search', '').strip()

    if search_query:
        query += " AND (c.Nombre LIKE %s OR c.Apellido LIKE %s)"
        params.extend(['%' + search_query + '%', '%' + search_query + '%'])

    query += " ORDER BY ultima_fecha_abono DESC"

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    abonos = cursor.fetchall()

    cursor.close()
    abonos_count = len(abonos)
    conexion.close()

    return render_template('see_abonos.html', abonos=abonos, search_query=search_query, abonos_count=abonos_count)

@abonos_bp.route('/historial_pagos/<int:cliente_id>', methods=['GET'])
def historial_pagos(cliente_id):
    if verificar_sesion():
        return verificar_sesion()

    # Consultas para obtener los datos del cliente y el saldo total
    query_cliente = """
    SELECT Nombre, Apellido 
    FROM Cliente 
    WHERE ClienteID = %s
    """
    
    # Consulta para obtener el saldo total del cliente
    query_saldo_total = """
    SELECT SaldoTotal 
    FROM SaldoClientes 
    WHERE ClienteID = %s
    """

    # Consulta para obtener el historial de abonos, el saldo restante y los detalles del producto comprado
    query_historial = """
    SELECT a.Fecha, a.Monto, a.SaldoRestante, p.marca, p.modelo, p.color, (v.Total / v.Cantidad) AS precio_usado, v.Cantidad
    FROM Abonos a
    JOIN 
    Ventas v ON a.VentaID = v.VentaID
    JOIN 
    Productos p ON v.ProductoID = p.ProductoID
    WHERE 
    v.ClienteID = %s AND v.MetodoPago = 'Abonos'
    ORDER BY a.Fecha DESC;
    """

    
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        # Ejecutar la consulta para obtener el nombre del cliente
        cursor.execute(query_cliente, (cliente_id,))
        cliente = cursor.fetchone()

        if not cliente:
            flash('Cliente no encontrado.', 'error')
            return redirect(url_for('abonos.see_abonos'))

        # Ejecutar la consulta para obtener el saldo total del cliente
        cursor.execute(query_saldo_total, (cliente_id,))
        saldo_total = cursor.fetchone()

        # Ejecutar la consulta para obtener el historial de abonos
        cursor.execute(query_historial, (cliente_id,))
        historial_abonos = cursor.fetchall()

        if not historial_abonos:
            flash('No hay abonos registrados para este cliente.', 'info')
            return redirect(url_for('abonos.see_abonos'))

    except Exception as e:
        flash(f'Error al obtener el historial: {e}', 'error')
    finally:
        cursor.close()
        conexion.close()

    return render_template('historial_pagos.html', cliente=cliente, saldo_total=saldo_total, historial_abonos=historial_abonos)



@abonos_bp.route('/delete_abono/<int:abono_id>', methods=['POST'])
def delete_abono(abono_id):
    if verificar_sesion():
        return verificar_sesion()

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("DELETE FROM Abonos WHERE AbonoID = %s", (abono_id,))
        conexion.commit()
        flash('Abono eliminado correctamente.', 'success')
    except Exception as e:
        flash(f'Error al eliminar el abono: {e}', 'error')
    finally:
        cursor.close()
        conexion.close()

    return redirect(url_for('abonos.see_abonos'))

@abonos_bp.route('/agregar_abono/<int:cliente_id>', methods=['GET', 'POST'])
def add_abono(cliente_id):
    if verificar_sesion():
        return verificar_sesion()

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        # Obtener la información del cliente
        cursor.execute("SELECT Nombre, Apellido FROM Cliente WHERE ClienteID = %s", (cliente_id,))
        cliente = cursor.fetchone()

        if request.method == 'POST':
            monto_abono = float(request.form['monto_abono'])

            # Obtener la última venta activa del cliente que tenga el método de pago 'Abonos'
            cursor.execute("""
                SELECT VentaID, Total
                FROM Ventas
                WHERE ClienteID = %s AND MetodoPago = 'Abonos'
                ORDER BY Fecha DESC LIMIT 1
            """, (cliente_id,))
            venta = cursor.fetchone()

            if not venta:
                flash('No se encontró ninguna venta activa en abonos para este cliente.', 'error')
                return render_template('add_abono.html', cliente_id=cliente_id, cliente=cliente)

            venta_id = venta['VentaID']

            # Obtener el último saldo restante del cliente
            cursor.execute("""
                SELECT SaldoRestante
                FROM Abonos
                WHERE VentaID = %s
                ORDER BY Fecha DESC LIMIT 1
            """, (venta_id,))
            ultimo_abono = cursor.fetchone()

            if ultimo_abono:
                saldo_restante = ultimo_abono['SaldoRestante']
            else:
                # Si no hay abonos previos, el saldo restante es el total de la venta
                saldo_restante = venta['Total']

            # Calcular el nuevo saldo restante después del abono
            nuevo_saldo_restante = saldo_restante - monto_abono

            # Actualizar el saldo total del cliente en la tabla SaldoClientes
            cursor.execute("""
                UPDATE SaldoClientes
                SET SaldoTotal = SaldoTotal - %s
                WHERE ClienteID = %s
            """, (monto_abono, cliente_id))

            # Registrar el nuevo abono
            cursor.execute("""
                INSERT INTO Abonos (VentaID, Monto, SaldoRestante, Fecha)
                VALUES (%s, %s, %s, NOW())
            """, (venta_id, monto_abono, nuevo_saldo_restante))

            conexion.commit()

            flash('Abono agregado exitosamente', 'success')
            return redirect(url_for('abonos.see_abonos'))

    except Exception as e:
        flash(f'Ocurrió un error: {str(e)}', 'error')
    finally:
        cursor.close()
        conexion.close()

    return render_template('add_abono.html', cliente_id=cliente_id, cliente=cliente)
