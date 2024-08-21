from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import re

# Importar Blueprints
from modulos.clientes import clientes_bp
from modulos.abonos import abonos_bp
from modulos.ventas import ventas_bp

# Inicializa la aplicación Flask
app = Flask(__name__)
app.secret_key = 'tu_secreto'  # Necesario para manejar sesiones

# Conexión a la base de datos MySQL
conexion = mysql.connector.connect(
    user="root",
    password="betoeseto",
    host="localhost",
    database="Proyecto",
    port="3306"
)

# Registrar Blueprints
app.register_blueprint(clientes_bp, url_prefix='/clientes')
app.register_blueprint(abonos_bp)
app.register_blueprint(ventas_bp, url_prefix='/ventas')

# Función para verificar si el usuario ha iniciado sesión
def verificar_sesion():
    if 'username' not in session:
        return redirect(url_for('login'))
    
# Ruta para la página de inicio, redirige a la página de login
@app.route('/')
def home():
    return redirect(url_for('login'))

# Ruta para la página de login, maneja métodos GET y POST
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    username = ""
    password = ""
    
    # Si el método de la solicitud es POST, significa que el formulario ha sido enviado
    if request.method == 'POST':
        username = request.form['username']  # Obtiene el nombre de usuario del formulario
        password = request.form['password']  # Obtiene la contraseña del formulario
        
        # Crea un cursor para ejecutar consultas en la base de datos
        cursor = conexion.cursor(dictionary=True)
        # Ejecuta una consulta para verificar las credenciales del usuario
        cursor.execute("SELECT * FROM administrador WHERE Usuario = %s AND Pass = %s", (username, password))
        user = cursor.fetchone()  # Obtiene el primer resultado de la consulta
        
        # Si el usuario es encontrado, se inicia la sesión y se redirige al dashboard
        if user:
            session['username'] = user['Usuario']
            return redirect(url_for('dashboard'))
        else:
            error = "Usuario o contraseña incorrectos"  # Mensaje de error si las credenciales son incorrectas
    
    # Renderiza la plantilla del login con posibles mensajes de error
    return render_template('login.html', error=error, username=username, password=password)

# Ruta para la página del dashboard
@app.route('/dashboard')
def dashboard():
    # Verifica si el usuario ha iniciado sesión
    if verificar_sesion():
        return verificar_sesion()
    return render_template('dashboard.html', username=session['username'])

# Ruta para cerrar la sesión
@app.route('/logout')
def logout():
    session.pop('username', None)  # Elimina el nombre de usuario de la sesión
    return redirect(url_for('login'))  # Redirige al login

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if verificar_sesion():
        return verificar_sesion()

    message = None
    error = None
    form_data = {}  # Diccionario para almacenar los valores del formulario

    if request.method == 'POST':
        if 'limpiar' in request.form:
            message = "Los campos se han limpiado exitosamente"
            return render_template('add_product.html', message=message, form_data=form_data)

        try:
            # Obtiene los datos del formulario
            marca = request.form['marca']
            modelo = request.form['modelo']
            color = request.form['color']
            existencias = int(request.form['existencias'])
            precio = float(request.form['precio'])
            talla = float(request.form['talla'])
            tipo = request.form['tipo']
            imagen = request.files['imagen']

            # Verifica si se ha subido una imagen
            if imagen.filename:
                imagen_nombre = imagen.filename
                imagen.save(f'static/images/{imagen_nombre}')
            else:
                # Si no se sube una nueva imagen, mantenemos la existente
                imagen_nombre = form_data.get('imagen_nombre')
                if not imagen_nombre:
                    raise ValueError("Por favor, agregue una imagen del producto")

            # Verifica reglas de integridad antes de insertar
            if precio < 0 or existencias < 0 or talla < 0:
                raise ValueError("El precio, las existencias o la talla no pueden ser negativos")
            if not re.match(r'^[a-zA-Z ]+$', marca) or not re.match(r'^[a-zA-Z ]+$', color):
                raise ValueError("La marca y el color solo pueden contener letras y espacios")
            # Asignar el valor de marca al modelo si el modelo está vacío
            if not modelo:
                modelo = marca
            if not re.match(r'^[a-zA-Z 0-9]+$', modelo):
                raise ValueError("El modelo solo pueden contener letras,numeros y espacios o estar vacio")
            

            # Inserta los datos en la base de datos
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO Productos (marca, modelo, color, existencias, precio, talla, tipo, imagen_nombre)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (marca, modelo, color, existencias, precio, talla, tipo, imagen_nombre))
            conexion.commit()  # Guarda los cambios en la base de datos

            message = "Producto agregado exitosamente"
        except mysql.connector.Error as err:
            error = f"Error en la base de datos: {err.msg}"
        except ValueError as ve:
            error = str(ve)
        except Exception as e:
            error = f"Ocurrió un error: {str(e)}"

        # Mantener los datos del formulario para un nuevo registro similar
        form_data = request.form.to_dict(flat=True)

    return render_template('add_product.html', message=message, error=error, form_data=form_data)


@app.route('/see_products', methods=['GET', 'POST'])
def see_products():
    if verificar_sesion():
        return verificar_sesion()

    search_query = request.args.get('search_query', '')
    filters = {
        'marca': request.args.get('marca', ''),
        'modelo': request.args.get('modelo', ''),
        'color': request.args.get('color', ''),
        'talla': request.args.get('talla', ''),
        'tipo': request.args.get('tipo', '')
    }
    # Cambiar el valor predeterminado a 'existencias_asc'
    order_by = request.args.get('order', 'existencias_desc')

    # mi papa dice que no quiere que le aparezcan los que tienen de existencias 0
    query = "SELECT * FROM Productos WHERE existencias > 0"
    params = []

    if request.method == 'POST':
        search_query = request.form.get('search', '').strip()
        filters['marca'] = request.form.get('marca', '').strip()
        filters['modelo'] = request.form.get('modelo', '').strip()
        filters['color'] = request.form.get('color', '').strip()
        filters['talla'] = request.form.get('talla', '').strip()
        filters['tipo'] = request.form.get('tipo', '').strip()

    if search_query:
        query += " AND (marca LIKE %s OR modelo LIKE %s OR color LIKE %s OR tipo LIKE %s)"
        params.extend(['%' + search_query + '%'] * 4)
    
    if filters['marca']:
        query += " AND marca LIKE %s"
        params.append('%' + filters['marca'] + '%')
    if filters['modelo']:
        query += " AND modelo LIKE %s"
        params.append('%' + filters['modelo'] + '%')
    if filters['color']:
        query += " AND color LIKE %s"
        params.append('%' + filters['color'] + '%')
    if filters['talla']:
        query += " AND talla LIKE %s"
        params.append('%' + filters['talla'] + '%')
    if filters['tipo']:
        query += " AND tipo LIKE %s"
        params.append('%' + filters['tipo'] + '%')

    if order_by == 'precio_asc':
        query += " ORDER BY precio ASC"
    elif order_by == 'precio_desc':
        query += " ORDER BY precio DESC"
    elif order_by == 'existencias_asc':
        query += " ORDER BY existencias ASC"
    elif order_by == 'existencias_desc':
        query += " ORDER BY existencias DESC"
    elif order_by == 'marca_asc':
        query += " ORDER BY marca ASC"
    elif order_by == 'marca_desc':
        query += " ORDER BY marca DESC"

    cursor = conexion.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    productos = cursor.fetchall()
    cursor.close()

    # Contar el número de productos encontrados
    productos_count = len(productos)

    return render_template('see_products.html', productos=productos, search_query=search_query, order_by=order_by, filters=filters, productos_count=productos_count)



# Ruta para editar un producto, maneja métodos GET y POST
@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if verificar_sesion():
        return verificar_sesion()

    message = None
    error = None
    cursor = conexion.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            # Obtiene los datos del formulario
            marca = request.form['marca']
            modelo = request.form['modelo']
            color = request.form['color']
            existencias = int(request.form['existencias'])
            precio = float(request.form['precio'])
            talla = float(request.form['talla'])
            tipo = request.form['tipo']
            imagen = request.files['imagen']
            
            # Verifica reglas de integridad antes de actualizar
            if precio < 0 or existencias < 0 or talla < 0:
                raise ValueError("El precio, las existencias o la talla no pueden ser negativos")
            if not re.match(r'^[a-zA-Z ]+$', marca) or not re.match(r'^[a-zA-Z ]+$', color):
                raise ValueError("La marca y el color solo pueden contener letras y espacios")
            # Asignar el valor de marca al modelo si el modelo está vacío
            if not modelo:
                modelo = marca
            
            if imagen:
                # Guarda la nueva imagen en el servidor
                imagen_nombre = imagen.filename
                imagen.save(f'static/images/{imagen_nombre}')
            else:
                # Si no se ha subido una nueva imagen, utiliza el nombre de la imagen existente
                cursor.execute("SELECT imagen_nombre FROM Productos WHERE ProductoID = %s", (id,))
                imagen_nombre = cursor.fetchone()['imagen_nombre']
            
            # Actualiza los datos en la base de datos
            cursor.execute("""
                UPDATE Productos
                SET marca = %s, modelo = %s, color = %s, existencias = %s, precio = %s, talla = %s, tipo = %s, imagen_nombre = %s
                WHERE ProductoID = %s
            """, (marca, modelo, color, existencias, precio, talla, tipo, imagen_nombre, id))
            conexion.commit()  # Guarda los cambios en la base de datos
            
            message = "Se editó el producto correctamente"
        except mysql.connector.Error as err:
            error = f"Error en la base de datos: {err.msg}"
        except ValueError as ve:
            error = str(ve)
        except Exception as e:
            error = f"Ocurrió un error: {str(e)}"
    
    # Obtiene los datos del producto para mostrar en el formulario de edición
    cursor.execute("SELECT * FROM Productos WHERE ProductoID = %s", (id,))
    producto = cursor.fetchone()
    cursor.close()

    return render_template('edit_product.html', producto=producto, message=message, error=error)


@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    if verificar_sesion():
        return verificar_sesion()

    cursor = conexion.cursor()

    try:
        # Verificar si hay ventas asociadas al producto
        cursor.execute("SELECT COUNT(*) FROM Ventas WHERE ProductoID = %s", (id,))
        ventas_count = cursor.fetchone()[0]

        if ventas_count > 0:
            flash("No se puede eliminar el producto porque tiene ventas asociadas.", "error")
            return redirect(url_for('see_products'))  # Redirige a ver productos con mensaje de error

        # Eliminar el producto si no hay ventas asociadas
        cursor.execute("DELETE FROM Productos WHERE ProductoID = %s", (id,))
        conexion.commit()  # Guarda los cambios en la base de datos

        flash("Producto eliminado correctamente.", "success")
        return redirect(url_for('see_products'))  # Redirige a ver productos con mensaje de éxito
    except Exception as e:
        flash(f"Error al eliminar el producto: {str(e)}", "error")
        return redirect(url_for('see_products'))  # Redirige a ver productos con mensaje de error
    finally:
        cursor.close()


@app.route('/realizar_venta/<int:producto_id>/<int:cliente_id>', methods=['GET', 'POST'])
def realizar_venta(producto_id, cliente_id):
    if verificar_sesion():
        return verificar_sesion()
    
    cursor = conexion.cursor(dictionary=True)
    
    try:
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

            # Insertar la venta en la base de datos
            cursor.execute("""
                INSERT INTO Ventas (ProductoID, ClienteID, Cantidad, MetodoPago, Total, Fecha)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (producto_id, cliente_id, cantidad, pago, cantidad * producto['precio']))
            conexion.commit()

            return redirect(url_for('ventas.see_ventas'))
    except Exception as e:
        # Manejar errores
        return render_template('realizar_venta.html', producto=producto, cliente=cliente, producto_id=producto_id, cliente_id=cliente_id, error=str(e))
    finally:
        cursor.close()

    return render_template('realizar_venta.html', producto=producto, cliente=cliente, producto_id=producto_id, cliente_id=cliente_id)


# Inicia la aplicación Flask en modo debug
if __name__ == '__main__':
    app.run(debug=True)
