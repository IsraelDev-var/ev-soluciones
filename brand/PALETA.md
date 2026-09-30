# E & V · Soluciones integrales

Paleta aprobada el 29 de septiembre de 2026. Esta guía conserva las decisiones de marca para la web y próximas piezas de redes sociales.

| Color | HEX | RGB | Uso |
|---|---|---|---|
| Azul marino | #0D3044 | 13, 48, 68 | Logo, titulares y fondos de destacados |
| Naranja | #F69724 | 246, 151, 36 | Rayo, iconos, precios y promociones |
| Blanco suave | #FAFBF9 | 250, 251, 249 | Fondos y texto sobre azul |
| Gris claro | #C8CED0 | 200, 206, 208 | Líneas divisorias y detalles secundarios |

## Aplicación

- Colores principales: azul marino y naranja. Blanco y gris funcionan como apoyo.
- Posts: fondo blanco, titulares azules y acentos naranjas.
- Destacados: fondo azul marino, iconos naranjas y sin texto dentro de las portadas.
- Cabecera web: símbolo nuevo junto a E & V y el descriptor Soluciones integrales.
- Logo vigente (original): `brand/ev-symbol-v2.png`. El build genera las versiones optimizadas en `dist/assets/`. Es el símbolo aprobado sin textos y con fondo blanco. No es un PNG transparente.
- En fondos claros, la web usa mezcla multiply para integrar el blanco. En el pie oscuro se usa un soporte blanco circular, sin alterar los colores del logo.
- Conservar el símbolo sin estirarlo ni añadir efectos. Evitar la versión original con demasiados detalles y las propuestas con fondo cuadriculado.

## Tipografía y contacto

- Titulares: Barlow Condensed, peso 700–800.
- Texto: DM Sans.
- WhatsApp: +1 (829) 970-4893.
- Instagram: @espinosavargas.soluciones.
- Lema: Conectamos tu confort.
- Las promociones deben incluir el logo nuevo y el teléfono. Las portadas de destacados usan solo su icono, según la dirección aprobada.

Los cuatro colores base ya se aplican a través de las variables `--ink`, `--orange`, `--paper` y `--line` en `src/site.css`.
