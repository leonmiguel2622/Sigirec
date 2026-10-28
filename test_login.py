import urllib.request
import urllib.parse
import re
import http.cookiejar

BASE = 'http://127.0.0.1:5000'

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [('User-Agent', 'test/1.0')]

print('=== PASO 1: Obtener página de login y CSRF ===')
try:
    r = op.open(BASE + '/login', timeout=15)
    html = r.read().decode('utf-8', 'replace')
    m = re.search(r'name="csrf-token"\s+content="([^"]+)"', html)
    csrf = m.group(1) if m else ''
    print('CSRF token:', csrf[:20] if csrf else 'NOT FOUND')
    print('Página de login cargada OK')
except Exception as e:
    print('Error getting login page:', e)
    csrf = ''

print()
print('=== PASO 2: Intentar login con credenciales 0000000000 / SigiRec2026! ===')
if csrf:
    try:
        data = urllib.parse.urlencode({
            'numero_identificacion': '0000000000',
            'clave': 'SigiRec2026!',
            'csrf_token': csrf,
        }).encode()
        req = urllib.request.Request(BASE + '/login', data=data, 
                                      headers={'Content-Type': 'application/x-www-form-urlencoded'})
        r2 = op.open(req, timeout=15)
        url = r2.geturl()
        print('Redirect to:', url)
        print('LOGIN SUCCESSFUL - No error')
    except urllib.error.HTTPError as e:
        print('Login HTTP error:', e.code)
        body = e.read().decode('utf-8', 'replace')
        print('Error body:', body[:500])
    except Exception as e:
        print('Login error:', type(e).__name__, e)
else:
    print('No se pudo obtener CSRF token')