from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "TU_LLAVE_SECRETA"  # Cambia esto por algo seguro en producción

@app.route("/")
def index():
    # Verificamos si el usuario está en sesión
    if "username" in session:
        return f"<h1>Bienvenido(a) {session['username']}!</h1><p>Estás en la página de inicio con sesión iniciada.</p>"
    else:
        return "<h1>Página de inicio (landing page)</h1><p>Usuario no autenticado.</p>"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Aquí recibimos datos de un formulario
        username = request.form.get("username")
        password = request.form.get("password")
        # Validación sencilla (HARDCODE - para ejemplo)
        if username == "admin" and password == "1234":
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return "<p>Credenciales inválidas. <a href='/login'>Intenta de nuevo</a></p>"
    return '''
    <h1>Inicio de Sesión</h1>
    <form method="POST">
        <label>Usuario:</label>
        <input type="text" name="username">
        <br><br>
        <label>Contraseña:</label>
        <input type="password" name="password">
        <br><br>
        <button type="submit">Iniciar sesión</button>
    </form>
    '''

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        # Recibir datos del formulario
        nuevo_usuario = request.form.get("nuevo_usuario")
        nuevo_password = request.form.get("nuevo_password")
        # Lógica de guardado en BD (simulada aquí)
        # ...
        return f"<p>Usuario '{nuevo_usuario}' registrado (simulado). <a href='/login'>Ir a login</a></p>"
    return '''
    <h1>Registro de Usuario</h1>
    <form method="POST">
        <label>Nuevo usuario:</label>
        <input type="text" name="nuevo_usuario">
        <br><br>
        <label>Contraseña:</label>
        <input type="password" name="nuevo_password">
        <br><br>
        <button type="submit">Registrarme</button>
    </form>
    '''

if __name__ == "__main__":
    app.run(debug=True, port=5050)

