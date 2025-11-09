#!/bin/bash
cd /Users/brandonsandoval/Downloads/pons-auto
.venv/bin/python -m uvicorn pons.main:app --reload --host 127.0.0.1 --port 8001
