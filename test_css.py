import urllib.request
import urllib.error
import re
import http.cookiejar

BASE = 'http://127.0.0.1:5000'

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [('User-Agent', 'test')]

try:
    r = op.open(BASE + '/login', timeout=15)
    html = r.read().decode('utf-8', 'replace')
    
    # Login with learner credentials
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
    print('Redirect to:', r2.geturl())
    
    # Now go to escanear
    r3 = op.open(BASE + '/escanear', timeout=15)
    html3 = r3.read().decode('utf-8', 'replace')
    
    # Check for camera wrapper in rendered HTML
    if 'camera-wrapper' in html3.lower():
        print('camera-wrapper found in page HTML')
    if 'min-height' in html3.lower():
        print('min-height found in page HTML')
    if 'aspect-ratio' in html3.lower():
        print('aspect-ratio found in page HTML')
        
    # Show relevant CSS-related content
    for line in html3.splitlines()[:150]:
        if 'camera' in line.lower() or 'style' in line.lower() or 'wrapper' in line.lower() or 'min-height' in line.lower() or 'aspect' in line.lower():
            print('HTML line:', line.strip()[:120])
            
except Exception as e:
    print('Error:', e)