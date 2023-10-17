"""
Class to interact with MongoDB Atlas
"""
from pymongo import MongoClient
from bson import ObjectId


class MongoDBHandler:
    def __init__(self, db_name, collection_name, connection_string):
        """
        Initialize MongoDB connection parameters.
        Parameters
        - db_name (str): Name of the database.
        - collection_name (str): Name of the collection within the database.
        - connection_string (str): MongoDB connection string
        """
        self.connection_string = connection_string
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):
        """
        Establish MongoDB Connection.
        """
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
        except Exception as e:
            print(f"Exception in connecting to MongoDB: {str(e)}")

    def insert_record(self, record):
        """
        Inserts a record into collection.
        Parameters:
        - record (dict): Data in dictionary format
        Returns:
        - str: Identifier of the inserted record
        """
        try:
            inserted_id = self.collection.insert_one(record).inserted_id
            print(f"Record inserted to MongoDB, Id:{inserted_id}")
            return inserted_id
        except Exception as e:
            print(f"Exception in inserting record to MongoDB: {str(e)}")

    def get_record(self, record_id):
        """
        Retrieves a specific record with the given identifier.
        Parameters:
        - record_id (str): Identifier of the record to be retrieved
        Returns:
        - dict: Dictionary with the results from collection
        """
        try:
            result = self.collection.find_one({'_id': ObjectId(record_id)})
            return result
        except Exception as e:
            print(f"Exception in reading record from MongoDB: {str(e)}")

    def close_connection(self):
        """
        Closes existing MongoDB connection.
        """
        try:
            if self.client:
                self.client.close()
        except Exception as e:
            print(f"Exception in closing MongoDB connection: {str(e)}")
