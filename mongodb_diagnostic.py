import os
import sys
import traceback
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Cargar variables de entorno
load_dotenv()

def diagnosticar_mongodb():
    try:
        # Obtener URI de MongoDB desde variables de entorno
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        db_name = os.getenv('MONGO_DB', 'dounel_createur')
        
        print(f"🔍 Diagnóstico de conexión a MongoDB")
        print(f"URI: {mongo_uri}")
        print(f"Base de datos: {db_name}")
        
        # Intentar conectar
        try:
            client = MongoClient(
                mongo_uri, 
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            
            # Probar la conexión
            client.admin.command('ismaster')
            
            # Seleccionar base de datos
            db = client[db_name]
            
            # Crear colección de prueba
            coleccion_prueba = db['prueba_conexion']
            resultado = coleccion_prueba.insert_one({"mensaje": "Prueba de conexión"})
            
            print(f"✅ Conexión exitosa")
            print(f"📝 Documento de prueba insertado. ID: {resultado.inserted_id}")
            
            # Eliminar colección de prueba
            coleccion_prueba.drop()
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ Error de conexión: {e}")
            print("Posibles causas:")
            print("1. MongoDB no está iniciado")
            print("2. URI de conexión incorrecta")
            print("3. Problemas de red o firewall")
            return False
        
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            print(traceback.format_exc())
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    diagnosticar_mongodb()
