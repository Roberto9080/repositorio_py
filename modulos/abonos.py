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

    # Definir la consulta para obtener la información necesaria
    query = """
    SELECT c.ClienteID, c.Nombre AS cliente_nombre, c.Apellido AS cliente_apellido, 
           SUM(a.Monto) AS total_abonado, 
           (SUM(v.Total) - SUM(a.Monto)) AS saldo_por_pagar, 
           MAX(a.Fecha) AS ultima_fecha_abono
    FROM Cliente c
    JOIN Ventas v ON c.ClienteID = v.ClienteID
    LEFT JOIN Abonos a ON v.VentaID = a.VentaID
    WHERE v.MetodoPago = 'Abonos'  -- Filtramos solo las ventas por abonos
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
