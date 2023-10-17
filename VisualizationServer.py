"""
Server to Visualize the data from MongoDB in the form of matplot
"""
from flask import Flask, request, Response, jsonify
import pandas as pd
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import configparser
from DatabaseHandler import MongoDBHandler


config = configparser.ConfigParser()
config.read('config.ini')

db_name = config['database']['DB_NAME']
collection_name = config['database']['COLLECTION_NAME']
connection_string = config['database']['CONNECTION_STRING']

app = Flask(__name__)
db_handler = MongoDBHandler(db_name=db_name, collection_name=collection_name,
                            connection_string=connection_string)


@app.get('/visualize')
def visualize():
    """
    GET API endpoint to read and visualize the data from MongoDB
    Parameters:
    - record_id (str): Record Identifier to retrieve from MongoDB
    Returns:
    - Response: PNG image of the data
    """
    try:
        record_id = request.args.get('record_id')
        db_handler.connect()
        record = db_handler.get_record(record_id)
        df_json_from_mongo = record['data']
        df_from_mongo = pd.read_json(df_json_from_mongo, orient='records')

        plt.subplots(dpi=100)
        plt.imshow(df_from_mongo, cmap='viridis')
        plt.title(record["time"], pad=10, fontsize=5, color="black", weight='bold')

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()
        return Response(buffer.getvalue(), mimetype='image/png')
    except Exception as e:
        print(f"Exception in visualizing data from Mongo: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        db_handler.close_connection()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
