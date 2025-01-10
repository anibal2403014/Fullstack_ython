from flask import Flask, request, session, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import bcrypt
import os

# Configuración de la aplicación Flask
app = Flask(__name__)

# Configuración de la base de datos
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance', 'usuarios.db')}"
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mi_secreto')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db = SQLAlchemy(app)

# Crear la carpeta 'instance' si no existe
os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)

# Modelo de la base de datos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    contrasena = db.Column(db.String(120), nullable=False)

# Decorador para proteger rutas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            flash("Acceso denegado. Por favor, inicia sesión.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Ruta principal (Index)
@app.route('/')
def index():
    return render_template('index.html')

# Ruta de Registro
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        contrasena = request.form.get('contrasena')

        if not nombre or not contrasena:
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for('registro'))

        if len(contrasena) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "error")
            return redirect(url_for('registro'))

        usuario_existente = Usuario.query.filter_by(nombre=nombre).first()
        if usuario_existente:
            flash(f"El usuario '{nombre}' ya está registrado.", "error")
            return redirect(url_for('registro'))

        contrasena_cifrada = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())
        nuevo_usuario = Usuario(nombre=nombre, contrasena=contrasena_cifrada.decode('utf-8'))
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash(f"Usuario '{nombre}' registrado con éxito.", "success")
        return redirect(url_for('login'))

    return render_template('registro.html')

# Ruta de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        contrasena = request.form.get('contrasena')

        if not nombre or not contrasena:
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for('login'))

        usuario = Usuario.query.filter_by(nombre=nombre).first()

        if usuario and bcrypt.checkpw(contrasena.encode('utf-8'), usuario.contrasena.encode('utf-8')):
            session['usuario'] = usuario.nombre
            flash(f"Bienvenido, {usuario.nombre}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Nombre de usuario o contraseña incorrectos.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

# Ruta de Dashboard (protegida)
@app.route('/dashboard')
@login_required
def dashboard():
    usuario = session.get('usuario')
    return render_template('dashboard.html', usuario=usuario)

# Ruta de Logout (cierre de sesión)
@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    session.pop('usuario', None)
    session.clear()  # Limpiar toda la sesión
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for('login'))

# Ejecutar la aplicación
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
