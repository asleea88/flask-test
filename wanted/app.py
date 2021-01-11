import os
import logging

from flask import Flask
from views import wanted_api


def create_app():
    app = Flask(__name__)

    app.register_blueprint(wanted_api)

    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    db_uri = 'sqlite:///{}'.format(db_path)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from models import db
    db.init_app(app)

    from helpers import DatabaseInitialzier
    with app.app_context():
        db.drop_all()
        db.create_all()
        database_initializer = DatabaseInitialzier('wanted_temp_data.csv')
        database_initializer.init()

    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logging.root.setLevel(logging.INFO)

    return app


app = create_app()
