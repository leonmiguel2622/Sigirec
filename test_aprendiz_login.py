import urllib.request
import urllib.parse
import re
import http.cookiejar

BASE = 'http://127.0.0.1:5000'

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [('User-Agent', 'test/1.0')]

# Probar login con cédula 1095308502 (Miguel Leon)
print('=== LOGIN CON CÉDULA 1095308502 (Miguel Leon) ===')

try:
    # Paso 1: Obtener página y CSRF
    r = op.open(BASE + '/login', timeout=15)
    html = r.read().decode('utf-8', 'replace')
    m = re.search(r'name="csrf-token"\s+content="([^"]+)"', html)
    csrf = m.group(1) if m else ''
    print('CSRF token:', csrf[:20] if csrf else 'NOT FOUND')
    
    # Paso 2: Login con cédula de Miguel Leon
    data = urllib.parse.urlencode({
        'numero_identificacion': '1095308502',
        'clave': 'SigiRec2026!',
        'csrf_token': csrf,
    }).encode()
    req = urllib.request.Request(BASE + '/login', data=data, 
                                  headers={'Content-Type': 'application/x-www-form-urlencoded'})
    r2 = op.open(req, timeout=15)
    url = r2.geturl()
    print('Redirect to:', url)
    print('LOGIN SUCCESSFUL')
except urllib.error.HTTPError as e:
    print('Login HTTP error:', e.code)
    body = e.read().decode('utf-8', 'replace')
    print('Error body:', body[:500])
except Exception as e:
    print('Error:', type(e).__name__, e)

print()

# Probar también con la cédula 3000000007 (Usuario de prueba 7)
print('=== LOGIN CON CÉDULA 3000000007 (Usuario prueba 7) ===')

cj2 = http.cookiejar.CookieJar()
op2 = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj2))
op2.addheaders = [('User-Agent', 'test/1.0')]

try:
    r = op2.open(BASE + '/login', timeout=15)
    html = r.read().decode('utf-8', 'replace')
    m = re.search(r'name="csrf-token"\s+content="([^"]+)"', html)
    csrf = m.group(1) if m else ''
    
    data = urllib.parse.urlencode({
        'numero_identificacion': '3000000007',
        'clave': 'SigiRec2026!',
        'csrf_token': csrf,
    }).encode()
    req = urllib.request.Request(BASE + '/login', data=data, 
                                  headers={'Content-Type': 'application/x-www-form-urlencoded'})
    r2 = op2.open(req, timeout=15)
    url = r2.geturl()
    print('Redirect to:', url)
    print('LOGIN SUCCESSFUL')
except urllib.error.HTTPError as e:
    print('Login HTTP error:', e.code)
    body = e.read().decode('utf-8', 'replace')
    print('Error body:', body[:500])
except Exception as e:
    print('Error:', type(e).__name__, e)