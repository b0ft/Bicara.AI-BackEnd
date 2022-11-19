from flask import Flask, Response, request, make_response, jsonify
import pymongo
import json
from bson.objectid import ObjectId

app = Flask(__name__)

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
        dbResponse = db.users.insert_one(user)
        print(dbResponse.inserted_id)
        return Response(response = json.dumps({"message": "Your email has been registered", "id": f"{dbResponse.inserted_id}"}), status = 200, mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"message": "Sorry, your email can't be registered"}), mimetype="application/json", status=500)
    
@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = {
            'email': request.form["email"], 
            'password': request.form["password"],
            'firstName': request.form["firstName"],
            'lastName': request.form["lastName"],}
        dbResponse = db.users.insert_one(data)
        response = make_response(
                jsonify(
                    {"message": "User created successfully"}
                ),
                200,
            )
        response.headers["Content-Type"] = "application/json"
        return response
    except Exception as e: 
        return jsonify({"error":str(e)})

if __name__ == '__main__':
    app.run(debug=True)
