"""Apply the approved logo consistently without regenerating page content."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
site = root / 'dist'
header_old = '<img src="assets/logo.png" alt="Logo E & V"><span>E & V <small>SOLUCIONES INTEGRALES</small></span>'
header_new = '<img src="assets/ev-symbol-v2.png" alt="" width="66" height="66"><span class="brand-wordmark">E & V<small>SOLUCIONES INTEGRALES</small></span>'
footer_pattern = r'<a class="footer-brand" href="[^"]*">.*?</a>'
footer_new = '<a class="footer-brand" href="index.html" aria-label="E y V, inicio"><img src="assets/ev-symbol-v2.png" alt="" width="64" height="64" loading="lazy"><span class="footer-wordmark">E & V<small>SOLUCIONES INTEGRALES</small></span></a>'
for path in site.glob('*.html'):
    content = path.read_text(encoding='utf-8')
    content = content.replace(header_old, header_new)
    content = re.sub(footer_pattern, footer_new, content, count=1)
    content = re.sub(r'<link rel="icon"[^>]*>', '<link rel="icon" type="image/png" href="assets/ev-symbol-v2.png">', content)
    if 'href="brand.css"' not in content:
        content = content.replace('</head>', '<link rel="stylesheet" href="brand.css"></head>')
    path.write_text(content, encoding='utf-8')

# Keep the page authoring script from restoring the old header on a future run.
generator = root / 'scripts/expand_site.py'
content = generator.read_text(encoding='utf-8').replace(header_old, header_new)
generator.write_text(content, encoding='utf-8')
print('Updated logo, footer and favicon in all 6 pages.')
