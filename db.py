from datetime import datetime

from bson import ObjectId
from pymongo import MongoClient, DESCENDING
from werkzeug.security import generate_password_hash

from user import User


client = MongoClient("mongodb+srv://middleadmin:teamorgullo@cluster0.hs1ao.mongodb.net/middleDB?retryWrites=true&w=majority")

db = client.test

middle_DB = client.get_database("middleDB")
coleccion_usuarios = middle_DB.get_collection("usuarios")
coleccion_miembros = middle_DB.get_collection("miembros")


def save_user(username, password):
    password_hash = generate_password_hash(password)
    coleccion_usuarios.insert_one({'_id': username, 'password': password_hash})


def get_user(username):
    user_data = coleccion_usuarios.find_one({'_id': username})
    return User(user_data['_id'], user_data['password']) if user_data else None


def get_rooms_for_user(username):
    return list(coleccion_miembros.find({'_id.username': username}))
