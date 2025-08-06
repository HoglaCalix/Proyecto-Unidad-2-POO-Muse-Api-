import os
import json
import logging
from pymongo import MongoClient
import requests 
from pymongo.server_api import ServerApi
import re
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
import base64
from fastapi import HTTPException
from dotenv import load_dotenv
from models.user import User
from models.loggin import Login
from utils.security import create_jwt_token
from utils.mongodb import get_collection


load_dotenv()
#
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
coll = get_collection("users")

def initialize_firebase():
    if firebase_admin._apps:
        return

    try:
        firebase_creds_base64 = os.getenv("FIREBASE_CREDENTIALS_BASE64")

        if firebase_creds_base64:
            firebase_creds_json = base64.b64decode(firebase_creds_base64).decode('utf-8')
            firebase_creds = json.loads(firebase_creds_json)
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized with environment variable credentials")
        else:
            # Fallback to local file (for local development)
            cred = credentials.Certificate("secrets/firebase.json")
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized with JSON file")

    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise HTTPException(status_code=500, detail=f"Firebase configuration error: {str(e)}")


initialize_firebase()
#Funcion para crear un usuario
async def create_user( user: User ) -> User:

    user_record ={}
    # Validar que el email no exista en Firebase. Se usa un try and catch en este codigo para manejar si hay un error en la conexion debido a que se
    # hace una conexion con servidores fuera de la red local.
    try:
        user_record = firebase_auth.create_user(
            email = user.email,
            password = user.password
        )

    except Exception as e:
        logger.warning(e)
        raise HTTPException(
            status_code= 400,
            detail = "Error al registrar en firebase"
        )
    
    # Validar que el email no exista en la base de datos
    #Este try en catch es para manejar algun problema de conexion a la base de datos
    try:
        coll = get_collection("users")
        new_user = User(
            name=user.name
            , lastname=user.lastname
            , email=user.email
            , password=user.password,
            admin=user.admin
        )
        #Crear el usuario en la base de datos excluyendo el id y la contraseña
        user_dict = new_user.model_dump(exclude={"id", "password"})
        inserted = coll.insert_one(user_dict)
        new_user.id = str(inserted.inserted_id)
        new_user.password = "*********"  # Mask the password in the response
        return new_user
        
    except Exception as e:
        # Si hay un error al insertar el usuario en la base de datos, eliminar el usuario de Firebase debido a 
        # inconsistencias en la base de datos
        firebase_auth.delete_user(user_record.uid)
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
#Funcion del login
async def login(user: Login):
    api_key = os.getenv("FIREBASE_API_KEY")
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": user.email
        , "password": user.password
        , "returnSecureToken": True
    }

    response = requests.post(url, json=payload)
    response_data = response.json()

    if "error" in response_data:
        raise HTTPException(
            status_code=400
            , detail="Error al autenticar usuario"
        )

    coll = get_collection("users")
    user_info = coll.find_one({ "email": user.email })

    if not user_info:
        raise HTTPException(
            status_code=404
            , detail="Usuario no encontrado en la base de datos"
        )

    return {
        "message": "Usuario Autenticado correctamente"
        , "idToken": create_jwt_token(
            user_info["name"]
            , user_info["lastname"]
            , user_info["email"]
            , user_info["active"]
            , user_info["admin"]
        )
    }
