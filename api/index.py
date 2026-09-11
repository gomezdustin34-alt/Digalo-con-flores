"""Punto de entrada para Vercel (funciones serverless de Python).

Vercel detecta la variable `app` de este módulo y la sirve como aplicación WSGI.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402

app = create_app()
