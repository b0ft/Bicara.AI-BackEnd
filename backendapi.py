from flask import Flask,current_app, Response, request, make_response, jsonify,flash,redirect,url_for,Blueprint
import pymongo
import json
from bson.objectid import ObjectId
from flask_mail import Mail, Message
import urllib.request
import bcrypt
from flask_cors import CORS
from werkzeug.utils import secure_filename
from collections import Counter
import vidProcess
import os
from datetime import datetime
import random

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
RESULT_FOLDER = 'static/results/'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'bicaraai.team@gmail.com'
app.config['MAIL_PASSWORD'] = 'soqkvyelnvhlvbdz'
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
CORS(app)
mail = Mail(app)

api = Blueprint('api', __name__, url_prefix='/api')
try:
    mongo = pymongo.MongoClient(host="mongodb://localhost:27017",serverSelectionTimeoutMS = 3000,connect=False) # connect = False for deployment purpose and connect = True for only development purpose
    db = mongo.bicara_ai
except:
    print("ERROR - Cannot connect to database")

@api.route('/', methods=['POST', 'GET'])
def notify_user():
    if request.method == 'POST':
        try:
            email = request.json['email'] 
            user = {"email": email}
            msg = Message('Hello', sender = 'noreply@demo.com', recipients = [email])
            msg.body = "Terimakasih sudah mendaftarkan email anda di Bicara AI. Kami akan mengirimkan email kepada anda ketika produk kami sudah siap."
            mail.send(msg)
            findEmail = db.users.find_one(user)
            if findEmail :
                return Response(response = json.dumps({"message": "Thank you for your registration. Your email will be notified once the product is fully launched."}), status = 200, mimetype="application/json")
            dbResponse = db.users.insert_one(user)
            return Response(response = json.dumps({"message": "Thank you for your registration. Your email will be notified once the product is fully launched.", "id": f"{dbResponse.inserted_id}"}), status = 200, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"message": str(e)}), mimetype="application/json", status=500)
    if request.method == 'GET':
            try:
                response = make_response(
                jsonify(
                {"message": "Video fetched successfully"}),200,
                )
                return response
    
            except Exception as e: 
                return jsonify({"error":str(e)})

@api.route('/signup', methods=['POST', 'GET'])
def signup():
    try:
        if request.method == 'POST':
            is_user_exist = db.users.find_one({'email' : request.json['email']})
            hash_password = bcrypt.hashpw(request.json['password'].encode('utf-8'), bcrypt.gensalt())
            data = {
                'email': request.json["email"], 
                'password': hash_password,
                'firstName': request.json["firstName"],
                'lastName': request.json["lastName"],}
            if is_user_exist is None:
                dbResponse = db.users.insert_one(data)
                response = make_response(
                        jsonify(
                            {"message": "User created successfully"}
                        ),
                        200,
                    )
                response.headers["Content-Type"] = "application/json"
                return response
            return make_response(
                jsonify(
                    {"message": "User already exist"}
                ),
                200,
            )
        
            
    except Exception as e: 
        return jsonify({"error":str(e)})

@api.route('/signin', methods=['POST','GET'])
def signin():
    try:
        if request.method == 'POST':
            is_user_exist = db.users.find_one({'email' : request.form['email']})
            if is_user_exist is not None:
                if bcrypt.checkpw(request.form['password'].encode('utf-8'), is_user_exist['password']):
                    response = make_response(
                        jsonify(
                            {"message": "User logged in successfully", "email": request.form['email']}
                        ),
                        200,
                    )
                    response.headers["Content-Type"] = "application/json"
                    return response
                return make_response(
                    jsonify(
                        {"message": "Invalid password or email"}
                    ),
                    200,
                )
            return make_response(
                jsonify(
                    {"message": "User does not exist"}
                ),
                200,
            )
        return make_response( 
            jsonify(
                {"message": "Please provide email and password"}
            ),
            200,
        )

    except Exception as e: 
        return jsonify({"error":str(e)})

@api.route('/signout')
def signout():
    try:
        if request.method == 'GET':
            response = make_response(
                jsonify(
                    {"message": "User logged out successfully"}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    
    except Exception as e: 
        return jsonify({"error":str(e)})

@api.route('/upload', methods=['POST'])
def upload_video():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        email = request.form['email']
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        else:
            file.filename = email.split('@')[0] + ' - Bicara.AI - ' + str(datetime.now()) + '.mp4'
            file.filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            analysis = vidProcess.videoProcess(file.filename,email)
            db.results.insert_one(analysis)
            msg = Message('Hello', sender = 'noreply@demo.com', recipients = [email])
            msg.body = "Terima kasih sudah menggunakan Bicara.AI. Video anda telah selesai dianalisis. Silahkan cek hasilnya di Bicara.AI."
            mail.send(msg)
            # add notification email after 
            flash('Video successfully uploaded and displayed below')
            return make_response(
                jsonify(
                    {"message": "Video successfully uploaded and displayed below"}
                ),
                200,
            )

@api.route('/user/<email>', methods=['GET'])
def get_user_by_email(email):
    try:
        if request.method == 'GET':
            
            user = db.users.find_one({'email': email})
            user['_id'] = str(user['_id'])
            user.pop('password', None)
            response = make_response(
            jsonify(user,
                    {"message": "Result fetched successfully"}
                ),
            200,
        )
        response.headers["Content-Type"] = "application/json"
        return user
    except Exception as e:
        return jsonify({"error":str(e)})

@api.route('/upload/display/<filename>')
def display_video(filename):
    #print('display_video filename: ' + filename)
    return redirect(url_for('static', filename='results/' + filename), code=301)
    
@api.route('/upload/process/<filename>')
def process_video(filename):
    #print('display_video filename: ' + filename)
    return redirect(url_for('static', filename='results/' + filename), code=301)

@api.route('/result/<email>', methods=['GET'])
def get_result_by_email(email):
    try:
        if request.method == 'GET':
            
            result = db.results.find({'email': email})
            result = list(result)
            for x in result:
                x['_id'] = str(x['_id'])
            current_app.logger.info(result)
            print(result)
            response = make_response(
                jsonify(
                    {"message": "Result fetched successfully", "result": result}
                ),  200, 
            )
            response.headers["Content-Type"] = "application/json"
            return response 
    except Exception as e:
        return jsonify({"error":str(e)})   


@api.route('/details/<_id>', methods=['GET'])
def get_result_by_id(_id):
    try:
        result = db.results.find_one({'_id': ObjectId(_id)})
        result['_id'] = str(result['_id'])
        response = make_response(
            jsonify(result,
                    {"message": "Result fetched successfully"}
                ),
            200,
        )
        response.headers["Content-Type"] = "application/json"
        return result
    except Exception as e:
        return jsonify({"error":str(e)}) 
        
@api.route('/user', methods=['GET'])
def get_user():
    try:
        if request.method == 'GET':
            user = db.users.find()
            user = list(user)
            for x in user:
                x['_id'] = str(x['_id'])
                x.pop('password', None)
            response = make_response(
                jsonify(
                    {"message": "Result fetched successfully", "user": user}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    except Exception as e:
        return jsonify({"error":str(e)})

@api.route('/sendotp', methods=['POST'])
def send_otp():
    try:
        if request.method == 'POST':
            email = request.json['email']
            otp = random.randint(100000, 999999)
            msg = Message('OTP Registration for Bicara.AI', sender = 'noreply@demo.com', recipients = [email])
            msg.body = "Your OTP is " + str(otp)
            mail.send(msg)
            response = make_response(
                jsonify(
                    {"message": "OTP sent successfully", "otp": str(otp)}
                ),
                200,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    except Exception as e:
        return jsonify({"error":str(e)})
app.register_blueprint(api)