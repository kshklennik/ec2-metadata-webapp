import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, build_opener, ProxyHandler

METADATA = "http://169.254.169.254"
# Access metadata directly, without using proxy environment variables.
opener = build_opener(ProxyHandler({}))


def fetch(path, method="GET", headers=None):
    request = Request(
        METADATA + path,
        method=method,
        headers=headers or {},
    )
    with opener.open(request, timeout=3) as response:
        return response.read().decode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return

        try:
            token = fetch(
                "/latest/api/token",
                method="PUT",
                headers={"X-aws-ec2-metadata-token-ttl-seconds": "60"},
            )
            headers = {"X-aws-ec2-metadata-token": token}

            result = {
                "region": fetch(
                    "/latest/meta-data/placement/region", headers=headers
                ),
                "availabilityZone": fetch(
                    "/latest/meta-data/placement/availability-zone",
                    headers=headers,
                ),
            }
            body = json.dumps(result).encode()
            status = 200
        except Exception:
            body = b'{"error":"EC2 metadata unavailable"}'
            status = 503

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 80), Handler).serve_forever()
