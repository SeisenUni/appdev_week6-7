from flask import Flask, jsonify, request
from flask_basicauth import BasicAuth
from pymongo.mongo_client import MongoClient

app = Flask(__name__)
uri = "mongodb+srv://chayathon14639:GVlE571RSj3LCD1p@cluster0.76js1dj.mongodb.net/?retryWrites=true&w=majority"
app.config['BASIC_AUTH_USERNAME'] = 'username'
app.config['BASIC_AUTH_PASSWORD'] = 'password'
basic_auth = BasicAuth(app)
client = MongoClient(uri)

db = client["students"]
collection = db["std_info"]

@app.route("/")
def greet():
    return "<p>Welcome to Student Management System</p>"

@app.route("/students", methods=["GET"])
@basic_auth.required
def get_all_students():
    students = list(collection.find({}))
    student_list = []

    for student in students:
        student_data = {
            "id": str(student["_id"]),
            "Fullname": student.get("Full_name", ""),
            "Major": student.get("Department", ""),
            "GPA": student.get("Gpa", "")
        }
        student_list.append(student_data)

    return jsonify({"students": student_list})

@app.route("/students/<string:std_id>", methods=["GET"])
@basic_auth.required
def get_student_by_id(std_id):
    student = collection.find_one({"_id": std_id})

    if student:
        student_data = {
            "id": str(student["_id"]),
            "Fullname": student.get("Full_name", ""),
            "Major": student.get("Department", ""),
            "GPA": student.get("Gpa", "")
        }
        return jsonify({"student": student_data})
    else:
        return jsonify({"message": "Student not found"}), 404

@app.route("/students", methods=["POST"])
@basic_auth.required
def create_student():
    data = request.get_json()

    existing_student = collection.find_one({"_id": data.get("_id")})
    if existing_student:
        return jsonify({"error": "Cannot create new student"}), 500
    new_student = {
        "_id": data.get("_id"),
        "Full_name": data.get("Full_name"),
        "Department": data.get("Department"),
        "Gpa": data.get("Gpa")
    }
    result = collection.insert_one(new_student)
    return jsonify({"student": new_student}), 200

@app.route("/students/<string:std_id>", methods=["PUT"])
@basic_auth.required
def update_student(std_id):
    data = request.get_json()

    existing_student = collection.find_one({"_id": std_id})

    if existing_student:
        updated_student = {
            "$set": {
                "Full_name": data.get("Full_name", existing_student["Full_name"]),
                "Department": data.get("Department", existing_student["Department"]),
                "Gpa": data.get("Gpa", existing_student["Gpa"])
            }
        }

        result = collection.find_one_and_update({"_id": std_id}, updated_student, return_document=True)

        return jsonify({"student": result}), 200
    else:
        return jsonify({"error": "Student not found"}), 404

@app.route("/students/<string:std_id>", methods=["DELETE"])
@basic_auth.required
def delete_student(std_id):
    deleted_student = collection.find_one_and_delete({"_id": std_id})

    if deleted_student:
        deleted_student_data = {
            "id": str(deleted_student["_id"]),
            "Fullname": deleted_student.get("Full_name", ""),
            "Major": deleted_student.get("Department", ""),
            "GPA": deleted_student.get("Gpa", "")
        }
        return jsonify({"message": "Student deleted successfully", "deleted_student": deleted_student_data}), 200
    else:
        return jsonify({"error": "Student not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
