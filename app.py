from flask import Flask, render_template, request, redirect, url_for, session, flash
import cx_Oracle

app = Flask(__name__)
app.secret_key = 'Ti3jCYj!R6R7kf!X4qt2'

# Configuración de conexión a Oracle
def get_connection(username, password):
    try:
        # Cambiaremos la dirección IP dependiendo de la red del servidor
        dsn = cx_Oracle.makedsn("192.168.1.31", 1521, service_name="ORCLCDB")
        connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
        return connection
    except cx_Oracle.DatabaseError as e:
        print(f"Error en la conexión: {e}")
        return None

# Ruta de inicio que muestra el formulario de login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_connection(username, password)
        if conn:
            session['username'] = username
            session['password'] = password
            return redirect(url_for('tables'))
        else:
            flash('Credenciales incorrectas. Inténtalo de nuevo.')
    
    return render_template('login.html')

# Ruta para mostrar las tablas accesibles del usuario
@app.route('/tables', methods=['GET'])
def tables():
    if 'username' in session and 'password' in session:
        conn = get_connection(session['username'], session['password'])
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT table_name FROM user_tables")
            tables = [table[0] for table in cursor.fetchall()]
            cursor.close()
            conn.close()
            return render_template('tables.html', tables=tables)
        else:
            flash('Conexión expirada. Por favor, vuelve a iniciar sesión.')
            return redirect(url_for('login'))
    return redirect(url_for('login'))

# Ruta para ver los registros de una tabla
@app.route('/table/<string:table_name>')
def view_table(table_name):
    if 'username' in session and 'password' in session:
        conn = get_connection(session['username'], session['password'])
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"SELECT * FROM {table_name}")
                records = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                cursor.close()
                conn.close()
                return render_template('table_view.html', table_name=table_name, records=records, columns=column_names)
            except cx_Oracle.DatabaseError as e:
                flash(f"Error al acceder a la tabla: {str(e)}")
                return redirect(url_for('tables'))
        else:
            flash('Conexión expirada. Por favor, vuelve a iniciar sesión.')
            return redirect(url_for('login'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
