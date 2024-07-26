# /modulos/__init__.py
from flask import Blueprint

clientes_bp = Blueprint('clientes', __name__)
abonos_bp = Blueprint('abonos', __name__)
ventas_bp = Blueprint('ventas', __name__)


from . import clientes, abonos, ventas
