from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'

# Configuración de Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Configuración de la base de datos
DATABASE = 'personas.db'


# Modelo de Usuario para Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Crear la tabla si no existe
def create_table():
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS persona (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                cedula INTEGER NOT NULL,
                correo TEXT NOT NULL,
                fecha_nacimiento TEXT NOT NULL,
                ubicacion TEXT NOT NULL,
                area TEXT NOT NULL
            )
        ''')
        connection.commit()

create_table()

# Rutas y vistas
@app.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 5 

    search_query = request.args.get('search', '')  # Obtener la consulta de búsqueda

    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()

        # Paginación
        if search_query:
            # Aplicar filtro de búsqueda si hay una consulta
            cursor.execute('SELECT COUNT(*) FROM persona WHERE nombre LIKE ?', (f'%{search_query}%',))
        else:
            cursor.execute('SELECT COUNT(*) FROM persona')

        total_personas = cursor.fetchone()[0]
        total_pages = (total_personas - 1) // per_page + 1

        # Limita el número de páginas
        page = min(page, total_pages)

        offset = (page - 1) * per_page

        if search_query:
            # Aplicar filtro de búsqueda si hay una consulta
            cursor.execute('SELECT * FROM persona WHERE nombre LIKE ? LIMIT ? OFFSET ?', (f'%{search_query}%', per_page, offset))
        else:
            cursor.execute('SELECT * FROM persona LIMIT ? OFFSET ?', (per_page, offset))

        personas = cursor.fetchall()

    return render_template('index.html', personas=personas, page=page, total_pages=total_pages)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificar las credenciales del usuario
        if username == 'superadmin@test.com' and password == 'sistemas24':
            # Crear un usuario 
            user = User(1)
            login_user(user)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('index'))
        else:
            flash('Credenciales incorrectas', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Cierre de sesión exitoso', 'success')
    return redirect(url_for('login'))

@app.route('/crear', methods=['POST', 'GET'])
@login_required
def crear():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            cedula = int(request.form['cedula'])  # Convertir a entero
            correo = request.form['correo']
            fecha_nacimiento = request.form['fecha_nacimiento']
            ubicacion = request.form['ubicacion']
            area = request.form['area']

            with sqlite3.connect(DATABASE) as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    INSERT INTO persona 
                    (nombre, apellido, cedula, correo, fecha_nacimiento, ubicacion, area)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (nombre, apellido, cedula, correo, fecha_nacimiento, ubicacion, area))
                connection.commit()

            flash('Persona agregada correctamente', 'success')
            return redirect(url_for('index'))

        except ValueError:
            flash('Error: La cédula debe ser un valor numérico', 'error')

    return render_template('crear.html')

@app.route('/actualizar/<int:id>', methods=['POST', 'GET'])
@login_required
def actualizar(id):
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM persona WHERE id=?', (id,))
        persona = cursor.fetchone()

    if not persona:
        flash('La persona no existe', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            nuevo_nombre = request.form['nombre']
            nuevo_apellido = request.form['apellido']
            nueva_cedula = int(request.form['cedula']) 
            nuevo_correo = request.form['correo']
            nueva_fecha_nacimiento = request.form['fecha_nacimiento']
            nueva_ubicacion = request.form['ubicacion']
            nuevo_area = request.form['area']

            with sqlite3.connect(DATABASE) as connection:
                cursor = connection.cursor()
                cursor.execute('''
                    UPDATE persona 
                    SET nombre=?, apellido=?, cedula=?, correo=?, fecha_nacimiento=?, ubicacion=?, area=?
                    WHERE id=?
                ''', (nuevo_nombre, nuevo_apellido, nueva_cedula, nuevo_correo, nueva_fecha_nacimiento, nueva_ubicacion, nuevo_area, id))
                connection.commit()

            flash('Persona actualizada correctamente', 'success')
            return redirect(url_for('index'))

        except ValueError:
            flash('Error: La cédula debe ser un valor numérico', 'error')

    return render_template('actualizar.html', persona=persona)

@app.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM persona WHERE id=?', (id,))
        connection.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
