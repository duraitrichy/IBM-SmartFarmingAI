"""Routes package — registers all Flask blueprints."""

from flask import Flask


def register_routes(app: Flask) -> None:
    from .main import main_bp
    from .chat import chat_bp
    from .weather import weather_bp
    from .crop import crop_bp
    from .soil import soil_bp
    from .pest import pest_bp
    from .market import market_bp
    from .profile import profile_bp
    from .reports import reports_bp
    from .api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp, url_prefix="/chat")
    app.register_blueprint(weather_bp, url_prefix="/weather")
    app.register_blueprint(crop_bp, url_prefix="/crop")
    app.register_blueprint(soil_bp, url_prefix="/soil")
    app.register_blueprint(pest_bp, url_prefix="/pest")
    app.register_blueprint(market_bp, url_prefix="/market")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(reports_bp, url_prefix="/report")
    app.register_blueprint(api_bp, url_prefix="/api")
