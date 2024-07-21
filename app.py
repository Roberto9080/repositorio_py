from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import re

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
            if imagen.filename == '':
                raise ValueError("Por favor, agregue una imagen del producto")
            # Verifica reglas de integridad antes de insertar
            if precio < 0 or existencias < 0 or talla < 0:
                raise ValueError("El precio, las existencias o la talla no pueden ser negativos")
            if not re.match(r'^[a-zA-Z ]+$', marca) or not re.match(r'^[a-zA-Z ]+$', color):
                raise ValueError("La marca y el color solo pueden contener letras y espacios")

            # Guarda la imagen en el servidor
            imagen_nombre = imagen.filename
            imagen.save(f'static/images/{imagen_nombre}')

            # Inserta los datos en la base de datos
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO Productos (marca, modelo, color, existencias, precio, talla, tipo, imagen_nombre)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (marca, modelo, color, existencias, precio, talla, tipo, imagen_nombre))
            conexion.commit()  # Guarda los cambios en la base de datos

            message = "Producto agregado exitosamente"
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

    return render_template('add_product.html', message=message, error=error, form_data=form_data)



# Ruta para ver los productos con búsqueda y filtros adicionales
@app.route('/see_products', methods=['GET', 'POST'])
def see_products():
    if verificar_sesion():
        return verificar_sesion()

    search_query = ''
    filters = {
        'marca': '',
        'modelo': '',
        'color': '',
        'talla': '',
        'tipo': ''
    }

    query = "SELECT * FROM Productos WHERE 1=1"
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
            query += " AND talla = %s"
            params.append(filters['talla'])
        if filters['tipo']:
            query += " AND tipo LIKE %s"
            params.append('%' + filters['tipo'] + '%')

    cursor = conexion.cursor(dictionary=True)
    cursor.execute(query, params)
    productos = cursor.fetchall()
    cursor.close()

    return render_template('see_products.html', productos=productos, search_query=search_query, **filters)

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


# Ruta para eliminar un producto
@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    if verificar_sesion():
        return verificar_sesion()

    cursor = conexion.cursor()
    cursor.execute("DELETE FROM Productos WHERE ProductoID = %s", (id,))
    conexion.commit()  # Guarda los cambios en la base de datos
    cursor.close()

    return redirect(url_for('see_products'))  # Redirige a ver productos después de eliminar

# Inicia la aplicación Flask en modo debug
if __name__ == '__main__':
    app.run(debug=True)
