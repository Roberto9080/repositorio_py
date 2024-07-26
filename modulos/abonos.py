# /modulos/abonos.py
from flask import Blueprint, render_template

abonos_bp = Blueprint('abonos', __name__, url_prefix='/abonos')

@abonos_bp.route('/')
def abonos():
    return "Página de Abonos"
