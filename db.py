from datetime import datetime

from bson import ObjectId
from pymongo import MongoClient, DESCENDING
from werkzeug.security import generate_password_hash

from user import User


client = MongoClient("mongodb+srv://middleadmin:teamorgullo@cluster0.hs1ao.mongodb.net/middleDB?retryWrites=true&w=majority")

db = client.test

middle_DB = client.get_database("middleDB")
coleccion_usuarios = middle_DB.get_collection("usuarios")
coleccion_canales = middle_DB.get_collection("canales")
coleccion_mensajes = middle_DB.get_collection("mensajes")

""" coleccion_test = middle_DB.get_collection("test")

def save_test(username):
    coleccion_test.insert_one({'_id': username, 'password': 'asd', 'channels': []})


def append_test(username):
    coleccion_test.update_one({'_id': username}, {"$push": {'channels': username}}) """


def save_user(username, password):
    password_hash = generate_password_hash(password)
    coleccion_usuarios.insert_one(  {'_id': username, 'password': password_hash, 'rooms': []}  )


def get_user(username):
    user_data = coleccion_usuarios.find_one(  {'_id': username}  )
    return User(user_data['_id'], user_data['password']) if user_data else None


def save_room(room_name, category, created_by):
    coleccion_canales.insert_one(  { '_id': room_name, 'category': category, 'created_by': created_by, 'members': [], 'created_at': datetime.now() }  )
    add_room_member(room_name, created_by)
    return room_name


def get_room(room_name):
    return coleccion_canales.find_one({'_id': room_name})


def get_rooms_for_user(username):
    return list(coleccion_usuarios.find(  {'_id.username': username}, {'rooms': 1}  ))


def get_available_rooms(username):
    return list(coleccion_canales.find(  {'members': { "$nin": [username] }}  ))

# No es necesario
def update_room(room_id, room_name):
    coleccion_canales.update_one({'_id': ObjectId(room_id)}, {'$set': {'name': room_name}})
    coleccion_miembros.update_many({'_id.room_id': ObjectId(room_id)}, {'$set': {'room_name': room_name}})


def add_room_member(room_name, username):
    coleccion_canales.update_one(  {'_id': room_name}, {"$push": {'members': username}}  )
    coleccion_usuarios.update_one(  {'_id': username}, {"$push": {'rooms': room_name}}  )


def remove_room_members(room_id, usernames):
    coleccion_miembros.delete_many(
        {'_id': {'$in': [{'room_id': ObjectId(room_id), 'username': username} for username in usernames]}})


def get_room_members(room_name):
    query = coleccion_canales.find_one(  {'_id': room_name}, {'_id': 0, 'members': 1}  )
    members = query['members']
    return members


def is_room_member(room_name, username):
    query = coleccion_usuarios.find_one(  {'_id': username}, {'_id': 0, 'rooms': 1} )
    rooms = query['rooms']
    return True if room_name in rooms else False


def is_room_admin(room_id, username):
    return coleccion_miembros.count_documents(
        {'_id': {'room_id': ObjectId(room_id), 'username': username}, 'is_room_admin': True})


def save_message(room_id, text, sender):
    coleccion_mensajes.insert_one({'room_id': room_id, 'text': text, 'sender': sender, 'created_at': datetime.now()})


MESSAGE_FETCH_LIMIT = 3


def get_messages(room_id, page=0):
    offset = page * MESSAGE_FETCH_LIMIT
    messages = list(
        coleccion_mensajes.find({'room_id': room_id}).sort('_id', DESCENDING).limit(MESSAGE_FETCH_LIMIT).skip(offset))
    for message in messages:
        message['created_at'] = message['created_at'].strftime("%d %b, %H:%M")
    return messages[::-1]
