from flask import Flask, request, session, redirect, url_for, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import bcrypt
import os

# Configuración de la aplicación Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/usuarios.db'
app.config['SECRET_KEY'] = 'mi_secreto'
db = SQLAlchemy(app)

# Crear la base de datos si no existe
db_path = "instance/usuarios.db"
if not os.path.exists(db_path):
    with app.app_context():
        db.create_all()
        print("Base de datos creada correctamente.")
else:
    print("La base de datos ya existe.")

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
            return jsonify({"error": "Acceso denegado. Por favor, inicia sesión."}), 403
        return f(*args, **kwargs)
    return decorated_function

# Ruta de Registro (Con cifrado de contraseña)
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    try:
        if request.method == 'POST':
            nombre = request.form['nombre']
            contrasena = request.form['contrasena']

            # Verificar si el usuario ya existe
            usuario_existente = Usuario.query.filter_by(nombre=nombre).first()
            if usuario_existente:
                return jsonify({"error": f"El usuario {nombre} ya está registrado. Intenta con otro nombre."}), 400

            # Cifrar la contraseña antes de guardarla
            contrasena_cifrada = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())

            # Guardar en la base de datos
            nuevo_usuario = Usuario(nombre=nombre, contrasena=contrasena_cifrada.decode('utf-8'))
            db.session.add(nuevo_usuario)
            db.session.commit()

            return jsonify({"mensaje": f"Usuario {nombre} registrado con éxito."}), 201

        return render_template('registro.html')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form['nombre']
        contrasena = request.form['contrasena']

        # Verificar si el usuario existe en la base de datos
        usuario = Usuario.query.filter_by(nombre=nombre).first()

        if usuario and bcrypt.checkpw(contrasena.encode('utf-8'), usuario.contrasena.encode('utf-8')):
            session['usuario'] = usuario.nombre
            return jsonify({"mensaje": f"Bienvenido {usuario.nombre}!"}), 200
        else:
            session.pop('usuario', None)  # Limpiar la sesión si las credenciales son incorrectas
            return jsonify({"error": "Nombre de usuario o contraseña incorrectos"}), 401

    return render_template('login.html')

# Ruta de Logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('usuario', None)
    return jsonify({"mensaje": "Has cerrado sesión correctamente."}), 200

# Ruta para listar usuarios registrados
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    lista_usuarios = [{"id": u.id, "nombre": u.nombre} for u in usuarios]
    return jsonify(lista_usuarios)

# Ruta protegida (Dashboard)
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    usuario_en_sesion = Usuario.query.filter_by(nombre=session.get('usuario')).first()
    if not usuario_en_sesion:
        session.pop('usuario', None)
        return jsonify({"error": "Usuario no encontrado o sesión inválida."}), 403
    return jsonify({"mensaje": f"Bienvenido al dashboard, {session['usuario']}!"})

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)