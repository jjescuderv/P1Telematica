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
coleccion_miembros = middle_DB.get_collection("miembros")
coleccion_mensajes = middle_DB.get_collection("mensajes")


def save_user(username, password):
    password_hash = generate_password_hash(password)
    coleccion_usuarios.insert_one({'_id': username, 'password': password_hash})


def get_user(username):
    user_data = coleccion_usuarios.find_one({'_id': username})
    return User(user_data['_id'], user_data['password']) if user_data else None


def save_room(room_name, created_by):
    room_id = coleccion_canales.insert_one(
        {'name': room_name, 'created_by': created_by, 'created_at': datetime.now()}).inserted_id
    add_room_member(room_id, room_name, created_by, created_by, is_room_admin=True)
    return room_id

def get_rooms_for_user(username):
    return list(coleccion_miembros.find({'_id.username': username}))

def update_room(room_id, room_name):
    coleccion_canales.update_one({'_id': ObjectId(room_id)}, {'$set': {'name': room_name}})
    coleccion_miembros.update_many({'_id.room_id': ObjectId(room_id)}, {'$set': {'room_name': room_name}})


def get_room(room_id):
    return coleccion_canales.find_one({'_id': ObjectId(room_id)})


def add_room_member(room_id, room_name, username, added_by, is_room_admin=False):
    coleccion_miembros.insert_one(
        {'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_name': room_name, 'added_by': added_by,
         'added_at': datetime.now(), 'is_room_admin': is_room_admin})

def add_room_members(room_id, room_name, usernames, added_by):
    coleccion_miembros.insert_many(
        [{'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_name': room_name, 'added_by': added_by,
          'added_at': datetime.now(), 'is_room_admin': False} for username in usernames])


def remove_room_members(room_id, usernames):
    coleccion_miembros.delete_many(
        {'_id': {'$in': [{'room_id': ObjectId(room_id), 'username': username} for username in usernames]}})


def get_room_members(room_id):
    return list(coleccion_miembros.find({'_id.room_id': ObjectId(room_id)}))




def is_room_member(room_id, username):
    return coleccion_miembros.count_documents({'_id': {'room_id': ObjectId(room_id), 'username': username}})


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
