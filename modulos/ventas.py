# /modulos/ventas.py
from flask import Blueprint, render_template

ventas_bp = Blueprint('ventas', __name__, url_prefix='/ventas')

@ventas_bp.route('/')
def ventas():
    return "Página de Ventas"
