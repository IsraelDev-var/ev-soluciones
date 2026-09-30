# E & V · Soluciones integrales

Sitio estático publicado como Cloudflare Worker (`wrangler.jsonc`), que sirve la carpeta `dist/`. Cada push a `main` se despliega solo.

## Estructura

```
src/                 Fuente del sitio (lo único que se edita)
  site.json          Dominio, contacto y title/description SEO de cada página
  services.json      Contenido de las 4 páginas de servicio
  products.json      Categorías de la tienda
  pages/index.html   Contenido de la portada
  pages/404.html     Página de error
  site.css, site.js  Estilos y comportamiento
  img/               Fotos originales
brand/               Guía de marca y logo original
scripts/build.py     Genera dist/ (HTML, imágenes optimizadas, sitemap, robots, _headers)
dist/                Resultado del build: no editar a mano
```

## Construir

```bash
pip install pillow
python scripts/build.py
```

Luego haz commit de `src/` y `dist/`. Cloudflare publica `dist/` (sin comando de build).

- Antes del primer despliegue, pon el dominio real en `src/site.json` → `url` (lo usan el canonical, Open Graph y el sitemap).
- Las URLs son limpias (`/electricidad`, `/tienda`): Cloudflare sirve `electricidad.html` en esa ruta.
- Los archivos de `dist/assets/` llevan un hash en el nombre, así que se cachean un año (`_headers`).
- Vista previa local con URLs limpias: `npx wrangler dev`.
