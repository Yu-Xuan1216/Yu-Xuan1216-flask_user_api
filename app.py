from flask import Flask, request, jsonify, redirect, url_for
import pandas as pd
from flasgger import Swagger

app = Flask(__name__)
Swagger(app)

# Store users in memory or database
users = []

def user_exists(name):
    """
    Check if a user with the given name already exists.
    Returns: bool
    """
    return any(user['Name'] == name for user in users)

def validate_user_data(name, age):
    """
    Validate user name and age.
    Returns: (is_valid: bool, error_message: str)
    """
    print("name:", name, "age:", age)
    # Name validation
    if not isinstance(name, str) or pd.isna(name) or name.strip() == '':
        return False, 'Name cannot be empty'

    # Age validation
    if pd.isna(age):
        return False, 'Age cannot be empty'
    
    try:
        age_float = float(age)
    except (ValueError, TypeError):
        return False, 'Age must be a number'

    if not age_float.is_integer():
        return False, 'Age must be an integer'

    age = int(age_float)
    if age <= 0 or age > 120:
        return False, 'Age must be between 1 and 120'

    return True, ''

@app.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user
    ---
    tags:
      - Users
    consumes:
      - application/json
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            Name:
              type: string
              description: The user's name
            Age:
              type: integer
              description: The user's age
          required:
            - Name
            - Age
    responses:
      201:
        description: User added successfully
      400:
        description: Invalid input or user already exists
    """
    data = request.get_json()
  
    if not data:
        return jsonify({'error': 'Name and age are required'}), 400
    
    name = data.get('Name')
    age = data.get('Age')

    is_valid, error = validate_user_data(name, age)
    if not is_valid:
        return jsonify({'error': error}), 400
    
    name = str(name).strip()
    age = int(age)

    # Check if user already exists
    if user_exists(name):
        return jsonify({'error': 'User already exists'}), 400
    
    user = {'Name': name, 'Age': age}
    users.append(user)
    return jsonify(user), 201

@app.route('/users/<name>', methods=['DELETE'])
def delete_user(name):
    """
    Delete a user by name
    ---
    tags:
      - Users
    parameters:
      - name: name
        in: path
        type: string
        required: true
        description: Name of the user to delete
    responses:
      200:
        description: User deleted successfully
      404:
        description: User not found
    """
    for user in users:
        if user['Name'] == name:
            users.remove(user)
            return jsonify({'message': f'User {name} deleted successfully'}), 200
    return jsonify({'error': 'User not found'}), 404

@app.route('/users', methods=['GET'])
def get_users():
    """
    Get all users
    ---
    tags:
      - Users
    responses:
      200:
        description: List of users
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: array
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                      age:
                        type: integer
                count:
                  type: integer
    """
    return jsonify({'data': users, 'count': len(users)}), 200

@app.route('/users/upload', methods=['POST'])
def upload_users():
    """
    Create new users from CSV file
    ---
    tags:
      - Users
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        format: binary
        required: true
        description: CSV file with 'Name' and 'Age' columns
    responses:
      201:
        description: Users added successfully
      400:
        description: Invalid file or CSV format
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400
    
    try:
        df = pd.read_csv(file)
    except Exception as e:
        return jsonify({'error': f'Error processing CSV file: {str(e)}'}), 400
    
    # Validate required columns
    if not all(col in df.columns for col in ['Name', 'Age']):
        return jsonify({'error': 'CSV must contain "Name" and "Age" columns'}), 400
    
    # Convert DataFrame to list of dictionaries
    new_users = df.to_dict('records')
    
    # Add new users
    added_users = []
    invalid_users = []
    
    for idx, user in enumerate(new_users):
        # Validate data types and values
        name = user.get('Name')
        age = user.get('Age')

        is_valid, error = validate_user_data(name, age)
        if not is_valid:
            invalid_users.append({'row': idx + 2, 'error': error})
            continue
        
        name = str(name).strip()
        age = int(age)

        # Check if user already exists
        if user_exists(name):
            invalid_users.append({'row': idx + 2, 'error': f'User {name} already exists'})
            continue
        
        # Add valid user
        valid_user = {'Name': name, 'Age': age}
        users.append(valid_user)
        added_users.append(valid_user)
    
    response = {
        'message': f'Successfully added {len(added_users)} users',
        'added_users': added_users,
    }
    
    if invalid_users:
        response['invalid_users'] = invalid_users
        response['warning'] = f'{len(invalid_users)} rows skipped due to validation errors or duplicates'

    return jsonify(response), 201

@app.route('/users/average-age', methods=['GET'])
def get_average_age_by_group():
    """
    Get average age of users grouped by the first character of their names
    ---
    tags:
      - Users
    responses:
      200:
        description: Average age by group
        content:
          application/json:
            schema:
              type: object
              properties:
                average_age:
                  type: object
                  additionalProperties:
                    type: number
      404:
        description: No users found
    """
    if not users:
        return jsonify({'error': 'No users found'}), 404
    
    df = pd.DataFrame(users)
    
    # Add group column based on first character of usernames
    df['Group'] = df['Name'].str[0].str.upper()
    
    # Calculate average age for each group
    group_averages = df.groupby('Group')['Age'].mean().round(2).to_dict()
    
    return jsonify({
        'average_age': group_averages
    }), 200

# Redirect root to Swagger UI
@app.route("/")
def home():
    return redirect(url_for('flasgger.apidocs'))  # redirect to /apidocs/

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
