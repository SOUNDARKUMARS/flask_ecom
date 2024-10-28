from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash


class Customer(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(100),unique=True)
    username=db.Column(db.String(100),nullable=False)
    password_hash=db.Column(db.String(150),nullable=False)
    date_joined=db.Column(db.DateTime,default=datetime.utcnow)

    cart_items=db.relationship('Cart', backref=db.backref('customer',lazy=True))
    orders=db.relationship('Order', backref=db.backref('customer',lazy=True))

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password=password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password=password)
    
    def __str__(self):
        return {
            "id":self.id,
            "username":self.username,
            "email":self.email,
            "date_joined":self.date_joined
        }
    
    
class Product(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    product_name=db.Column(db.String(100),nullable=False)
    current_price=db.Column(db.Float,nullable=False)
    previous_price=db.Column(db.Float,nullable=False)
    in_stock=db.Column(db.Integer,nullable=False)
    product_img=db.Column(db.String(1000),nullable=False)
    flash_sale=db.Column(db.Boolean,default=False)
    date_added=db.Column(db.DateTime,default=datetime.utcnow)

    brand_name=db.Column(db.String(40),nullable=False)
    category_name=db.Column(db.String(40),nullable=False)

    carts=db.relationship('Cart',backref=db.backref('product',lazy=True))
    orders=db.relationship('Order',backref=db.backref('product',lazy=True))

    def __str__(self):
        return {
            "id":self.id,
            "product_name":self.product_name,
            "current_price":self.current_price,
            "previous_price":self.previous_price,
            "brand_name":self.brand_name,
            "category_name":self.category_name,
            "in_stock":self.in_stock,
            "product_img":self.product_img,
            "flash_sale":self.flash_sale,
            "date_added":self.date_added,
        }
    
    # temp_mod:change the column quanity to quantity
class Cart(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    quanity=db.Column(db.Integer,nullable=False)

    customer_link=db.Column(db.Integer, db.ForeignKey('customer.id'),nullable=False)
    product_link=db.Column(db.Integer, db.ForeignKey('product.id', ondelete='cascade'),nullable=False)

    def __str__(self):
        return {
            "id":self.id,
            "quanity":self.quanity,
            "product_id":self.product_link,
            "product_name":self.product.product_name,
            "product_brand":self.product.brand_name
        }


class OTPStore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    
    # temp_mod:change the column quanity to quantity
class Order(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    quanity=db.Column(db.Integer,nullable=False)
    price=db.Column(db.Float,nullable=False)
    status=db.Column(db.String(100),nullable=False)
    payment_id=db.Column(db.String(1000),nullable=False)

    customer_link=db.Column(db.Integer,db.ForeignKey('customer.id'),nullable=False)
    product_link=db.Column(db.Integer,db.ForeignKey('product.id'),nullable=False)

    def __str__(self):
        return '<Order %r>' %self.id 