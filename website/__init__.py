from flask import Flask,jsonify,g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager,create_access_token,jwt_required,get_jwt_identity
from flask_migrate import Migrate
from config import Config
from .celery import celery_app

db=SQLAlchemy()
DB_NAME='database.sqlite3'

def create_database():
    db.create_all()
    print('Database Created!')

def create_app():
    app=Flask(__name__)
   
    app.config['SECRET_KEY']='efpn234nef0sdv34fvnwf'
    app.config['SQLALCHEMY_DATABASE_URI']=f'sqlite:///{DB_NAME}'
    app.config.from_object(Config)

    db.init_app(app)
    jwt=JWTManager(app)
    migrate=Migrate(app,db)

    @app.errorhandler(404)
    def page_not_found(error):
        return "This page is not found: 404,"

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({'error': 'Invalid token', 'message': reason}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token expired', 'message': 'The token has expired'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(reason):
        return jsonify({'error': 'Missing token', 'message': reason}), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token revoked', 'message': 'The token has been revoked'}), 401
    
    from .views import views
    from .auth import auth
    from .admin import admin

    app.register_blueprint(views,url_prefix='/')
    app.register_blueprint(auth,url_prefix='/auth')
    app.register_blueprint(admin,url_prefix='/admin')

    from .models import Customer

    @app.before_request
    @jwt_required(optional=True)
    def load_user():
        current_user_id=get_jwt_identity()
        current_user=Customer.query.get(current_user_id)
        if current_user_id:
            g.user=current_user
        else:
            g.user=None
    

    # with app.app_context(): #just before returning, create db once
    #     create_database()



    return app

__all__ = ['celery_app']