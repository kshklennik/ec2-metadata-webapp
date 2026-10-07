#!/bin/bash
set -euo pipefail
python3 -m py_compile webapp/app.py
mkdir -p dist
tar --exclude='__pycache__' -czf dist/webapp.tar.gz webapp
