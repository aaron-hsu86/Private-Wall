from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app import schema
from flask_app.models import user_model
tables = 'messages'

class Messages:

    # DB = schema
    # tables = 'messages'

    def __init__(self, data) -> None:
        self.id = data['id']
        self.message = data['message']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.sender_id = data['sender_id']
        self.receiver_id = data['receiver_id']
        self.sender = {}
        self.receiver = {}

    @classmethod
    def get_all_msgs(cls):
        query = f'''
                SELECT * FROM {tables}
                LEFT JOIN users AS sender ON sender.id = sender_id
                LEFT JOIN users AS receiver ON receiver.id = receiver_id;
                '''
        results = connectToMySQL(schema).query_db(query)
        if len(results) < 1:
            return False
        all_msgs = []
        for row in results:
            # create msg class
            msg = cls(row)
            # sort sender info to attach to msg.sender
            sender_data = {
                'id' : row['sender.id'],
                'first_name' : row['sender.first_name'],
                'last_name' : row['sender.last_name'],
                'email' : row['sender.email'],
                'password' : row['sender.password'],
                'created_at' : row['sender.created_at'],
                'updated_at' : row['sender.updated_at']
            }
            msg.sender.update(user_model.Users(sender_data))
            # sort receiver into to attach to msg.receiver
            receiver_data = {
                'id' : row['receiver.id'],
                'first_name' : row['receiver.first_name'],
                'last_name' : row['receiver.last_name'],
                'email' : row['receiver.email'],
                'password' : row['receiver.password'],
                'created_at' : row['receiver.created_at'],
                'updated_at' : row['receiver.updated_at']
            }
            msg.receiver.update(user_model.Users(receiver_data))
            # add msg with sender/receiver data into all_msgs
            all_msgs.append(msg)
        return all_msgs

    @classmethod
    def get_one_msgs(cls, id):
        query = f'''
                SELECT * FROM {tables}
                LEFT JOIN users AS sender ON sender.id = sender_id
                LEFT JOIN users AS receiver ON receiver.id = receiver_id
                WHERE messages.id = %(id)s;
                '''
        data = {'id': id}
        results = connectToMySQL(schema).query_db(query, data)
        if len(results) < 1:
            return False
        # create msg class
        one_msg = cls(results[0])
        # sort sender info to attach to one_msg.sender
        sender_data = {
            'id' : results[0]['sender.id'],
            'first_name' : results[0]['sender.first_name'],
            'last_name' : results[0]['sender.last_name'],
            'email' : results[0]['sender.email'],
            'password' : results[0]['sender.password'],
            'created_at' : results[0]['sender.created_at'],
            'updated_at' : results[0]['sender.updated_at']
        }
        one_msg.sender.update(user_model.Users(sender_data))
        # sort receiver into to attach to one_msg.receiver
        receiver_data = {
            'id' : results[0]['receiver.id'],
            'first_name' : results[0]['receiver.first_name'],
            'last_name' : results[0]['receiver.last_name'],
            'email' : results[0]['receiver.email'],
            'password' : results[0]['receiver.password'],
            'created_at' : results[0]['receiver.created_at'],
            'updated_at' : results[0]['receiver.updated_at']
        }
        one_msg.receiver.update(user_model.Users(receiver_data))
        return one_msg

    @staticmethod
    def save_message(data):
        query = '''INSERT INTO messages (message, sender_id, receiver_id)
                VALUES ( %(message)s, %(sender_id)s, %(receiver_id)s );'''
        return connectToMySQL(schema).query_db(query, data)
    
    @staticmethod
    def delete_message(id):
        query = 'DELETE FROM messages WHERE id = %(id)s;'
        data = {'id':id}
        return connectToMySQL(schema).query_db(query, data)