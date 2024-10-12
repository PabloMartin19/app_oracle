from flask import Flask, render_template, request, redirect, url_for, session
import cx_Oracle

# Configuración de la base de datos
DB_USER = 'remoto'
DB_PASSWORD = 'remoto'  # Cambia a la contraseña del usuario remoto
DB_DSN = '192.168.1.23:1521/ORCLCDB'  # Cambia esto al DSN de tu base de datos

# Inicializa la aplicación Flask
app = Flask(__name__)
app.secret_key = 'mi_clave_secreta'  # Necesaria para las sesiones, cambia por una clave segura.

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Autenticación simple
        if username == DB_USER and password == DB_PASSWORD:
            session['username'] = username
            return redirect(url_for('tables'))
    
    return render_template('login.html')

@app.route('/tables')
def tables():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = cx_Oracle.connect(DB_USER, DB_PASSWORD, DB_DSN)
        cursor = conn.cursor()
        
        # Obtener las tablas accesibles para el usuario
        cursor.execute("SELECT table_name FROM all_tables WHERE owner = 'PABLOMARTIN'")
        tables = cursor.fetchall()
        
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print("Error en la conexión a la base de datos:", error.message)
        tables = []  # Si hay un error, no mostrar tablas.

    finally:
        cursor.close()
        conn.close()
    
    return render_template('tables.html', tables=tables)

@app.route('/table/<table_name>')
def view_table(table_name):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = cx_Oracle.connect(DB_USER, DB_PASSWORD, DB_DSN)
        cursor = conn.cursor()
        
        # Consulta de la tabla seleccionada
        query = f"SELECT * FROM pablomartin.{table_name}"
        cursor.execute(query)
        
        # Obtener nombres de las columnas
        column_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
    
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print("Error en la consulta de la tabla:", error.message)
        rows = []  # Si hay un error, no mostrar filas.
        column_names = []  # No hay columnas en caso de error.

    finally:
        cursor.close()
        conn.close()
    
    return render_template('view_table.html', table_name=table_name, rows=rows, column_names=column_names)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')  # Cambia el host según tu necesidad
