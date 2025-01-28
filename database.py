from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
import sys
import logging
import traceback
from dotenv import load_dotenv
from datetime import datetime
import uuid

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('database.log', mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Cargar variables de entorno
load_dotenv()

class DatabaseConnectionError(Exception):
    """Excepción personalizada para errores de conexión a base de datos"""
    pass

class Database:
    _instance = None
    _db_connection = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Database, cls).__new__(cls)
            try:
                cls._instance._connect()
            except Exception as e:
                logging.error(f"Error crítico al conectar a la base de datos: {e}")
                logging.error(traceback.format_exc())
                raise DatabaseConnectionError(f"No se pudo establecer conexión: {e}")
        return cls._instance
    
    def _connect(self):
        try:
            # Obtener URI de MongoDB desde variables de entorno
            mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
            db_name = os.getenv('MONGO_DB', 'dounel_createur')
            
            logging.info(f"Intentando conectar a MongoDB: {mongo_uri}")
            
            # Configurar cliente de MongoDB con timeout
            self.client = MongoClient(
                mongo_uri, 
                serverSelectionTimeoutMS=10000,  # 10 segundos de timeout
                connectTimeoutMS=10000,          # 10 segundos para establecer conexión
                socketTimeoutMS=10000            # 10 segundos de timeout de socket
            )
            
            # Probar la conexión
            self.client.admin.command('ismaster')
            
            # Seleccionar base de datos
            self.db = self.client[db_name]
            
            # Verificar si la base de datos existe o crear colecciones
            self._inicializar_colecciones()
            
            # Guardar referencia de conexión
            Database._db_connection = self.db
            
            logging.info(f"Conexión a MongoDB establecida. Base de datos: {db_name}")
        
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logging.error(f"Error de conexión a MongoDB: {e}")
            logging.error(f"Detalles de la URI: {mongo_uri}")
            logging.error(f"Nombre de base de datos: {db_name}")
            logging.error(traceback.format_exc())
            raise DatabaseConnectionError(f"No se pudo conectar a MongoDB: {e}")
        
        except Exception as e:
            logging.error(f"Error inesperado al conectar a MongoDB: {e}")
            logging.error(traceback.format_exc())
            raise DatabaseConnectionError(f"Error crítico de conexión: {e}")
    
    def _inicializar_colecciones(self):
        """Crear colecciones iniciales si no existen"""
        try:
            # Lista de colecciones a crear
            colecciones = ['contactos', 'cursos', 'usuarios']
            
            for coleccion in colecciones:
                # Crear la colección si no existe
                if coleccion not in self.db.list_collection_names():
                    self.db.create_collection(coleccion)
                    logging.info(f"Colección '{coleccion}' creada.")
            
            # Insertar datos iniciales de cursos si la colección está vacía
            cursos_collection = self.db['cursos']
            if cursos_collection.count_documents({}) == 0:
                cursos_iniciales = [
                    {
                        "id": "web",
                        "titulo": "Desarrollo Web Full Stack",
                        "descripcion": "Aprende desarrollo web desde cero",
                        "precio": 200.00,
                        "duracion": "3 meses",
                        "nivel": "Principiante"
                    },
                    {
                        "id": "marketing",
                        "titulo": "Marketing Digital",
                        "descripcion": "Estrategias de marketing online",
                        "precio": 180.00,
                        "duracion": "2 meses",
                        "nivel": "Intermedio"
                    }
                ]
                cursos_collection.insert_many(cursos_iniciales)
                logging.info("Datos iniciales de cursos insertados.")
        
        except Exception as e:
            logging.error(f"Error inicializando colecciones: {e}")
            logging.error(traceback.format_exc())
            raise
    
    @classmethod
    def get_connection(cls):
        """Obtener la conexión de base de datos de manera segura"""
        if not cls._db_connection:
            raise DatabaseConnectionError("No hay conexión a la base de datos")
        return cls._db_connection

    def get_collection(self, collection_name):
        """Obtener una colección específica"""
        return self.db[collection_name]

    def insert_document(self, collection_name, document):
        """Insertar un documento en una colección"""
        collection = self.get_collection(collection_name)
        return collection.insert_one(document)

    def find_documents(self, collection_name, query=None):
        """Buscar documentos en una colección"""
        collection = self.get_collection(collection_name)
        return list(collection.find(query or {}))

    def update_document(self, collection_name, query, update):
        """Actualizar documentos en una colección"""
        collection = self.get_collection(collection_name)
        return collection.update_many(query, {"$set": update})

    def delete_document(self, collection_name, query):
        """Eliminar documentos de una colección"""
        collection = self.get_collection(collection_name)
        return collection.delete_many(query)

    def guardar_mensaje_contacto(self, nombre, email, telefono, mensaje):
        try:
            # Validar campos
            if not all([nombre, email, telefono, mensaje]):
                raise ValueError("Todos los campos son obligatorios")
            
            contactos = self.db['contactos']
            mensaje_data = {
                "id": str(uuid.uuid4()),
                "nombre": nombre,
                "email": email,
                "telefono": telefono,
                "mensaje": mensaje,
                "timestamp": datetime.utcnow(),
                "estado": "pendiente",
                "leido": False
            }
            resultado = contactos.insert_one(mensaje_data)
            logging.info(f"Mensaje de contacto guardado. ID: {resultado.inserted_id}")
            return resultado
        
        except ValueError as ve:
            logging.error(f"Error de validación: {ve}")
            raise
        except Exception as e:
            logging.error(f"Error guardando mensaje de contacto: {e}")
            logging.error(traceback.format_exc())
            raise DatabaseConnectionError(f"Error al guardar mensaje: {e}")

    def obtener_mensajes_contacto(self, limite=50):
        """Obtener los últimos mensajes de contacto"""
        try:
            contactos = self.db['contactos']
            return list(contactos.find().sort('timestamp', -1).limit(limite))
        
        except Exception as e:
            logging.error(f"Error obteniendo mensajes de contacto: {e}")
            logging.error(traceback.format_exc())
            raise

    def marcar_mensaje_contacto(self, mensaje_id, estado):
        """Marcar un mensaje de contacto"""
        try:
            contactos = self.db['contactos']
            return contactos.update_one(
                {"id": mensaje_id},
                {"$set": {"estado": estado, "leido": True}}
            )
        
        except Exception as e:
            logging.error(f"Error marcando mensaje de contacto: {e}")
            logging.error(traceback.format_exc())
            raise

def init_database():
    try:
        # Inicializar base de datos
        db = Database()
        logging.info("Base de datos inicializada correctamente")
        return db
    
    except DatabaseConnectionError as e:
        logging.error(f"Error de conexión a base de datos: {e}")
        return None
    except Exception as e:
        logging.error(f"Error inesperado inicializando base de datos: {e}")
        logging.error(traceback.format_exc())
        return None

# Diagnóstico de conexión
if __name__ == "__main__":
    try:
        print("Iniciando diagnóstico de conexión a MongoDB...")
        
        # Verificar variables de entorno
        mongo_uri = os.getenv('MONGO_URI')
        mongo_db = os.getenv('MONGO_DB')
        
        print(f"URI de MongoDB: {mongo_uri}")
        print(f"Base de datos: {mongo_db}")
        
        # Intentar conectar
        db = init_database()
        
        if db:
            # Probar operaciones básicas
            print("\nProbando operaciones básicas...")
            
            # Guardar mensaje de prueba
            resultado = db.guardar_mensaje_contacto(
                'Prueba', 
                'prueba@ejemplo.com', 
                '1234567890', 
                'Mensaje de diagnóstico'
            )
            
            print(f"Mensaje de prueba guardado. ID: {resultado.inserted_id}")
        else:
            print("No se pudo establecer conexión a la base de datos.")
    
    except Exception as e:
        print(f"Error en diagnóstico: {e}")
        print(traceback.format_exc())
