from app.app import create_app
from app.settings import DevConfig, ProdConfig, os
from app.extensions import sio

# call config service
CONFIG = DevConfig if os.environ.get('FLASK_DEBUG') == '1' else ProdConfig

app = create_app(config_object=CONFIG)

if __name__ == '__main__':
    """Main Application
    python manage.py
    """
    sio.run(app, host='0.0.0.0', port=5000)
