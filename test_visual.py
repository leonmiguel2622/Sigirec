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
    # Get escanear page
    try:
        r3 = op.open(BASE + '/escanear', timeout=15)
        html3 = r3.read().decode('utf-8', 'replace')
        
        # Check for CSS-related content
        print('Escanear page loaded:', len(html3), 'bytes')
        
        # Look for camera-related elements
        checks = ['camera-wrapper', 'min-height', 'aspect-ratio', 'scan-frame', 'scan-button']
        for check in checks:
            if check in html3.lower():
                print(f'  ✓ {check} found in page')
            else:
                print(f'  ✗ {check} NOT found in page')
        
        # Show first 500 chars of HTML related to camera
        print()
        print('=== Primeros 500 chars del HTML ===')
        for line in html3.splitlines()[:50]:
            if any(x in line.lower() for x in ['camera', 'min-height', 'aspect', 'wrapper', 'scan']):
                print(f'  {line.strip()[:120]}')
                
    except Exception as e:
        print(f'Error getting escanear: {e}')
else:
    print('No se pudo obtener la página de escáner (puede que ya esté en admin)')