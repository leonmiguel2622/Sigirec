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
        
        # Check CSS-related stuff in HTML
        print()
        print('=== Verificando estilos en la página ===')
        checks = ['height: 400', 'min-height', 'camera-wrapper', 'overflow: hidden']
        for check in checks:
            # Search in a case-insensitive way
            if check.lower() in html3.lower():
                # Find the line
                for line in html3.splitlines():
                    if check.lower() in line.lower():
                        print(f'  Encontrado: {line.strip()[:100]}')
                        break
            else:
                print(f'  No encontrado: {check}')
        
        # Show camera-related lines
        print()
        print('=== Líneas relacionadas con cámara ===')
        for line in html3.splitlines()[:200]:
            lower = line.lower()
            if any(x in lower for x in ['camera', 'min-height', 'max-height', 'wrapper', 'aspect']):
                print(f'  {line.strip()[:120]}')
                
    except Exception as e:
        print(f'Error getting escanear: {e}')
else:
    print('No se pudo obtener la página de escáner')