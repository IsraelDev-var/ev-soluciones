"""Build the static site in dist/ from src/.

src/ is the only source of truth: never edit dist/ by hand, it is deleted on every build.
Run: python scripts/build.py   (requires Pillow)
"""
from datetime import date
from hashlib import sha256
from html import escape
from io import BytesIO
from pathlib import Path
from urllib.parse import quote
import json
import re

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
DIST = ROOT / 'dist'
ASSETS = DIST / 'assets'

site = json.loads((SRC / 'site.json').read_text(encoding='utf-8'))
services = json.loads((SRC / 'services.json').read_text(encoding='utf-8'))
catalog = json.loads((SRC / 'products.json').read_text(encoding='utf-8'))
BASE = site['url'].rstrip('/')
ORG_ID = BASE + '/#organizacion'
FONTS = 'https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=DM+Sans:wght@400;500;600;700&display=swap'


# ---------- assets: content-hashed names so Cloudflare can cache them forever ----------
asset_urls = {}

def emit(name, data):
    stem, ext = name.rsplit('.', 1)
    hashed = f'{stem}.{sha256(data).hexdigest()[:8]}.{ext}'
    (ASSETS / hashed).write_bytes(data)
    asset_urls[name] = '/assets/' + hashed
    return asset_urls[name]

def encode(image, fmt, **options):
    buffer = BytesIO()
    image.save(buffer, fmt, **options)
    return buffer.getvalue()

def build_images():
    logo = Image.open(ROOT / 'brand/ev-symbol-v2.png').convert('RGB')
    for size in (132, 180, 512):
        emit(f'ev-symbol-{size}.png', encode(logo.resize((size, size), Image.LANCZOS), 'PNG', optimize=True))
    emit('ev-symbol-132.webp', encode(logo.resize((132, 132), Image.LANCZOS), 'WEBP', quality=90))
    # Stable names: browsers and crawlers request these paths directly.
    (DIST / 'favicon.ico').write_bytes(encode(logo, 'ICO', sizes=[(16, 16), (32, 32), (48, 48)]))
    (DIST / 'apple-touch-icon.png').write_bytes(encode(logo.resize((180, 180), Image.LANCZOS), 'PNG', optimize=True))

    # The hero is always shown in grayscale: bake it in instead of a CSS filter.
    hero = ImageOps.grayscale(Image.open(SRC / 'img/electricidad.jpg')).convert('RGB')
    for width in (800, 1600):
        resized = hero.resize((width, round(hero.height * width / hero.width)), Image.LANCZOS)
        emit(f'hero-{width}.webp', encode(resized, 'WEBP', quality=72))
        emit(f'hero-{width}.jpg', encode(resized, 'JPEG', quality=74, optimize=True, progressive=True))

    # Social preview (1200x630) for WhatsApp, Facebook and X.
    og = Image.new('RGB', (1200, 630), '#0d3044')
    draw = ImageDraw.Draw(og)
    draw.ellipse((90, 175, 370, 455), fill='#fafbf9')
    og.paste(logo.resize((230, 230), Image.LANCZOS), (115, 200))
    fonts_dir = Path('C:/Windows/Fonts')
    def font(name, size):
        try:
            return ImageFont.truetype(str(fonts_dir / name), size)
        except OSError:
            return ImageFont.load_default(size)
    draw.text((430, 190), 'E & V', font=font('impact.ttf', 120), fill='#fafbf9')
    draw.text((434, 330), 'SOLUCIONES INTEGRALES', font=font('arialbd.ttf', 34), fill='#f69724')
    draw.text((434, 390), 'Electricidad · Climatización', font=font('arial.ttf', 32), fill='#c8ced0')
    draw.text((434, 432), 'Ventanas y puertas · Electromecánica', font=font('arial.ttf', 32), fill='#c8ced0')
    draw.rectangle((0, 610, 1200, 630), fill='#f69724')
    emit('og-image.jpg', encode(og, 'JPEG', quality=85, optimize=True))

def build_code():
    css = (SRC / 'site.css').read_text(encoding='utf-8')
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    css = re.sub(r'\s*\n\s*', '', css)
    emit('site.css', css.encode())
    emit('site.js', (SRC / 'site.js').read_bytes())


# ---------- shared layout ----------
NAV = [('/#servicios', 'Servicios', None), ('/tienda', 'Tienda', 'tienda'), ('/#nosotros', 'Nosotros', None), ('/#proceso', 'Cómo trabajamos', None)]

def header(current):
    links = ''.join(f'<a href="{href}"{" aria-current=\"page\"" if key and key == current else ""}>{label}</a>' for href, label, key in NAV)
    return (f'<a class="skip-link" href="#contenido">Saltar al contenido</a><header><a class="brand" href="/" aria-label="E y V, inicio">'
            f'<picture><source type="image/webp" srcset="{asset_urls["ev-symbol-132.webp"]}"><img src="{asset_urls["ev-symbol-132.png"]}" alt="" width="66" height="66"></picture>'
            '<span class="brand-wordmark">E &amp; V<small>SOLUCIONES INTEGRALES</small></span></a>'
            '<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="main-nav">Menú</button>'
            f'<nav id="main-nav" aria-label="Navegación principal">{links}</nav>'
            '<a class="button small header-quote" href="/#contacto">Cotiza tu proyecto</a></header>')

def footer():
    return ('<footer><div class="footer-top"><a class="footer-brand" href="/" aria-label="E y V, inicio">'
            f'<img src="{asset_urls["ev-symbol-132.png"]}" alt="" width="64" height="64" loading="lazy">'
            '<span class="footer-wordmark">E &amp; V<small>SOLUCIONES INTEGRALES</small></span></a>'
            '<p>Soluciones eléctricas, climatización,<br>ventanas y puertas.</p>'
            f'<a href="{site["instagram"]}" target="_blank" rel="noopener">Instagram</a><a href="#inicio">Volver al inicio</a></div>'
            '<div class="footer-word" aria-hidden="true">TU CONFORT.</div>'
            '<div class="footer-bottom"><span>© <span id="year">' + str(date.today().year) + '</span> E &amp; V Soluciones.</span><span>CONECTAMOS TU CONFORT</span></div></footer>')

def organization():
    return {
        '@type': 'HomeAndConstructionBusiness', '@id': ORG_ID, 'name': site['name'], 'legalName': site['legal_name'],
        'slogan': site['slogan'], 'url': BASE + '/', 'telephone': site['phone'],
        'logo': BASE + asset_urls['ev-symbol-512.png'], 'image': BASE + asset_urls['og-image.jpg'],
        'sameAs': [site['instagram']], 'address': {'@type': 'PostalAddress', 'addressCountry': site['country']},
        'areaServed': {'@type': 'Country', 'name': 'República Dominicana'},
        'contactPoint': {'@type': 'ContactPoint', 'telephone': site['phone'], 'contactType': 'customer service', 'availableLanguage': 'es'},
    }

def breadcrumbs(trail):
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i, 'name': name, 'item': BASE + path} for i, (name, path) in enumerate(trail, 1)]}

def page(key, path, main, graph=(), current=None, indexable=True):
    meta = site['pages'][key]
    url = BASE + path
    title, description = escape(meta['title']), escape(meta['description'], quote=True)
    ld = json.dumps({'@context': 'https://schema.org', '@graph': [organization(), *graph]}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    head = (
        '<!doctype html>\n<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{title}</title><meta name="description" content="{description}">'
        + (f'<link rel="canonical" href="{url}">' if indexable else '<meta name="robots" content="noindex">')
        + '<meta name="theme-color" content="#0d3044">'
        f'<meta property="og:type" content="website"><meta property="og:locale" content="{site["locale"]}"><meta property="og:site_name" content="E &amp; V Soluciones Integrales">'
        f'<meta property="og:title" content="{title}"><meta property="og:description" content="{description}"><meta property="og:url" content="{url}">'
        f'<meta property="og:image" content="{BASE + asset_urls["og-image.jpg"]}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
        '<meta name="twitter:card" content="summary_large_image">'
        f'<link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="icon" type="image/png" href="{asset_urls["ev-symbol-180.png"]}"><link rel="apple-touch-icon" href="/apple-touch-icon.png">'
        '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        f'<link rel="stylesheet" href="{FONTS}"><link rel="stylesheet" href="{asset_urls["site.css"]}">'
        f'<script src="{asset_urls["site.js"]}" defer></script>'
        f'<script type="application/ld+json">{ld}</script></head>\n'
    )
    main = re.sub(r'\{\{asset:([^}]+)\}\}', lambda m: asset_urls[m.group(1)], main)
    main = main.replace('<main id="inicio">', '<main id="contenido">', 1)
    return head + f'<body id="inicio">{header(current)}\n{main}\n{footer()}</body></html>\n'

def write(name, html):
    (DIST / name).write_text(html, encoding='utf-8')


# ---------- pages ----------
def whatsapp(text):
    return f'https://wa.me/{site["whatsapp"]}?text=' + quote(text)

def build_home():
    main = (SRC / 'pages/index.html').read_text(encoding='utf-8')
    graph = [{'@type': 'WebSite', '@id': BASE + '/#sitio', 'url': BASE + '/', 'name': site['name'], 'inLanguage': 'es', 'publisher': {'@id': ORG_ID}}]
    write('index.html', page('index', '/', main, graph))

def build_service(number, s):
    cards = ''.join(f'<article><span class="label">{i:02d}</span><h3>{escape(item["title"])}</h3><p>{escape(item["text"])}</p></article>' for i, item in enumerate(s['items'], 1))
    faqs = ''.join(f'<details><summary>{escape(f["q"])}</summary><p>{escape(f["a"])}</p></details>' for f in s['faqs'])
    link = whatsapp(f'Hola, E & V. Quiero consultar sobre {s["name"].lower()}.')
    main = f'''<main id="inicio"><section class="detail-hero frame"><nav class="breadcrumbs" aria-label="Ruta de navegación"><a href="/">Inicio</a><span aria-hidden="true">/</span><a href="/#servicios">Servicios</a><span aria-hidden="true">/</span><span aria-current="page">{s['name']}</span></nav><span class="label">SERVICIO {number:02d} / E &amp; V</span><h1>{s['title']}</h1><div class="detail-intro"><p>{s['intro']}</p><a class="button" href="{link}" target="_blank" rel="noopener">Consultar este servicio</a></div></section>
<section class="detail-scope frame"><div class="section-heading"><span class="label">EL ALCANCE</span><h2>¿EN QUÉ TE AYUDAMOS?</h2></div><div class="scope-grid">{cards}</div></section>
<section class="detail-context frame"><div><span class="label">PARA TU PROYECTO</span><h2>UNA SOLUCIÓN<br>PARA TU ESPACIO.</h2><p>{s['when']}</p></div><aside><span class="label">ANTES DE COTIZAR</span><h3>Cuéntanos los detalles.</h3><p>{s['prepare']}</p><p class="scope-note">El alcance, los materiales, el costo y los plazos se acuerdan en la cotización.</p><a class="text-link" href="{link}" target="_blank" rel="noopener">Hablar con E &amp; V</a></aside></section>
<section class="faqs frame"><div><span class="label">RESOLVEMOS TUS DUDAS</span><h2>ANTES DE<br>EMPEZAR.</h2></div><div>{faqs}</div></section>
<section class="related-shop frame"><div><span class="label">SERVICIOS + PRODUCTOS</span><h2>COMPLETA TU PROYECTO.</h2><p>Consulta los productos relacionados y la posibilidad de incluir su instalación.</p></div><a class="button" href="/tienda?categoria={s['category']}">Ver productos relacionados</a></section></main>'''
    path = '/' + s['slug']
    graph = [
        {'@type': 'Service', 'name': s['name'], 'description': site['pages'][s['slug']]['description'], 'provider': {'@id': ORG_ID},
         'areaServed': {'@type': 'Country', 'name': 'República Dominicana'}, 'url': BASE + path,
         'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': s['name'], 'itemListElement': [
             {'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': item['title'], 'description': item['text']}} for item in s['items']]}},
        {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': f['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': f['a']}} for f in s['faqs']]},
        breadcrumbs([('Inicio', '/'), ('Servicios', '/#servicios'), (s['name'], path)]),
    ]
    write(s['slug'] + '.html', page(s['slug'], path, main, graph))

def build_shop():
    names = catalog['categories']
    cards = ''.join(
        f'<article class="product-card" data-category="{p["category"]}" data-name="{escape(p["name"])}"><div class="product-family"><span class="label">{names[p["category"]]}</span>'
        f'<span class="product-index" aria-hidden="true">{i:02d}</span><h2>{p["name"]}</h2></div><div class="product-body"><h3>{p["subtitle"]}</h3><p>{p["description"]}</p>'
        f'<span class="availability">Precio y disponibilidad por consultar</span><button class="button product-add" type="button" data-product="{escape(p["name"])}">Añadir a mi consulta<span class="sr-only">: {escape(p["name"])}</span></button></div></article>'
        for i, p in enumerate(catalog['products'], 1))
    filters = ''.join(f'<button type="button" data-filter="{key}" aria-pressed="false">{label}</button>' for key, label in names.items())
    main = f'''<main id="inicio"><section class="shop-hero frame"><nav class="breadcrumbs" aria-label="Ruta de navegación"><a href="/">Inicio</a><span aria-hidden="true">/</span><span aria-current="page">Tienda</span></nav><span class="label">E &amp; V / TIENDA</span><h1>PRODUCTOS PARA<br><span>TU PROYECTO.</span></h1><div class="shop-intro"><p>Explora por categoría y cuéntanos qué necesitas. Confirmamos referencias, precios y disponibilidad contigo por WhatsApp.</p><a class="text-link" href="#mi-consulta">Mi consulta (<span data-cart-count>0</span>)</a></div></section>
<section class="shop-catalog frame" aria-label="Catálogo de productos"><div class="shop-toolbar"><div class="category-filters" role="group" aria-label="Filtrar por categoría"><button type="button" data-filter="todos" aria-pressed="true">Todos</button>{filters}</div><p id="product-count" role="status">{len(catalog['products'])} categorías de productos</p></div><div class="product-grid">{cards}</div></section>
<section class="inquiry frame" id="mi-consulta"><div><span class="label">TU SELECCIÓN</span><h2>PREPAREMOS<br>TU CONSULTA.</h2><p>Añade los productos que te interesan y la cantidad aproximada. Revisaremos contigo las opciones y los detalles antes de acordar la compra.</p><div class="inquiry-help"><h3>¿También necesitas instalación?</h3><p>Inclúyela en tu consulta para revisar el producto y el servicio en conjunto.</p></div></div><form id="shop-inquiry"><div id="cart-items"><p class="cart-empty">Tu consulta está vacía. Añade una categoría de producto para comenzar.</p></div><div id="cart-fields" hidden><label for="shop-notes">Especificaciones o detalles del proyecto</label><textarea id="shop-notes" name="notes" rows="3" maxlength="1200" placeholder="Modelo, medidas, potencia o la referencia que buscas…"></textarea><label class="check-label"><input type="checkbox" id="include-installation"> También quiero consultar la instalación</label><button class="button" type="submit">Consultar selección por WhatsApp</button><p class="form-note">Se abrirá WhatsApp para revisar y enviar tu mensaje. Esta consulta no reserva productos ni confirma un pedido.</p></div></form></section><p class="shop-feedback" role="status" aria-live="polite" id="shop-feedback"></p></main>'''
    graph = [breadcrumbs([('Inicio', '/'), ('Tienda', '/tienda')]),
             {'@type': 'ItemList', 'name': 'Categorías de productos', 'itemListElement': [
                 {'@type': 'ListItem', 'position': i, 'name': p['name']} for i, p in enumerate(catalog['products'], 1)]}]
    write('tienda.html', page('tienda', '/tienda', main, graph, current='tienda'))

def build_meta_files():
    paths = ['/', *('/' + s['slug'] for s in services), '/tienda']
    today = date.today().isoformat()
    urls = ''.join(f'<url><loc>{BASE}{p}</loc><lastmod>{today}</lastmod></url>' for p in paths)
    write('sitemap.xml', f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    write('robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n')
    write('_headers', '''/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: DENY
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Content-Security-Policy: default-src 'self'; script-src 'self' https://static.cloudflareinsights.com; style-src 'self' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self' https://cloudflareinsights.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'

/assets/*
  Cache-Control: public, max-age=31536000, immutable
''')


if __name__ == '__main__':
    # Empty dist/ but keep the folders: synced drives (OneDrive) can lock them.
    for old in sorted(DIST.rglob('*'), reverse=True):
        old.rmdir() if old.is_dir() and old != ASSETS else old.unlink() if old.is_file() else None
    ASSETS.mkdir(parents=True, exist_ok=True)
    build_images()
    build_code()
    build_home()
    for number, service in enumerate(services, 1):
        build_service(number, service)
    build_shop()
    write('404.html', page('404', '/404', (SRC / 'pages/404.html').read_text(encoding='utf-8'), indexable=False))
    build_meta_files()
    total = sum(f.stat().st_size for f in DIST.rglob('*') if f.is_file())
    print(f'dist/ built: {sum(1 for _ in DIST.rglob("*.html"))} pages, {total / 1024:.0f} KB total')
