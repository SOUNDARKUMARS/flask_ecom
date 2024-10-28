from flask import Blueprint,jsonify,request,g,url_for
from flask_jwt_extended import jwt_required,get_jwt_identity
from .models import Customer
from werkzeug.utils import secure_filename
from .models import Product
from . import db
import os
import cloudinary
import cloudinary.uploader

admin=Blueprint('admin',__name__)

cloudinary.config(
    cloud_name = 'dceod41m6',
    api_key = '976975349539932',
    api_secret = 'j7inJ9gzuSrokaNjlu6fS8cndFQ'
)

@admin.route('/current-user')
@jwt_required()
def current_user():
    return {'current user':g.user.id}


@admin.route('/userbase')
def getUserBase():
    users=Customer.query.all()
    return [user.__str__() for user in users]

# ADD SHOP ITEM
@admin.route('/add-shop-items',methods=['GET','POST'])
@jwt_required()
def add_shop_item():
    if g.user.email!='soundarkumarsaravanan@gmail.com':
        return {"error":"Access Denied"}        
    # temp_mod: replace the " " into "_" since " " not supported as args
    product_name=request.form.get('product_name')
    current_price=request.form.get('current_price')
    previous_price=request.form.get('previous_price')
    in_stock=request.form.get('in_stock')
    flash_sale=request.form.get('flash_sale')
    brand_name=request.form.get('brand_name')
    category_name=request.form.get('category_name')
    product_image=request.files.get('product_image')

    # return product_image.filename

    in_stock = int(in_stock)#instock str to int
    flash_sale = flash_sale.lower() == 'true'

    # product image url gen
    img_upload_res=cloudinary.uploader.upload(product_image)
    image_url=img_upload_res.get('secure_url')

    new_shop_item=Product()
    new_shop_item.product_name=product_name
    new_shop_item.current_price=current_price
    new_shop_item.previous_price=previous_price
    new_shop_item.in_stock=in_stock
    new_shop_item.flash_sale=flash_sale
    new_shop_item.brand_name=brand_name
    new_shop_item.category_name=category_name
    new_shop_item.product_img='ADD_IMAGE'
    new_shop_item.product_img=image_url

    try:
        db.session.add(new_shop_item)
        db.session.commit()
        return new_shop_item.__str__()
    except Exception as e:
        return {"error":f"Failed to add item: {e}"}
    

# GET, SORT and FILTER items
@admin.route('/shop-items',methods=['GET','POST'])
@jwt_required()
def get_shop_item():
    if g.user.email=='soundarkumarsaravanan@gmail.com':
        # sort_by and sortable_filters
        sort_by=request.args.get('sort_by')
        sortable_filters={
            'current_price':Product.current_price,
            'product_name':Product.product_name,
            "previous_price":Product.previous_price,
            "in_stock":Product.in_stock
        }

        # filters from req args
        category_filter=request.args.get('category_name')
        brand_filter=request.args.get('brand_name')
        min_price=request.args.get('min_price',type=float)
        max_price=request.args.get('max_price',type=float)
        in_stock=request.args.get('in_stock', type=bool)

        # split category_name and brand_name with comma as list
        category_filter_list=category_filter.split(',') if category_filter else None
        brand_filter_list=brand_filter.split(',') if brand_filter else None

        # base query
        query=Product.query

        if category_filter_list:
            query=query.filter(Product.category_name.in_(category_filter_list))
        if brand_filter_list:
            query=query.filter(Product.brand_name.in_(brand_filter_list))

        if min_price is not None:
            query=query.filter(Product.current_price>=min_price)
        if max_price is not None:
            query=query.filter(Product.current_price<=max_price)

        if in_stock is not None:
            if in_stock.lower()=='true':
                query.filter(Product.in_stock>0)
            else:
                query=query.filter(Product.in_stock==0)

        # apply sorting
        if sort_by and sort_by in sortable_filters:
            query=query.order_by(sortable_filters[sort_by])
        else:
            query=query.order_by(Product.date_added)

        items=query.all()
        return [item.__str__() for item in items]
    else:
        return {"error":"Access Denied"}
    

# UPDATE PRODUCT
@admin.route('/update-item/<int:item_id>',methods=["PUT"])
@jwt_required()
def update_shop_item(item_id):
    if g.user.email=='soundarkumarsaravanan@gmail.com':
        item=Product.query.get(item_id)
        if not item:
            return{'error':"product not found"}
        
        product_name=request.form.get('product_name')
        current_price=request.form.get('current_price')
        previous_price=request.form.get('previous_price')
        in_stock=request.form.get('in_stock')
        flash_sale=request.form.get('flash_sale')
        category_name=request.form.get('category_name')
        brand_name=request.form.get('brand_name')

        if product_name:
            item.product_name=product_name
        if current_price:
            item.current_price=current_price
        if previous_price:
            item.previous_price=previous_price
        if in_stock:
            item.in_stock=in_stock
        if flash_sale:
            item.flash_sale=flash_sale.lower()=='true'
        if brand_name:
            item.brand_name=brand_name
        if category_name:
            item.category_name=category_name

        try:
            db.session.commit()
            return {"message":"Item updated successfuly"}
        except Exception as e:
            return {"error":f"Failed to update item: {e}"},


    return {"error":"Access Denied"},403
    
@admin.route('/delete/<int:item_id>',methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    if g.user.email=='soundarkumarsaravanan@gmail.com':
        item=Product.query.get(item_id)
        # return item.__str__
        if not item:
            return {"error":"Item does not exists"}
        try:
            db.session.delete(item)
            db.session.commit()
            return {"message":"Item deleted"}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to delete item: {e}"},500
    else:
        {"error":"Access Denied"},403