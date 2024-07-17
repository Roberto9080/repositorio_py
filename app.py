from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

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
    # Verifica si el usuario está en la sesión
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect(url_for('login'))  # Si no hay sesión, redirige al login

# Ruta para cerrar la sesión
@app.route('/logout')
def logout():
    session.pop('username', None)  # Elimina el nombre de usuario de la sesión
    return redirect(url_for('login'))  # Redirige al login

# Ruta para la página de agregar producto, maneja métodos GET y POST
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    # Verifica si el usuario está en la sesión
    if 'username' not in session:
        return redirect(url_for('login'))  # Si no hay sesión, redirige al login

    if request.method == 'POST':
        # Obtiene los datos del formulario
        marca = request.form['marca']
        modelo = request.form['modelo']
        color = request.form['color']
        existencias = int(request.form['existencias'])
        precio = float(request.form['precio'])
        talla = int(request.form['talla'])
        tipo = request.form['tipo']
        imagen = request.files['imagen']
        
        # Guarda la imagen en el servidor (opcional, puedes ajustar esta parte según tus necesidades)
        imagen_nombre = imagen.filename
        imagen.save(f'static/images/{imagen_nombre}')
        
        # Inserta los datos en la base de datos
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO Productos (marca, modelo, color, existencias, precio, talla, tipo, imagen_nombre)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (marca, modelo, color, existencias, precio, talla, tipo, imagen_nombre))
        conexion.commit()  # Guarda los cambios en la base de datos
        
        return redirect(url_for('dashboard'))  # Redirige al dashboard después de agregar el producto

    return render_template('add_product.html')  # Renderiza la plantilla para agregar productos

# Ruta para ver los productos con búsqueda y filtros adicionales
@app.route('/see_products', methods=['GET', 'POST'])
def see_products():
    # Verifica si el usuario está en la sesión
    if 'username' not in session:
        return redirect(url_for('login'))  # Si no hay sesión, redirige al login

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

# Inicia la aplicación Flask en modo debug
if __name__ == '__main__':
    app.run(debug=True)
