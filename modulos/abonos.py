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

    # Consulta para obtener el saldo total por cliente consolidado
    query = """
    SELECT c.ClienteID, c.Nombre AS cliente_nombre, c.Apellido AS cliente_apellido, 
           SUM(COALESCE(a.Monto, 0)) AS total_abonado,
           SUM(v.Total) AS total_venta,
           (SUM(v.Total) - COALESCE(SUM(a.Monto), 0)) AS saldo_por_pagar, 
           MAX(a.Fecha) AS ultima_fecha_abono
    FROM Cliente c
    JOIN Ventas v ON c.ClienteID = v.ClienteID
    LEFT JOIN Abonos a ON v.VentaID = a.VentaID
    WHERE v.MetodoPago = 'Abonos'
    GROUP BY c.ClienteID
    HAVING saldo_por_pagar > 0
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

    # Consulta para obtener los datos del cliente
    query_cliente = """
    SELECT Nombre, Apellido 
    FROM Cliente 
    WHERE ClienteID = %s
    """
    
    # Consulta para obtener el historial de abonos y calcular el saldo restante acumulado
    query_historial = """
    SELECT a.Fecha, a.Monto, 
           @saldo_restante := @saldo_restante - a.Monto AS saldo_restante
    FROM (SELECT v.VentaID, v.Total, v.ClienteID
          FROM Ventas v
          WHERE v.ClienteID = %s AND v.MetodoPago = 'Abonos') ventas
    JOIN Abonos a ON a.VentaID = ventas.VentaID, 
         (SELECT @saldo_restante := SUM(v.Total) 
          FROM Ventas v WHERE v.ClienteID = %s AND v.MetodoPago = 'Abonos') init
    ORDER BY a.Fecha ASC
    """
    
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    # Ejecutar la consulta para obtener el nombre del cliente
    cursor.execute(query_cliente, (cliente_id,))
    cliente = cursor.fetchone()

    # Ejecutar la consulta para obtener el historial de abonos con saldo acumulado
    cursor.execute(query_historial, (cliente_id, cliente_id))
    historial_abonos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('historial_pagos.html', cliente=cliente, historial_abonos=historial_abonos)

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

            # Obtener la última venta activa para este cliente que tenga el método de pago 'Abonos'
            cursor.execute("""
                SELECT VentaID
                FROM Ventas
                WHERE ClienteID = %s AND MetodoPago = 'Abonos'
                ORDER BY Fecha DESC LIMIT 1
            """, (cliente_id,))
            venta = cursor.fetchone()

            if venta is None:
                flash('No se encontró ninguna venta en abonos para este cliente.', 'error')
                return render_template('add_abono.html', cliente_id=cliente_id, cliente=cliente)

            venta_id = venta['VentaID']

            # Obtener el saldo total adeudado del cliente
            cursor.execute("""
                SELECT SUM(v.Total) AS total_deudado
                FROM Ventas v
                WHERE v.ClienteID = %s AND v.MetodoPago = 'Abonos'
            """, (cliente_id,))
            total_deudado = cursor.fetchone()['total_deudado']

            if total_deudado is None:
                total_deudado = 0

            # Actualizar el saldo restante y registrar el abono
            saldo_restante = total_deudado - monto_abono
            cursor.execute("""
                INSERT INTO Abonos (VentaID, Monto, SaldoRestante, Fecha)
                VALUES (%s, %s, %s, NOW())
            """, (venta_id, monto_abono, saldo_restante))
            conexion.commit()  # Guarda los cambios en la base de datos

            flash('Abono agregado exitosamente', 'success')
            return redirect(url_for('abonos.see_abonos'))

    except Exception as e:
        # Manejar errores
        flash(f'Ocurrió un error: {str(e)}', 'error')
    finally:
        cursor.close()
        conexion.close()

    return render_template('add_abono.html', cliente_id=cliente_id, cliente=cliente)

