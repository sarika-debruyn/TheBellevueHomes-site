#!/bin/sh
set -eu

python3 tools/seo_audit.py
python3 tools/seo_live_audit.py
