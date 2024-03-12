from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Configuración de la base de datos
DATABASE = 'personas.db'

# Crear la tabla si no existe
def create_table():
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS persona (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                edad INTEGER
            )
        ''')
        connection.commit()

create_table()

# Rutas y vistas
@app.route('/')
def index():
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM persona')
        personas = cursor.fetchall()
    return render_template('index.html', personas=personas)

@app.route('/crear', methods=['POST', 'GET'])
def crear():
    if request.method == 'POST':
        nombre = request.form['nombre']
        edad = request.form['edad']

        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO persona (nombre, edad) VALUES (?, ?)', (nombre, edad))
            connection.commit()

        return redirect(url_for('index'))

    return render_template('crear.html')

@app.route('/actualizar/<int:id>', methods=['POST', 'GET'])
def actualizar(id):
    if request.method == 'POST':
        nuevo_nombre = request.form['nombre']
        nueva_edad = request.form['edad']

        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('UPDATE persona SET nombre=?, edad=? WHERE id=?', (nuevo_nombre, nueva_edad, id))
            connection.commit()

        return redirect(url_for('index'))

    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM persona WHERE id=?', (id,))
        persona = cursor.fetchone()

    return render_template('actualizar.html', persona=persona)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM persona WHERE id=?', (id,))
        connection.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
