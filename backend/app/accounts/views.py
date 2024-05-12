from flask import Blueprint, request, jsonify, url_for
from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies
from app.accounts.models import User
from app.db import db
from app import bcrypt
from app.mail import mail
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

accounts_bp = Blueprint("accounts", __name__)
s = URLSafeTimedSerializer('this-is-secret')


@accounts_bp.route('/register', methods=["POST"])
def register():
    data = request.get_json()
    password = data['password']
    email = data['email']
    verif_token = s.dumps(email, salt='email-verif')

    user = User.query.filter(User.email == email).first()
    print(user)
    print(verif_token)
    if user is None:
        print("Berhasil")
        user = User(
            email=email, password=bcrypt.generate_password_hash(password).decode('utf-8'))

        db.session.add(user)
        db.session.commit()

        msg = Message('Verify Your Email!', recipients=[email])
        link = url_for('accounts.verification',
                       verif_token=verif_token, _external=True)
        msg.body = "Click the link to verify your email! {}".format(link)
        mail.send(msg)

        print("Berhasil 2")
        response = jsonify(message="Succes register")
        return response, 200

    else:
        print("Makan tuh")
        return jsonify(message="Data sudah ada."), 400


@accounts_bp.route('/verification/<verif_token>')
def verification(verif_token):
    try:
        email = s.loads(verif_token, salt='email-verif', max_age=1800)
        user = User.query.filter(User.email == email).first()

        if user and user.is_verified == False:
            user.is_verified = True
            db.session.commit()
            return jsonify(email), 200
        elif user and user.is_verified == True:
            return jsonify("User is already verified"), 400
        else:
            return jsonify("User not found"), 404

    except SignatureExpired:
        return jsonify("the token is expired")


@accounts_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    password = data['password']
    email = data['email']

    user = User.query.filter(User.email == email).first()

    if user == None:
        return jsonify({"msg": "email not found"}), 400
    if bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=email)
        # refresh_token = create_refresh_token(identity=user.email)

        response = jsonify(message="Succes Login")
        set_access_cookies(response, access_token)
        # set_refresh_cookies(response, refresh_token)
        return response, 200
    else:
        return jsonify({"msg": "password invalid"}), 400