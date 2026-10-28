import urllib.request
import re
import http.cookiejar

BASE = 'http://127.0.0.1:5000'

# Login as aprendiz
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [('User-Agent', 'test')]

print('=== LOGIN ===')
try:
    r = op.open(BASE + '/login', timeout=15)
    html = r.read().decode('utf-8', 'replace')
    m = re.search(r'name="csrf-token"\s+content="([^"]+)"', html)
    csrf = m.group(1) if m else ''
    
    data = urllib.parse.urlencode({
        'numero_identificacion': '1095308502',
        'clave': 'SigiRec2026!',
        'csrf_token': csrf,
    }).encode()
    req = urllib.request.Request(BASE + '/login', data=data, 
                                  headers={'Content-Type': 'application/x-www-form-urlencoded'})
    r2 = op.open(req, timeout=15)
    url = r2.geturl()
    print(f'Redirect to: {url}')
except Exception as e:
    print(f'Login error: {e}')
    url = ''

print()
print('=== ESCANEAR PAGE ===')
if url and 'admin' not in url.lower():
    try:
        r3 = op.open(BASE + '/escanear', timeout=15)
        html3 = r3.read().decode('utf-8', 'replace')
        
        print('Escanear page loaded:', len(html3), 'bytes')
        
        # Check for z-index and position in HTML (though these are in CSS)
        print()
        print('=== Verificando CSS aplicado ===')
        
        # Look for the CSS classes we modified
        checks = ['z-index', 'position: relative', 'overflow: hidden']
        for check in checks:
            count = html3.lower().count(check.lower())
            print(f'  "{check}": aparece {count} veces en HTML')
        
        # Show relevant parts
        print()
        print('=== Primeras 20 líneas del HTML ===')
        for i, line in enumerate(html3.splitlines()[:30]):
            print(f'  {i+1}: {line.strip()[:100]}')
            
    except Exception as e:
        print(f'Error getting escanear: {e}')
else:
    print('No se pudo obtener la página de escáner')