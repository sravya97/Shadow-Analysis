"""
Server to perform Shadow Analysis and store the data in MongoDB
"""
from flask import Flask, jsonify
import configparser
from solarposition import *
from shadowingfunction_wallheight_13 import shadowingfunction_wallheight_13
from DatabaseHandler import MongoDBHandler

config = configparser.ConfigParser()
config.read('config.ini')

db_name = config['database']['DB_NAME']
collection_name = config['database']['COLLECTION_NAME']
connection_string = config['database']['CONNECTION_STRING']

app = Flask(__name__)
db_handler = MongoDBHandler(db_name=db_name, collection_name=collection_name,
                            connection_string=connection_string)


@app.get('/analyze')
def analyze():
    """
    GET API endpoint to do shadow analysis with current time and store the data
    Returns:
    - Response: Record identifier of the output data in MongoDB
    """
    try:
        current_timestamp = pd.Timestamp.now()
        record = perform_shadow_analysis(current_timestamp)
        record_id = store_shadow_data(record)
        response = {'record_id': record_id}
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def perform_shadow_analysis(timestamp):
    """
    Execute shadow analysis
    Parameters:
    - timestamp (pandas time): Timestamp to perform the analysis
    Returns:
    - dict: Shadow data in the form of dictionary
    """
    try:
        dsm = np.load('./dsm_local_array.npy')
        dsm = np.nan_to_num(dsm, nan=0)

        lon = -95.30052
        lat = 29.73463
        utc_offset = -6

        df_solar_data = pd.DataFrame({'TimeStamp': [timestamp]})
        df_solar_data['TimeStamp'] = pd.DatetimeIndex(df_solar_data['TimeStamp']) - pd.DateOffset(hours=utc_offset)
        # To_Datetime
        df_solar_data["TimeStamp"] = df_solar_data["TimeStamp"].apply(pd.to_datetime)
        df_solar_data.set_index("TimeStamp", inplace=True)

        # Add time index
        df_solar_data["TimeStamp"] = df_solar_data.index

        df_solar = get_solarposition(df_solar_data.index, lat, lon)

        # Add time index
        df_solar['TimeStamp'] = pd.DatetimeIndex(df_solar.index) + pd.DateOffset(hours=utc_offset)

        df_solar = df_solar[['TimeStamp', 'apparent_zenith', 'zenith', 'apparent_elevation', 'elevation',
                             'azimuth', 'equation_of_time']]

        # To_Datetime
        df_solar["TimeStamp"] = df_solar["TimeStamp"].apply(pd.to_datetime)
        df_solar.set_index("TimeStamp", inplace=True)

        df_solar["TimeStamp"] = df_solar.index
        df_solar = df_solar[['TimeStamp', 'elevation', 'zenith', 'azimuth']]

        df_solar = df_solar.rename(columns={"elevation": "Elevation", "azimuth": "Azimuth", "zenith": "Zenith"})

        scale = 1
        walls = np.zeros((dsm.shape[0], dsm.shape[1]))
        dirwalls = np.zeros((dsm.shape[0], dsm.shape[1]))

        i = 0

        altitude = df_solar['Elevation'][i]
        azimuth = df_solar['Azimuth'][i]

        hour = df_solar.index[i].hour
        minute = df_solar.index[i].minute

        sh, wallsh, wallsun, facesh, facesun = shadowingfunction_wallheight_13(dsm, azimuth, altitude, scale, walls,
                                                                               dirwalls * np.pi / 180.)

        df = pd.DataFrame(sh)
        record = {
            'timestamp': timestamp,
            'time': "%2s" % str(hour).zfill(2) + ":%2s" % str(minute).zfill(2),
            'data': df.to_json(orient='records')
        }
        return record
    except Exception as e:
        raise Exception(f"Exception in performing shadow analysis: {str(e)}")


def store_shadow_data(record):
    """
    Store the data from shadow analysis into MongoDB.
    Parameters:
    - record (dict): Data to insert into MongoDB
    Returns:
    - str: Identifier of the inserted record
    """
    try:
        db_handler.connect()
        inserted_id = db_handler.insert_record(record)
    except Exception as e:
        raise Exception(f"Exception in storing shadow data: {str(e)}")
    finally:
        db_handler.close_connection()
    return str(inserted_id)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000)





