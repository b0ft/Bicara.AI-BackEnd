from flask import Flask, Response, request, make_response, jsonify,session
import pymongo
import json
from bson.objectid import ObjectId
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
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

@app.route('/', methods=['POST'])
def notify_user():
    try:
        user = {"email": request.form["email"]}
        findEmail = db.users.find_one(user)
        if findEmail:
            return Response(json.dumps({"message": "Email already exists"}), mimetype="application/json", status=500)
        dbResponse = db.users.insert_one(user)
        return Response(response = json.dumps({"message": "Thank you for your registration. Your email will be notified once the product is fully launched.", "id": f"{dbResponse.inserted_id}"}), status = 200, mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"message": "Sorry, your email can't be registered"}), mimetype="application/json", status=500)
    
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    try:
        if request.method == 'POST':
            is_user_exist = db.users.find_one({'email' : request.form['email']})
            hash_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            data = {
                'email': request.form["email"], 
                'password': hash_password,
                'firstName': request.form["firstName"],
                'lastName': request.form["lastName"],}
            if is_user_exist is None:
                dbResponse = db.users.insert_one(data)
                response = make_response(
                        jsonify(
                            {"message": "User created successfully"}
                        ),
                        200,
                    )
                response.headers["Content-Type"] = "application/json"
                session['email'] = request.form['email']
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
                    return response
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

@app.route('/', methods=['GET'])
def getvideo():
    try:
        videos = db.videos.find_one({'link': 'https://www.youtube.com/watch?v=7lCDEYXw3mM'}) #link video hanya contoh karena belum ada link video di database
        response = make_response(
            jsonify(
                {"message": "Video fetched successfully"}
            ),
            200,
        )
        
        return response
       
    except Exception as e: 
        return jsonify({"error":str(e)})

if __name__ == '__main__':
    app.run(debug=True)
