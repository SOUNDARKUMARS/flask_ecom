from flask import Blueprint,jsonify
from datetime import datetime
from flask import request
from .models import Customer,OTPStore
from .import db
from flask_jwt_extended import create_access_token,jwt_required,get_jwt_identity
from datetime import timedelta
import random
import smtplib
from email.message import EmailMessage


auth=Blueprint('auth',__name__)

# Helper function to send OTP via email
def send_otp_email(recipient_email, otp):
    from_mail = 'soundarkumarsaravanan@gmail.com'
    email_password = 'tbva cpmb jepr eama'

    try:
        email_server = smtplib.SMTP('smtp.gmail.com', 587)
        email_server.starttls()
        email_server.login(from_mail, email_password)

        msg = EmailMessage()
        msg['Subject'] = 'OTP Verification'
        msg['From'] = from_mail
        msg['To'] = recipient_email
        msg.set_content(f"Your OTP is: {otp}")

        email_server.send_message(msg)
        email_server.quit()
    except Exception as e:
        print(f"Failed to send OTP email: {e}")

# OTP and email storage can be managed in-memory or in a proper session storage
otp_store = {}

# Login route with OTP verification
@auth.route('/login', methods=['POST'])
def login():
    user_otp = request.json.get('otp')
    email = request.json.get('email')
    
    if not user_otp or not email:
        return {"error": "OTP and email are required"}, 400

    current_user = Customer.query.filter_by(email=email).first()
    if not current_user:
        return {"error": "User not found"}, 404

    # Check if the OTP matches
    stored_otp=OTPStore.query.filter_by(email=email).first()
    
    if (datetime.utcnow()-stored_otp.created_at).total_seconds()>120:
        return {'error':"OTP expired"}
    
    if stored_otp.otp == str(user_otp):
        access_token = create_access_token(identity=current_user.id, expires_delta=timedelta(days=7))
        return {"access_token": access_token, "message": "Login successful"}, 200
    else:
        return {"error": "Invalid OTP"}, 400

# Route to send OTP for login
@auth.route('/send-otp', methods=['POST'])
def send_otp():
    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        return {"error": "Email and password are required"}, 400

    customer = Customer.query.filter_by(email=email).first()
    if customer and customer.verify_password(password):
        otp = str(random.randint(100000,999999))
        stored_otp=OTPStore.query.filter_by(email=email).first()
        if stored_otp:
            stored_otp.otp=otp
            db.session.commit()
        else:
            new_otp=OTPStore(email=email,otp=otp)
            db.session.add(new_otp)
            db.session.commit()

        # Send OTP via email
        send_otp_email(email, otp)
        return {"message": "OTP sent successfully"}, 200
    else:
        return {"error": "Invalid email or password"}, 400

# Registration with OTP verification to confirm email
@auth.route('/register', methods=['POST'])
def register():
    email = request.json.get('email').lower()
    username = request.json.get('username')
    password = request.json.get('password')
    confirm_password = request.json.get('confirm_password')

    if not email or not username or not password or not confirm_password:
        return {"error": "All fields are required"}, 400

    if password != confirm_password:
        return {"error": "Passwords do not match"}, 400

    existing_email = Customer.query.filter_by(email=email).first()
    if existing_email:
        return {"error": "This email is already registered, try logging in"}, 400

    # Send OTP to verify email before registering
    otp = str(random.randint(100000,999999))
    # Check if OTP already exists for the email
    existing_otp = OTPStore.query.filter_by(email=email).first()

    if existing_otp:
        # If OTP exists, update it with the new OTP and reset the creation time
        existing_otp.otp = otp
        existing_otp.created_at = datetime.utcnow()
        db.session.commit()
    else:
        # If no OTP exists, create a new OTP entry
        new_otp = OTPStore(email=email, otp=otp)
        db.session.add(new_otp)
        db.session.commit()
    
    send_otp_email(email, otp)

    return {"message": "otp_sent"}, 200

# Verify OTP for registration and create account
@auth.route('/verify-registration', methods=['POST'])
def verify_registration():
    email = request.json.get('email')
    username = request.json.get('username')
    password = request.json.get('password')
    user_otp = request.json.get('otp')
    otp_store[email]='heloo man'

    if not email or not username or not password or not user_otp:
        return {"error": "All fields are required"}, 400
    stored_otp=OTPStore.query.filter_by(email=email).first()
    if stored_otp is None or stored_otp.otp!=str(user_otp):
        return {"error":f'Invalid otp {stored_otp.otp}:{user_otp}'}
    if (datetime.utcnow()-stored_otp.created_at).total_seconds()>120: #expires after 120 seconds
        return {'error':"OTP expired"}

    # Create new customer account
    new_customer = Customer(email=email, username=username)
    new_customer.password = password

    try:
        db.session.add(new_customer)
        db.session.commit()
        otp_store.pop(email, None)  # Clear OTP after successful registration
        return {'message': 'Account created successfully'}, 201
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        return {"error": "Account creation failed. Try again with a different username"}, 500





@auth.route('/profile')
@jwt_required()
def profile():
    customer_id=get_jwt_identity()
    customer=Customer.query.filter_by(id=customer_id).first()
    if not customer:
        return jsonify({"error":"customer not found"}),404
    return {"customer":customer.__str__()}

@auth.route('/change-password',methods=['GET','POST'])
@jwt_required()
def change_password():
    current_password=request.json.get('current_password')
    new_password=request.json.get('new_password')
    confirm_new_password=request.json.get('confirm_new_password')

    # Validate that all required parameters are present
    if not current_password:
        return jsonify({'error': 'Current password is required'}), 400
    if not new_password:
        return jsonify({'error': 'New password is required'}), 400
    if not confirm_new_password:
        return jsonify({'error': 'Confirm new password is required'}), 400

    customer_id=get_jwt_identity()
    customer=Customer.query.filter_by(id=customer_id).first()
    if not customer:
        return jsonify({"error":"customer not found"}),404
    if customer.verify_password(current_password):
        if new_password==confirm_new_password:
            customer.password=confirm_new_password
            db.session.commit()
            return {'message':'password changed successfully'}
        else:
            return jsonify({'error':"passwords don't match"})
    else:
        return jsonify({'error':'the current password is incorrect'})
 


