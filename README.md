# Menú Azuero — App de comercio electrónico + seguridad

Sitio web funcional (Flask + SQLite) que sirve para **dos semestrales**:

1. **Seguridad en el Desarrollo de Software** — autenticación con bcrypt y
   gestión de sesiones seguras.
2. **Desarrollo de Software IX** — sitio de Comercio Electrónico: carrito,
   buscador, FAQ, contacto, ofertas/promociones, recomendaciones de producto
   y sistema de pago (simulado).

Vende platos reales de 3 restaurantes de Azuero: **Club de Golf**, **El
Azteca** y **La Frankería**.

## Instalación

```bash
cd frankeria_app
python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar

```bash
python app.py
```

Abre **https://localhost:5000**. El navegador mostrará una advertencia de
certificado no confiable (normal, es HTTPS local autofirmado, necesario para
que la cookie `Secure` funcione) — dale "Avanzado" → "Continuar a localhost".

La base de datos (`app.db`) se crea sola al arrancar.

## Acceso con Google (opcional)

El sitio funciona perfectamente con **correo y contraseña** (que es lo que
demuestra el hash con bcrypt del semestral de seguridad). Además tiene un botón
**"Continuar con Google"** que puedes activar así:

1. Entra a Google Cloud Console (https://console.cloud.google.com/), crea un
   proyecto y ve a *APIs y servicios → Credenciales*.
2. Crea unas credenciales de tipo *ID de cliente de OAuth 2.0* → *Aplicación
   web*.
3. En *URIs de redireccionamiento autorizados* agrega exactamente:
   `https://localhost:5000/login/google/callback`
4. Copia el *Client ID* y *Client Secret* y expórtalos antes de correr la app:

   ```bash
   export GOOGLE_CLIENT_ID="tu-client-id"
   export GOOGLE_CLIENT_SECRET="tu-client-secret"
   python app.py
   ```

   (En Windows PowerShell usa `$env:GOOGLE_CLIENT_ID="..."`.)

Si no configuras las credenciales, el botón sigue visible pero avisa que no
está configurado, y el login con correo/contraseña funciona igual. **Consejo:**
si vas a demostrar Google en el examen, pruébalo antes; si algo falla en vivo,
usa correo y contraseña como respaldo.

> Nota técnica: la sesión real de la app sigue usando la tabla `sessions`
> propia (no `flask.session`). `flask.session` solo se usa para el paso
> temporal del handshake de Google (estado/nonce), como es estándar.

## Cómo agregar tus propias fotos

No hay que tocar código. Solo guarda las imágenes con el nombre correcto:

- **Fotos de platos** → `static/img/productos/<id-del-producto>.jpg`
  (instrucciones y el listado completo de ids están en
  `static/img/productos/LEEME.txt`)
- **Fotos/banner de cada restaurante** → `static/img/restaurantes/<slug>.jpg`
  (`club-de-golf.jpg`, `el-azteca.jpg`, `la-frankeria.jpg`)

Si el archivo no existe todavía, se muestra automáticamente un cuadro gris de
"Foto del producto/restaurante" en su lugar — el sitio nunca se rompe por
falta de imágenes.

## Mapa del sitio

| Ruta | Qué hace | Requiere login |
|---|---|---|
| `/` | Home: ofertas, restaurantes, recomendados | No |
| `/restaurante/<slug>` | Menú de un restaurante | No (ver), sí (agregar al carrito) |
| `/buscar?q=...` | Buscador de productos | No |
| `/ofertas` | Promociones activas | No |
| `/faq` | Preguntas frecuentes | No |
| `/contacto` | Formulario de contacto | No |
| `/register`, `/login`, `/logout` | Cuenta de usuario | — |
| `/carrito` | Ver/editar carrito | Sí |
| `/checkout` | Pago (simulado) | Sí |
| `/pedido/<id>` | Confirmación / recibo | Sí |
| `/tecnologia` | Ficha técnica del stack | No |

## Rúbrica — Comercio Electrónico (50 pts de elementos del sitio)

| Elemento pedido | Dónde está |
|---|---|
| Carrito de la compra | `/carrito`, `carrito_agregar/actualizar/eliminar` en `app.py` |
| Buscador efectivo | `/buscar` — busca por nombre, descripción, restaurante y sección |
| Página de preguntas frecuentes | `/faq` |
| Página de contacto | `/contacto` (formulario + info, guarda mensajes en SQLite) |
| Sistema de registro para el usuario | `/register` (ya cumplía la rúbrica de seguridad) |
| Sección con ofertas y promociones | `/ofertas` + destacadas en home |
| Recomendaciones de producto | Sección "Recomendados" en home y "También te podría gustar" en carrito |
| Sistema de pago | `/checkout` → valida tarjeta (formato) → `/pedido/<id>` con recibo |
| Software o aplicación utilizada | `/tecnologia` + este README |
| Otros (creatividad/originalidad) | Catálogo con datos reales de 3 restaurantes de Azuero, diseño propio tipo "recibo/menú de comida" |

## Rúbrica — Seguridad en el Desarrollo de Software

| Punto | Dónde | Cómo |
|---|---|---|
| Registro con correo y contraseña | `app.py: register()` | Formulario + validación |
| Hash con sal usando bcrypt (costo 10-12) | `register()` | `bcrypt.hashpw(pw, bcrypt.gensalt(rounds=12))` |
| Verificación de credenciales en login | `login()` | `bcrypt.checkpw(...)` |
| Session ID seguro | `generate_session_id()` | `secrets.token_hex(32)` (256 bits) |
| Cookies seguras | `set_session_cookie()` | `HttpOnly=True, Secure=True, SameSite='Lax'` |
| Timeout por inactividad (15 min) | `get_current_user()` | Compara `last_activity` en tabla `sessions` |
| Rotación de session ID tras login | `login()` | Se destruye cualquier sesión previa y se genera una nueva tras autenticar |

## Estructura

```
frankeria_app/
├── app.py                      # Rutas, auth, sesiones, carrito, pagos
├── menus.py                    # Catálogo real de los 3 restaurantes
├── requirements.txt
├── static/
│   ├── style.css
│   └── img/
│       ├── placeholder-producto.svg
│       ├── placeholder-restaurante.svg
│       ├── productos/          # ← pon aquí fotos de platos
│       └── restaurantes/       # ← pon aquí fotos/banners de restaurantes
└── templates/
    ├── base.html                (navbar + footer compartidos)
    ├── index.html                (home)
    ├── restaurant.html
    ├── buscar.html
    ├── ofertas.html
    ├── faq.html
    ├── contacto.html
    ├── carrito.html
    ├── checkout.html
    ├── pedido.html
    ├── tecnologia.html
    ├── login.html
    └── register.html
```
