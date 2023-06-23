from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app import bcrypt, schema
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
from flask_app.models import message_model
tables = 'users'

class Users:

    # DB = schema
    # tables = 'users'

    def __init__(self, data) -> None:
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.sent_msgs = []
        self.received_msgs = []

    @classmethod
    def get_all(cls):
        query = f'SELECT * FROM {tables};'
        results = connectToMySQL(schema).query_db(query)
        users = []
        if results:
            for user in results:
                users.append( cls(user) )
        return users
    
    @classmethod
    def get_one(cls, id):
        query = f'SELECT * FROM {tables} WHERE id = %(id)s;'
        data = {'id': id}
        results = connectToMySQL(schema).query_db(query, data)
        if len(results)< 1:
            return False
        return cls(results[0])
    
    @staticmethod
    def save_user(form):
        query = f'''INSERT INTO {tables} (first_name, last_name, email, password) 
                VALUES (  %(first_name)s, %(last_name)s, %(email)s, %(password)s  );'''
        
        pw_hash = bcrypt.generate_password_hash(form['password']).decode('utf-8')
        data = {
            'first_name' : form['first_name'],
            'last_name' : form['last_name'],
            'email' : form['email'],
            'password' : pw_hash
        }

        return connectToMySQL(schema).query_db(query, data)
    
    @staticmethod
    def update(form):
        query = f'''UPDATE {tables} 
                SET first_name = %(first_name), last_name = %(last_name)s, email = %(email)s, password = %(password)s
                WHERE id = %(id)s;'''
        
        pw_hash = bcrypt.generate_password_hash(form['password']).decode('utf-8')
        data = {
            'first_name' : form['first_name'],
            'last_name' : form['last_name'],
            'email' : form['email'],
            'password' : pw_hash
        }
        return connectToMySQL(schema).query_db(query, data)
    
    @staticmethod
    def delete(id):
        query = f'DELETE FROM {tables} WHERE id = %(id)s;'
        data = {'id' : id}
        return connectToMySQL(schema).query_db(query, data)

    @staticmethod
    def validate_email( email ):
        is_valid = True
        if not EMAIL_REGEX.match(email['email']):
            is_valid = False
        return is_valid

    @classmethod
    def password_check(cls, data):
        user = cls.get_one_email(data)
        # check if user password matches
        if bcrypt.check_password_hash(user.password, data['password']):
            return True
        return False

    # query via email
    @classmethod
    def get_one_email(cls, data):
        query = f'SELECT * FROM {tables} WHERE email = %(email)s;'
        results = connectToMySQL(schema).query_db(query, data)
        # if no match, result len is < 1, return false
        if len(results)< 1:
            return False
        # else we return the cls(returned user info)
        return cls(results[0])

    @classmethod
    def login_check(cls, data):
        is_valid = True
        if not cls.validate_email(data):
            # incorrect email format
            flash('Invalid email address! Check your spelling', 'login')
            is_valid = False
        elif not cls.get_one_email(data):
            # email not in database
            flash('Invalid email/password combination!', 'login')
            is_valid = False
        elif not cls.password_check(data):
            # invalid password
            flash('Invalid email/password combination!', 'login')
            is_valid = False
        return is_valid

    @classmethod
    def registration_check(cls, data):
        is_valid = True
        if len(data['first_name']) < 2:
            flash('First name must be at least 2 character long', 'registration')
            is_valid = False
        if any(char.isdigit() for char in data['first_name']):
            flash('First name cannot contain numbers', 'registration')
            is_valid = False
        if len(data['last_name']) < 2:
            flash('Last name must be at least 2 character long', 'registration')
            is_valid = False
        if any(char.isdigit() for char in data['last_name']):
            flash('Last name cannot contain numbers', 'registration')
            is_valid = False
        if not cls.validate_email(data):
            flash('Invalid email address!', 'registration')
            is_valid = False
        if cls.get_one_email(data):
            flash('Email is already registered', 'registration')
            is_valid = False
        if len(data['password']) < 8:
            flash('Password must be between 8 and 20 characters long', 'registration')
            is_valid = False
        if len(data['password']) > 20:
            flash('Password must be between 8 and 20 characters long', 'registration')
            is_valid = False
        # password check to have 1 number and One uppercase letter
        upper = False
        digit = False
        for i in data['password']:
            if i.isupper():
                upper = True
            elif i.isdigit():
                digit = True
        if not upper:
            flash('Password should include one upper-case letter', 'registration')
            is_valid = False
        if not digit:
            flash('Password should include one number', 'registration')
            is_valid = False
        if data['password'] != data['confirm_password']:
            flash('Password does not match', 'registration')
            is_valid = False
        return is_valid

    
    @classmethod
    def user_received_msgs(cls,id):
        query = f'''
                SELECT * FROM users
                LEFT JOIN messages ON receiver_id = users.id
                LEFT JOIN users AS sender ON sender_id = sender.id
                WHERE users.id = %(id)s;
                '''
        data = {'id': id}
        results = connectToMySQL(schema).query_db(query, data)
        if len(results) < 1:
            return False
        user = cls(results[0])
        for row in results:
            msg_data = {
                'id' : row['messages.id'],
                'message' : row['message'],
                'created_at' : row['messages.created_at'],
                'updated_at' : row['messages.updated_at'],
                'sender_id' : row['sender_id'],
                'receiver_id' : row['receiver_id']
            }
            msg = message_model.Messages(msg_data)
            sender_data = {
                'id' : row['sender.id'],
                'first_name' : row['sender.first_name'],
                'last_name' : row['sender.last_name'],
                'email' : row['sender.email'],
                'password' : row['sender.password'],
                'created_at' : row['sender.created_at'],
                'updated_at' : row['sender.updated_at']
            }
            msg.sender.update(sender_data)
            user.received_msgs.append(msg)
        return user

    @classmethod
    def user_sent_msgs(cls, id):
        query = f'''
                SELECT * FROM users
                left join messages on sender_id = users.id
                left join users as receiver on receiver_id = receiver.id
                where users.id = 1;'''
        data = {'id': id}
        results = connectToMySQL(schema).query_db(query, data)
        if len(results) < 1:
            return False
        user = cls(results[0])
        for row in results:
            msg_data = {
                'id' : row['messages.id'],
                'message' : row['message'],
                'created_at' : row['messages.created_at'],
                'updated_at' : row['messages.updated_at'],
                'sender_id' : row['sender_id'],
                'receiver_id' : row['receiver_id']
            }
            msg = message_model.Messages(msg_data)
            receiver_data = {
                'id' : row['receiver.id'],
                'first_name' : row['receiver.first_name'],
                'last_name' : row['receiver.last_name'],
                'email' : row['receiver.email'],
                'password' : row['receiver.password'],
                'created_at' : row['receiver.created_at'],
                'updated_at' : row['receiver.updated_at']
            }
            msg.receiver.update(receiver_data)
            user.received_msgs.append(msg)
        return user
    
    @classmethod
    def get_other_users(cls,id):
        query = f'SELECT * FROM users WHERE users.id != %(id)s ORDER BY first_name ASC;'
        data = {'id': id}
        results = connectToMySQL(schema).query_db(query, data)
        if len(results) < 1:
            return False
        all_users = []
        for row in results:
            all_users.append(cls(row))
        return all_users