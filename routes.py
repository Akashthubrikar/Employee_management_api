from flask import Flask, request, jsonify
from models import db, Employee
import requests
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)

@app.route('/employees_add', methods=['POST'])
def add_employee():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    position = data.get('position')
    salary = data.get('salary')

    new_employee = Employee(name=name, email=email, position=position, salary=salary)
    db.session.add(new_employee)
    db.session.commit()

    external_api_url = "https://reqres.in/api/users"
    payload = {
        "name": name,
        "job": position,
        "email": email,
        "age": data.get('age', 30),
        "address": data.get('address', {
            "street": "123 Main St",
            "city": "Anytown",
            "zip": "12345"
        }),
        "skills": data.get('skills', ["JavaScript", "React", "Node.js"])
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(external_api_url, json=payload, headers=headers)

    if response.status_code == 201:
        response_data = response.json()
        new_employee.api_id = response_data['id']
        new_employee.created_on = datetime.strptime(response_data['createdAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
        db.session.commit()

    return jsonify({"message": "Employee added successfully!"}), 201

@app.route('/employees_get', methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    result = []
    for employee in employees:
        emp_data = {
            'id': employee.id,
            'name': employee.name,
            'email': employee.email,
            'position': employee.position,
            'salary': employee.salary,
            'api_id': employee.api_id,
            'created_on': employee.created_on
        }
        result.append(emp_data)
    return jsonify(result), 200

@app.route('/employees_get_id/<int:id>', methods=['GET'])
def get_employee(id):
    employee = Employee.query.get(id)
    if not employee:
        return jsonify({"message": "Employee not found"}), 404

    emp_data = {
        'id': employee.id,
        'name': employee.name,
        'email': employee.email,
        'position': employee.position,
        'salary': employee.salary,
        'api_id': employee.api_id,
        'created_on': employee.created_on
    }
    return jsonify(emp_data), 200

@app.route('/employees_chng/<int:id>', methods=['PUT'])
def update_employee(id):
    employee = Employee.query.get(id)
    if not employee:
        return jsonify({"message": "Employee not found"}), 404

    data = request.get_json()
    employee.name = data.get('name', employee.name)
    employee.email = data.get('email', employee.email)
    employee.position = data.get('position', employee.position)
    employee.salary = data.get('salary', employee.salary)
    db.session.commit()
    return jsonify({"message": "Employee updated successfully"}), 200

@app.route('/employees_del/<int:id>', methods=['DELETE'])
def delete_employee(id):
    employee = Employee.query.get(id)
    if not employee:
        return jsonify({"message": "Employee not found"}), 404

    db.session.delete(employee)
    db.session.commit()
    return jsonify({"message": "Employee deleted successfully"}), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
