from flask import Flask,current_app, Response, request, make_response, jsonify,session, render_template,flash,redirect,url_for
import pymongo
import json
from bson.objectid import ObjectId
from flask_session import Session
from flask_mail import Mail, Message
import urllib.request
import bcrypt
from flask_cors import CORS
from werkzeug.utils import secure_filename
from collections import Counter
import vidProcess
import os


app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
RESULT_FOLDER = 'static/results/'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
CORS(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'boftkingdom@gmail.com'
app.config['MAIL_PASSWORD'] = 'gyoalqqzzpntdoed'
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
mail = Mail(app)
Session(app)

try:
    mongo = pymongo.MongoClient(
        host="mongodb://localhost:27017",
        serverSelectionTimeoutMS = 3000
    )
    db = mongo.bicara_ai
    mongo.server_info()
except:
    print("ERROR - Cannot connect to database")



@app.route('/', methods=['POST', 'GET'])
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
            return Response(json.dumps({"message": "Sorry, your email can't be registered"}), mimetype="application/json", status=500)
    if request.method == 'GET':
            try:
                videos = db.videos.find_one({'link': 'https://www.youtube.com/watch?v=7lCDEYXw3mM'}) #link video hanya contoh karena belum ada link video di database
                response = make_response(
                jsonify(
                {"message": "Video fetched successfully"}),200,
                )
                return response
       
            except Exception as e: 
                return jsonify({"error":str(e)})

@app.route('/signup', methods=['POST', 'GET'])
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
                session['email'] = request.json['email']
                return response
            return make_response(
                jsonify(
                    {"message": "User already exist"}
                ),
                200,
            )
        
            
    except Exception as e: 
        return jsonify({"error":str(e)})

@app.route('/signin', methods=['POST','GET'])
def signin():
    try:
        if 'email' in session:
            return jsonify({"message":"User already logged in"})
        if request.method == 'POST':
            is_user_exist = db.users.find_one({'email' : request.form['email']})
            if is_user_exist is not None:
                if bcrypt.checkpw(request.form['password'].encode('utf-8'), is_user_exist['password']):
                    session["email"] = request.form.get("email")
                    response = make_response(
                        jsonify(
                            {"message": "User logged in successfully"}
                        ),
                        200,
                    )
                    response.headers["Content-Type"] = "application/json"
                    return render_template('dashboard.html')
                return make_response(
                    jsonify(
                        {"message": "Invalid password"}
                    ),
                    200,
                )
            return make_response(
                jsonify(
                    {"message": "User does not exist"}
                ),
                200,
            )
        if request.method == 'GET':
            return render_template('signin.html')
    except Exception as e: 
        return jsonify({"error":str(e)})

@app.route('/signout')
def signout():
    try:
        if 'email' in session:
            session.pop('email', None)
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

@app.route('/upload', methods=['POST'])
def upload_video():
    if request.method == 'POST':
        current_app.logger.debug(request)
        current_app.logger.debug(request.form)
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        else:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            vidProcess.videoProcess(filename)
            #print('upload_video filename: ' + filename)
            flash('Video successfully uploaded and displayed below')
            return make_response(
                jsonify(
                    {"message": "Video successfully uploaded and displayed below"}
                ),
                200,
            )
    

@app.route('/upload/display/<filename>')
def display_video(filename):
	#print('display_video filename: ' + filename)
	return redirect(url_for('static', filename='results/' + filename), code=301)
	
@app.route('/upload/process/<filename>')
def process_video(filename):
	#print('display_video filename: ' + filename)
	return redirect(url_for('static', filename='results/' + filename), code=301)

@app.route('/result/<email>', methods=['GET'])
def get_result(email):
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
    
        
        

if __name__ == '__main__':
    app.run(debug=True)
