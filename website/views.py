from flask import Blueprint,request,g,jsonify
from .models import Product,Cart
from .import db
from flask_jwt_extended import jwt_required,get_jwt_identity
from sqlalchemy import or_
from .tasks import long_running_task

views=Blueprint('views',__name__)

@views.route('/')
def home():
    return "This is the home you are seeing!!!"


@views.route('/current-user')
def current_user():
    return{'curent user id':g.user.id,"current user mail":g.user.email}

# GET, SORT and FILTER items
@views.route('/shop-items',methods=['GET','POST'])
@jwt_required()

def get_shop_item():
        # sort_by and sortable_filters
    sort_by=request.args.get('sort_by')
    sortable_filters={
        'current_price':Product.current_price,
        'product_name':Product.product_name,
        "previous_price":Product.previous_price,
        "in_stock":Product.in_stock
    }

    # filters from req args
    search_query = request.args.get('search', '')
    category_filter=request.args.get('category_name')
    brand_filter=request.args.get('brand_name')
    min_price=request.args.get('min_price',type=float)
    max_price=request.args.get('max_price',type=float)
    in_stock=request.args.get('in_stock',)

    # split category_name and brand_name with comma as list
    category_filter_list=category_filter.split(',') if category_filter else None
    brand_filter_list=brand_filter.split(',') if brand_filter else None

    # base query
    query=Product.query

    if search_query:
            search_pattern = f"%{search_query}%"
            query = query.filter(
                or_(
                    Product.product_name.ilike(search_pattern),
                    Product.brand_name.ilike(search_pattern),
                    Product.category_name.ilike(search_pattern)
                )
            )

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

@views.route('/add-to-cart/<int:item_id>')
@jwt_required()
def add_to_cart(item_id):
    user_id=get_jwt_identity()
    
    item_exists=Cart.query.filter_by(product_link=item_id, customer_link=user_id).first()
    if item_exists:
        try:
            item_exists.quanity=item_exists.quanity+1
            db.session.commit()
            return {'message':f"{item_exists.product.product_name}'s quantity has been updated to {item_exists.quanity}."}
        except Exception as e:
            return{'error':f"Failed to update {item_exists.product.product_name}'s quantity : {e}"}
    
    new_cart_item=Cart(product_link=item_id,customer_link=user_id,quanity=1)
    try:
        db.session.add(new_cart_item)
        db.session.commit()
        return{'message':f'{new_cart_item.product.product_name} added cart'}
    except Exception as e:
        return {"error":f"Failed to add the item. {e}"}
    
@views.route('/delete-cart-item/<int:item_id>',methods=["DELETE"])
@jwt_required()
def remove_cart_item(item_id):
    item_to_remove=Cart.query.filter_by(product_link=item_id,customer_link=g.user.id).first()
    if item_to_remove:
        try:
            db.session.delete(item_to_remove)
            db.session.commit()
            return {'message': 'item removed from cart.'}, 200
        except Exception as e:
            return{'error':f"Failed to remove the item from cart: {e}"},500
    else:
        return{"error":"Item not found"},404
    
@views.route('/cart')
@jwt_required()
def get_cart_items():
    user_id=get_jwt_identity()

    cart_items=Cart.query.filter_by(customer_link=user_id)
    
    cart_total=0
    cart_data=[]
    for item in cart_items:
        item_total=item.product.current_price*item.quanity
        cart_total+=item_total
        cart_data.append({
            "Product_name":item.product.product_name,
            "quantity":item.quanity,
            "current_price":item.product.current_price,
            "item_total":item_total
        })

    return{
        "cart_total":cart_total,
        "cart_items":cart_data
    }

@views.route("/long-running-task/<int:number>",methods=["GET"])
def run_task(number):
    task=long_running_task.delay(number)
    return jsonify({"taks_id":"task.id", "status": "Task has been started!"}),202