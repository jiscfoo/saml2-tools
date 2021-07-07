# Invoke as: python start-authn-request.py <victim_sso_service_url>
# Then access: http://localhost:8080/

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import random
import string
from datetime import datetime, date, time, timezone
import html
import base64
import sys
import zlib
import urllib

hostName = "localhost"
serverPort = 8080
sso_url = sys.argv[1]

# https://docs.oasis-open.org/security/saml/v2.0/saml-authn-context-2.0-os.pdf
authn_classes = [
    "urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport",
    "urn:oasis:names:tc:SAML:2.0:ac:classes:Password",
    "urn:oasis:names:tc:SAML:2.0:ac:classes:Kerberos",
    "urn:oasis:names:tc:SAML:2.0:ac:classes:X509",
    "urn:oasis:names:tc:SAML:2.0:ac:classes:InternetProtocol",
    "https://refeds.org/profile/mfa",
]

request_template = '''<samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                    ID="__ID__"
                    Version="2.0"
                    IssueInstant="__NOW__"
                    ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                    Destination="__SSO_URL__"
                    AssertionConsumerServiceURL="__ACS__"
                    >
    <saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">__SP_ENTITYID__</saml:Issuer>
    <samlp:NameIDPolicy xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                        Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient"
                        AllowCreate="true"
                        />
    <samlp:RequestedAuthnContext xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" Comparison="exact">
        <saml:AuthnContextClassRef xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
            __AUTHN_CLASS__
        </saml:AuthnContextClassRef>
    </samlp:RequestedAuthnContext>
</samlp:AuthnRequest>'''

def random_string_generator(str_size):
    allowed_chars = string.ascii_letters + string.digits
    return ''.join(random.choice(allowed_chars) for x in range(str_size))


def create_request(sso_url, acs, sp_entityid, authn_class):
    id = random_string_generator(32)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    req = request_template.replace("__SSO_URL__", sso_url)\
        .replace("__ACS__", acs)\
        .replace("__SP_ENTITYID__", sp_entityid)\
        .replace("__AUTHN_CLASS__", authn_class)\
        .replace("__NOW__", now)\
        .replace("__ID__", id)

    return req

def deflate(b):
    compresser = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS, zlib.DEF_MEM_LEVEL, 0)
    out = compresser.compress(b)
    if out:
        return out
    out = compresser.flush()
    return out

def get_authn_class(qs):
    desired_class = qs.get("authn_class")
    if desired_class:
        if desired_class[0] in authn_classes:
            return desired_class[0]
        else:
            raise Exception("Unknown authn_class")
    return authn_classes[0]

def send_error(self, message, code = 500):
    self.send_response(code)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(bytes(message, "utf-8"))

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):

        acs = "https://test.ukfederation.org.uk/Shibboleth.sso/SAML2/POST"
        sp_entityid = "https://test.ukfederation.org.uk/entity"

        query_string = urllib.parse.parse_qs(self.path[2:])

        try:
            authn_class = get_authn_class(query_string)

            req = create_request(sso_url, acs, sp_entityid, authn_class)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<html><head><title>AuthN context launcher</title></head>", "utf-8"))
            self.wfile.write(bytes("<body>", "utf-8"))

            form_template = """<ul>"""
            for c in authn_classes:
                form_template += f"""  <li><a href="?authn_class={c}">{c}</a></li>"""
            form_template += """</ul>"""

            self.wfile.write(bytes(form_template, "utf-8"))
            self.wfile.write(bytes("<h1>SAML Authn Context launcher</h1>", "utf-8"))
            self.wfile.write(bytes("<pre>" + html.escape(req) + "</pre>", "utf-8"))
            self.wfile.write(bytes("<a href=\"" \
                + sso_url + "?SAMLRequest=" \
                + str(base64.urlsafe_b64encode(\
                    deflate(req.encode("utf-8"))
                ), "utf-8") \
                + "\">Go</a>", "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))

        except Exception as e:
            send_error(self, str(e.args))

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("> Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
