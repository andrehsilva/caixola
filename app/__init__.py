# app/__init__.py
import os
from flask import Flask
from markupsafe import Markup
from . import commands

# Importando as extensões
from .extensions import db, migrate, login_manager
from config import config_by_name

def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)

    # --- Configuração ---
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config_by_name[config_name])
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

    # --- Inicialização das Extensões ---
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Registra os comandos CLI
    commands.register_commands(app)

    # --- Blueprints e Componentes ---
    with app.app_context():
        from . import models
        
        # Importa e registra os Blueprints
        from .main import bp as main_bp
        app.register_blueprint(main_bp)
        from .auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
        from .dashboard import bp as dashboard_bp
        app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

        # ✅ FILTRO PARA QUEBRA DE LINHA
        @app.template_filter('nl2br')
        def nl2br_filter(s):
            return Markup(s.replace('\n', '<br>')) if s else ''

        # ✅ INJETOR DE URL DO SUPABASE (Para funcionar nos HTMLs)
        @app.context_processor
        def inject_media_url():
            from app.utils import get_media_url
            return dict(get_media_url=get_media_url)

        @login_manager.user_loader
        def load_user(user_id):
            return models.User.query.get(int(user_id))

    return app