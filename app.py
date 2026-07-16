# -*- coding: utf-8 -*-
"""
Menú Azuero — App de demostración
Cubre 2 semestrales:
  1) Seguridad en el Desarrollo de Software: bcrypt + sesiones seguras.
  2) Desarrollo de Software IX: sitio de Comercio Electrónico
     (carrito, buscador, FAQ, contacto, ofertas, recomendaciones, pago).
"""

import os
import re
import sqlite3
import secrets
import unicodedata
from functools import wraps
from datetime import datetime, timedelta

import bcrypt
from flask import (
    Flask, request, redirect, url_for, render_template,
    make_response, g, session as flask_session
)

from menus import MENUS

app = Flask(__name__)
# Clave secreta usada SOLO para el handshake temporal de Google OAuth (estado/nonce).
# La sesión real de la app NO usa flask.session: usa la tabla `sessions` (ver más abajo).
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))

DATABASE = "app.db"
BCRYPT_COST = 12
SESSION_TIMEOUT_MINUTES = 1

# --- Google OAuth (opcional) -----------------------------------------------
# Para activarlo, exporta estas variables de entorno antes de correr la app:
#   GOOGLE_CLIENT_ID=...   GOOGLE_CLIENT_SECRET=...
# (ver el README para sacarlas de Google Cloud Console).
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_ENABLED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

oauth = None
if GOOGLE_ENABLED:
    from authlib.integrations.flask_client import OAuth
    oauth = OAuth(app)
    oauth.register(
        name="google",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


@app.context_processor
def inject_google_flag():
    return dict(google_enabled=GOOGLE_ENABLED)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text


def enrich_menus_with_ids():
    """Agrega un id único y datos de contexto a cada plato del catálogo."""
    for r in MENUS.values():
        for sec in r["secciones"]:
            for item in sec["platos"]:
                item["id"] = f"{r['slug']}-{slugify(item['nombre'])}"
                item["restaurante_slug"] = r["slug"]
                item["restaurante_nombre"] = r["nombre"]
                item["seccion"] = sec["titulo"]


enrich_menus_with_ids()

ITEM_INDEX = {
    item["id"]: item
    for r in MENUS.values()
    for sec in r["secciones"]
    for item in sec["platos"]
}


def resolve_item(restaurante_slug, nombre_contiene):
    for item in ITEM_INDEX.values():
        if item["restaurante_slug"] == restaurante_slug and nombre_contiene.lower() in item["nombre"].lower():
            return item
    return None


# ---------------------------------------------------------------------------
# Ofertas y recomendaciones (curadas a mano sobre el catálogo real)
# ---------------------------------------------------------------------------
_OFERTAS_CONFIG = [
    {"restaurante": "la-frankeria", "nombre_contiene": "Classic Cheese Burger", "descuento_pct": 15, "etiqueta": "Combo Clásico"},
    {"restaurante": "el-azteca", "nombre_contiene": "Tacos Mixtos", "descuento_pct": 10, "etiqueta": "Para compartir"},
    {"restaurante": "club-de-golf", "nombre_contiene": "Menú Nº3", "descuento_pct": 12, "etiqueta": "Especial del día"},
    {"restaurante": "la-frankeria", "nombre_contiene": "Cheezy Nachos de Pollo", "descuento_pct": 10, "etiqueta": "Antojo de fin de semana"},
]

OFERTAS = []
for cfg in _OFERTAS_CONFIG:
    item = resolve_item(cfg["restaurante"], cfg["nombre_contiene"])
    if item:
        precio_oferta = round(item["precio"] * (1 - cfg["descuento_pct"] / 100), 2)
        OFERTAS.append({**cfg, "item": item, "precio_oferta": precio_oferta})

# Promociones especiales de La Frankería (packs, no productos individuales)
# Se muestran como tarjetas informativas — no se agregan al carrito porque
# son promos que el cliente coordina directamente con el restaurante al pasar.
PROMOS_ESPECIALES = [
    {
        "id": "promo-pack-sabado",
        "titulo": "Pack del Sábado",
        "descripcion": "Promoción especial válida solamente los sábados.",
        "restaurante": "La Frankería",
        "restaurante_slug": "la-frankeria",
        "etiqueta": "Solo sábados",
    },
    {
        "id": "promo-weekend-pack",
        "titulo": "Weekend Pack",
        "descripcion": "Combo especial disponible viernes y sábado.",
        "restaurante": "La Frankería",
        "restaurante_slug": "la-frankeria",
        "etiqueta": "Viernes y sábado",
    },
]

_RECOMENDADOS_CONFIG = [
    ("club-de-golf", "Menú Nº4"),
    ("el-azteca", "Tacos Mixtos"),
    ("la-frankeria", "Super Burra"),
    ("el-azteca", "Queso Fundido"),
    ("la-frankeria", "Bacon Ranch"),
    ("club-de-golf", "Menú Nº2"),
]
RECOMENDADOS_BASE = [
    it for it in (resolve_item(s, n) for s, n in _RECOMENDADOS_CONFIG) if it
]


def get_recomendados(exclude_ids=None, n=3):
    exclude_ids = exclude_ids or set()
    pool = [it for it in RECOMENDADOS_BASE if it["id"] not in exclude_ids]
    return pool[:n]


FAQS = [
    ("¿Cómo funciona Menú Azuero?", "Es una app de «pide y pasa a buscar». Eliges un restaurante, armas tu pedido, pagas en línea y pasas a recogerlo directamente en el local cuando esté listo. No hay servicio a domicilio."),
    ("¿Cómo hago un pedido?", "Elige un restaurante, agrega los platos que quieras al carrito y confirma tu pago en el checkout. Luego pasas a buscar tu pedido en el restaurante."),
    ("¿Necesito una cuenta para pedir?", "Puedes navegar el catálogo libremente, pero para agregar al carrito y pagar necesitas iniciar sesión o registrarte."),
    ("¿Qué métodos de pago aceptan?", "Puedes pagar en efectivo al recoger tu pedido en el local, o por Yappy (se te muestra el número al finalizar la compra)."),
    ("¿Cuánto tarda en estar listo mi pedido?", "El tiempo varía según el restaurante y el pedido. Te sugerimos coordinar directamente con el local o esperar unos minutos antes de pasar a buscarlo."),
    ("¿Puedo combinar productos de varios restaurantes en un mismo pedido?", "Sí, el carrito acepta platos de los 3 restaurantes en una sola orden. Recuerda que tendrás que pasar por cada local a recoger."),
    ("¿Cómo elimino un producto del carrito?", "En la página del carrito, cambia la cantidad a 0 o usa el botón «Quitar»."),
    ("¿Mi sesión se cierra sola?", "Sí, por seguridad la sesión expira tras 15 minutos de inactividad."),
]


# ---------------------------------------------------------------------------
# Imágenes: si el archivo no existe, se usa un placeholder automáticamente
# ---------------------------------------------------------------------------
def _find_static_image(subfolder, base_name):
    for ext in ("jpg", "jpeg", "png", "webp"):
        rel = f"img/{subfolder}/{base_name}.{ext}"
        if os.path.exists(os.path.join(app.root_path, "static", rel)):
            return url_for("static", filename=rel)
    return None


@app.template_global()
def product_image(item_id):
    return _find_static_image("productos", item_id) or url_for("static", filename="img/placeholder-producto.svg")


@app.template_global()
def restaurant_image(slug):
    return _find_static_image("restaurantes", slug) or url_for("static", filename="img/placeholder-restaurante.svg")


# ---------------------------------------------------------------------------
# Base de datos (SQLite)
# ---------------------------------------------------------------------------
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            auth_provider TEXT NOT NULL DEFAULT 'local',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            last_activity TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            added_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total REAL NOT NULL,
            created_at TEXT NOT NULL,
            metodo_pago TEXT NOT NULL,
            telefono TEXT NOT NULL,
            direccion TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            item_id TEXT NOT NULL,
            nombre TEXT NOT NULL,
            restaurante TEXT NOT NULL,
            precio REAL NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id)
        );

        CREATE TABLE IF NOT EXISTS mensajes_contacto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    db.commit()
    db.close()


# Ejecutar init_db al importar el módulo, así gunicorn crea las tablas
# la primera vez que arranca la app en Render (u otros servicios cloud).
init_db()


# ---------------------------------------------------------------------------
# Gestión de sesiones seguras (semestral de Seguridad)
# ---------------------------------------------------------------------------
def generate_session_id():
    return secrets.token_hex(32)


def create_session(user_id):
    session_id = generate_session_id()
    now = datetime.utcnow().isoformat()
    db = get_db()
    db.execute(
        "INSERT INTO sessions (session_id, user_id, created_at, last_activity) VALUES (?, ?, ?, ?)",
        (session_id, user_id, now, now),
    )
    db.commit()
    return session_id


def destroy_session(session_id):
    if not session_id:
        return
    db = get_db()
    db.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    db.commit()


def get_current_user():
    """Cacheada en `g` para no golpear la DB más de una vez por request."""
    if hasattr(g, "_current_user_cache"):
        return g._current_user_cache

    session_id = request.cookies.get("session_id")
    if not session_id:
        g._current_user_cache = (None, None)
        return g._current_user_cache

    db = get_db()
    row = db.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
    if not row:
        g._current_user_cache = (None, None)
        return g._current_user_cache

    last_activity = datetime.fromisoformat(row["last_activity"])
    if datetime.utcnow() - last_activity > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
        destroy_session(session_id)
        g._current_user_cache = (None, None)
        return g._current_user_cache

    db.execute(
        "UPDATE sessions SET last_activity = ? WHERE session_id = ?",
        (datetime.utcnow().isoformat(), session_id),
    )
    db.commit()

    user = db.execute("SELECT * FROM users WHERE id = ?", (row["user_id"],)).fetchone()
    g._current_user_cache = (user, session_id)
    return g._current_user_cache


def set_session_cookie(response, session_id):
    response.set_cookie(
        "session_id",
        session_id,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=SESSION_TIMEOUT_MINUTES * 60,
    )
    return response


def clear_session_cookie(response):
    response.delete_cookie("session_id")
    return response


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user, _ = get_current_user()
        if not user:
            had_cookie = request.cookies.get("session_id") is not None
            # Si la petición viene de un formulario de acción (p. ej. POST /carrito/agregar),
            # usamos el campo oculto 'next' o el referrer para no rebotar a una URL solo-POST.
            fallback_next = request.form.get("next") or request.referrer or request.path
            resp = make_response(
                redirect(url_for(
                    "login",
                    expired=1 if had_cookie else None,
                    login_required=None if had_cookie else 1,
                    next=fallback_next,
                ))
            )
            return clear_session_cookie(resp)
        return view_func(user, *args, **kwargs)
    return wrapper


@app.context_processor
def inject_globals():
    user, _ = get_current_user()
    cart_count = 0
    if user:
        db = get_db()
        row = db.execute(
            "SELECT COALESCE(SUM(quantity), 0) AS c FROM cart_items WHERE user_id = ?",
            (user["id"],),
        ).fetchone()
        cart_count = row["c"]
    return dict(current_user=user, cart_count=cart_count)


def get_cart_items(user_id):
    db = get_db()
    rows = db.execute("SELECT * FROM cart_items WHERE user_id = ?", (user_id,)).fetchall()
    items, total = [], 0.0
    for row in rows:
        info = ITEM_INDEX.get(row["item_id"])
        if not info:
            continue
        subtotal = round(info["precio"] * row["quantity"], 2)
        total += subtotal
        items.append({"cart_id": row["id"], "item": info, "quantity": row["quantity"], "subtotal": subtotal})
    return items, round(total, 2)


def agrupar_por_restaurante(items):
    """
    Agrupa los items del carrito por restaurante y devuelve una lista con el
    nombre, su número de Yappy/teléfono y el subtotal de cada restaurante.
    Útil para el pago por Yappy cuando un pedido mezcla varios restaurantes.
    """
    grupos = {}
    for row in items:
        slug = row["item"]["restaurante_slug"]
        if slug not in grupos:
            r = MENUS.get(slug, {})
            grupos[slug] = {
                "nombre": row["item"]["restaurante_nombre"],
                "telefono": r.get("telefono", ""),
                "subtotal": 0.0,
            }
        grupos[slug]["subtotal"] = round(grupos[slug]["subtotal"] + row["subtotal"], 2)
    return list(grupos.values())


def create_order(user_id, items, total, metodo_pago, telefono, direccion):
    db = get_db()
    now = datetime.utcnow().isoformat()
    cur = db.execute(
        "INSERT INTO orders (user_id, total, created_at, metodo_pago, telefono, direccion) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, total, now, metodo_pago, telefono, direccion),
    )
    order_id = cur.lastrowid
    for it in items:
        db.execute(
            "INSERT INTO order_items (order_id, item_id, nombre, restaurante, precio, quantity) VALUES (?, ?, ?, ?, ?, ?)",
            (order_id, it["item"]["id"], it["item"]["nombre"], it["item"]["restaurante_nombre"], it["item"]["precio"], it["quantity"]),
        )
    db.commit()
    return order_id


# ---------------------------------------------------------------------------
# Rutas — Catálogo / navegación pública
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    restaurantes = [{"slug": r["slug"], "nombre": r["nombre"], "eslogan": r["eslogan"]} for r in MENUS.values()]
    return render_template("index.html", restaurantes=restaurantes, ofertas=OFERTAS[:3], recomendados=get_recomendados(n=4), promos=PROMOS_ESPECIALES)


@app.route("/dashboard")
def dashboard_redirect():
    return redirect(url_for("index"))


@app.route("/restaurante/<slug>")
def restaurant(slug):
    data = MENUS.get(slug)
    if not data:
        return redirect(url_for("index"))
    return render_template("restaurant.html", r=data)


@app.route("/buscar")
def buscar():
    q = request.args.get("q", "").strip()
    resultados = []
    if q:
        ql = q.lower()
        for item in ITEM_INDEX.values():
            haystack = f"{item['nombre']} {item['descripcion']} {item['restaurante_nombre']} {item['seccion']}".lower()
            if ql in haystack:
                resultados.append(item)
        resultados.sort(key=lambda x: (ql not in x["nombre"].lower(), x["nombre"]))
    return render_template("buscar.html", q=q, resultados=resultados)


@app.route("/ofertas")
def ofertas():
    return render_template("ofertas.html", ofertas=OFERTAS)


@app.route("/faq")
def faq():
    return render_template("faq.html", faqs=FAQS)


@app.route("/tecnologia")
def tecnologia():
    return render_template("tecnologia.html")


@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    enviado = False
    error = None
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip()
        mensaje = request.form.get("mensaje", "").strip()
        if not nombre or not email or not mensaje:
            error = "Completa todos los campos."
        else:
            db = get_db()
            db.execute(
                "INSERT INTO mensajes_contacto (nombre, email, mensaje, created_at) VALUES (?, ?, ?, ?)",
                (nombre, email, mensaje, datetime.utcnow().isoformat()),
            )
            db.commit()
            enviado = True
    return render_template("contacto.html", enviado=enviado, error=error)


# ---------------------------------------------------------------------------
# Rutas — Autenticación
# ---------------------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    next_url = request.values.get("next") or url_for("index")
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not email or not password:
            error = "Correo y contraseña son obligatorios."
        elif password != confirm:
            error = "Las contraseñas no coinciden."
        elif len(password) < 8:
            error = "La contraseña debe tener al menos 8 caracteres."
        else:
            db = get_db()
            existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if existing:
                error = "Ese correo ya está registrado."
            else:
                password_hash = bcrypt.hashpw(
                    password.encode("utf-8"), bcrypt.gensalt(rounds=BCRYPT_COST)
                ).decode("utf-8")
                db.execute(
                    "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
                    (email, password_hash, datetime.utcnow().isoformat()),
                )
                db.commit()
                return redirect(url_for("login", registered=1, next=next_url))

    return render_template("register.html", error=error, next=next_url)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    next_url = request.values.get("next") or url_for("index")
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user and not user["password_hash"]:
            # Cuenta creada con Google: no tiene contraseña local.
            error = "Esta cuenta usa Google. Entra con el botón «Continuar con Google»."
        elif not user or not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
            error = "Correo o contraseña incorrectos."
        else:
            old_session_id = request.cookies.get("session_id")
            if old_session_id:
                destroy_session(old_session_id)
            new_session_id = create_session(user["id"])

            resp = make_response(redirect(request.form.get("next") or next_url))
            set_session_cookie(resp, new_session_id)
            return resp

    return render_template(
        "login.html",
        error=error,
        expired=request.args.get("expired"),
        login_required=request.args.get("login_required"),
        registered=request.args.get("registered"),
        logged_out=request.args.get("logged_out"),
        google_off=request.args.get("google_off"),
        google_error=request.args.get("google_error"),
        next=next_url,
    )


@app.route("/logout", methods=["POST"])
def logout():
    session_id = request.cookies.get("session_id")
    destroy_session(session_id)
    resp = make_response(redirect(url_for("login", logged_out=1)))
    clear_session_cookie(resp)
    return resp


# ---------------------------------------------------------------------------
# Google OAuth ("Continuar con Google")
# ---------------------------------------------------------------------------
def iniciar_sesion_para(user_id, next_url):
    """Crea una sesión segura (rotando cualquier sesión previa) y fija la cookie."""
    old_session_id = request.cookies.get("session_id")
    if old_session_id:
        destroy_session(old_session_id)
    new_session_id = create_session(user_id)
    resp = make_response(redirect(next_url or url_for("index")))
    set_session_cookie(resp, new_session_id)
    return resp


@app.route("/login/google")
def login_google():
    if not GOOGLE_ENABLED:
        return redirect(url_for("login", google_off=1))
    # Guardamos a dónde volver tras autenticar
    flask_session["oauth_next"] = request.args.get("next") or url_for("index")
    redirect_uri = url_for("callback_google", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route("/login/google/callback")
def callback_google():
    if not GOOGLE_ENABLED:
        return redirect(url_for("login", google_off=1))
    try:
        token = oauth.google.authorize_access_token()
        userinfo = token.get("userinfo") or oauth.google.userinfo()
    except Exception:
        return redirect(url_for("login", google_error=1))

    email = (userinfo.get("email") or "").strip().lower()
    if not email:
        return redirect(url_for("login", google_error=1))

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not user:
        db.execute(
            "INSERT INTO users (email, password_hash, auth_provider, created_at) VALUES (?, ?, ?, ?)",
            (email, None, "google", datetime.utcnow().isoformat()),
        )
        db.commit()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    next_url = flask_session.pop("oauth_next", None)
    return iniciar_sesion_para(user["id"], next_url)


# ---------------------------------------------------------------------------
# Rutas — Carrito / Checkout (requieren sesión)
# ---------------------------------------------------------------------------
@app.route("/carrito")
@login_required
def carrito(user):
    items, total = get_cart_items(user["id"])
    exclude_ids = {i["item"]["id"] for i in items}
    recomendados = get_recomendados(exclude_ids=exclude_ids, n=3)
    return render_template("carrito.html", items=items, total=total, recomendados=recomendados)


@app.route("/carrito/agregar", methods=["POST"])
@login_required
def carrito_agregar(user):
    item_id = request.form.get("item_id")
    try:
        cantidad = max(1, int(request.form.get("cantidad", 1)))
    except (TypeError, ValueError):
        cantidad = 1

    if item_id in ITEM_INDEX:
        db = get_db()
        existing = db.execute(
            "SELECT * FROM cart_items WHERE user_id = ? AND item_id = ?", (user["id"], item_id)
        ).fetchone()
        if existing:
            db.execute("UPDATE cart_items SET quantity = quantity + ? WHERE id = ?", (cantidad, existing["id"]))
        else:
            db.execute(
                "INSERT INTO cart_items (user_id, item_id, quantity, added_at) VALUES (?, ?, ?, ?)",
                (user["id"], item_id, cantidad, datetime.utcnow().isoformat()),
            )
        db.commit()

    destino = request.form.get("next") or request.referrer or url_for("carrito")
    return redirect(destino)


@app.route("/carrito/actualizar/<int:cart_id>", methods=["POST"])
@login_required
def carrito_actualizar(user, cart_id):
    try:
        cantidad = max(0, int(request.form.get("cantidad", 1)))
    except (TypeError, ValueError):
        cantidad = 1
    db = get_db()
    row = db.execute("SELECT * FROM cart_items WHERE id = ? AND user_id = ?", (cart_id, user["id"])).fetchone()
    if row:
        if cantidad == 0:
            db.execute("DELETE FROM cart_items WHERE id = ?", (cart_id,))
        else:
            db.execute("UPDATE cart_items SET quantity = ? WHERE id = ?", (cantidad, cart_id))
        db.commit()
    return redirect(url_for("carrito"))


@app.route("/carrito/eliminar/<int:cart_id>", methods=["POST"])
@login_required
def carrito_eliminar(user, cart_id):
    db = get_db()
    db.execute("DELETE FROM cart_items WHERE id = ? AND user_id = ?", (cart_id, user["id"]))
    db.commit()
    return redirect(url_for("carrito"))


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout(user):
    items, total = get_cart_items(user["id"])
    if not items:
        return redirect(url_for("carrito"))

    grupos = agrupar_por_restaurante(items)
    error = None

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = re.sub(r"[^\d]", "", request.form.get("telefono", ""))
        metodo_pago = request.form.get("metodo_pago", "")

        if metodo_pago not in ("efectivo", "yappy"):
            error = "Selecciona un método de pago."
        elif not nombre:
            error = "Escribe tu nombre."
        elif len(telefono) < 7:
            error = "Escribe un número de teléfono válido."
        else:
            order_id = create_order(user["id"], items, total, metodo_pago, telefono, "")
            db = get_db()
            db.execute("DELETE FROM cart_items WHERE user_id = ?", (user["id"],))
            db.commit()
            return redirect(url_for("pedido", order_id=order_id))

    return render_template("checkout.html", items=items, total=total, grupos=grupos, error=error)


@app.route("/pedido/<int:order_id>")
@login_required
def pedido(user, order_id):
    db = get_db()
    order = db.execute("SELECT * FROM orders WHERE id = ? AND user_id = ?", (order_id, user["id"])).fetchone()
    if not order:
        return redirect(url_for("index"))
    items = db.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall()

    # Agrupar por restaurante para mostrar a quién pagar (Yappy)
    grupos = {}
    for it in items:
        rest = it["restaurante"]
        if rest not in grupos:
            tel = ""
            for r in MENUS.values():
                if r["nombre"] == rest:
                    tel = r.get("telefono", "")
                    break
            grupos[rest] = {"nombre": rest, "telefono": tel, "subtotal": 0.0}
        grupos[rest]["subtotal"] = round(grupos[rest]["subtotal"] + it["precio"] * it["quantity"], 2)
    grupos = list(grupos.values())

    return render_template("pedido.html", order=order, items=items, grupos=grupos)


if __name__ == "__main__":
    init_db()
    # En Render (u otros servicios cloud), la plataforma provee el puerto
    # mediante la variable de entorno PORT y maneja el HTTPS por su cuenta.
    # En localhost, usamos SSL autofirmado en el puerto 5000.
    port = int(os.environ.get("PORT", 5000))
    if os.environ.get("RENDER") or os.environ.get("PORT"):
        # Modo producción / cloud: HTTP interno, la plataforma agrega HTTPS
        app.run(host="0.0.0.0", port=port, debug=False)
    else:
        # Modo local: HTTPS autofirmado
        app.run(debug=True, host="0.0.0.0", port=port, ssl_context="adhoc")
