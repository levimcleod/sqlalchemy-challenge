import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# Database Setup

engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the tables
measure = Base.classes.measurement

station = Base.classes.station



# Flask Setup

app = Flask(__name__)



# Flask Routes


@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format YYYY-MM-DD.</p>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    
    try:
        # Create our session (link) from Python to the DB
        session = Session(engine)
    
        latest_date = session.query(measure.date).order_by(measure.date.desc()).first()[0]

        query_date = pd.to_datetime(latest_date) - dt.timedelta(days=365)

        query_date_string = query_date.strftime("%Y-%m-%d")

        # Perform a query to retrieve the data and precipitation scores

        precip_data = session.query(measure.date, measure.prcp).\
                   filter(measure.date >= query_date_string).\
                   order_by(measure.date.desc()).all()

        session.close()
        
        precip_data_dict = {date: prcp for date, prcp in precip_data}
        
        return jsonify(precip_data_dict)
    
    except Exception as e:
        
        return jsonify({"error": str(e)}), 500
    
    
@app.route("/api/v1.0/stations")
def stations():
    try:
        # Create our session (link) from Python to the DB
        session = Session(engine)

        # Perform a query to retrieve the list of stations
        stations_data = session.query(station.station).all()

        session.close()

        # Extract the list of stations from the query results
        stations_list = [s[0] for s in stations_data]

        return jsonify(stations_list)
    
    except Exception as e:
        
        return jsonify({"error": str(e)}), 500

    
@app.route("/api/v1.0/tobs")
def tobs():
    try:
        # Create our session (link) from Python to the DB
        session = Session(engine)

        latest_date = session.query(measure.date).order_by(measure.date.desc()).first()[0]

        query_date = pd.to_datetime(latest_date) - dt.timedelta(days=365)

        query_date_string = query_date.strftime("%Y-%m-%d")

        # Perform a query to retrieve the data for the most active station
        station_data = session.query(measure.date, measure.tobs).\
        filter(measure.station == 'USC00519281').\
        filter(measure.date >= query_date_string).all()

        session.close()

        # convert the list of tuples into a dictionary
        station_data_dict = {date: tobs for date, tobs in station_data}

        return jsonify(station_data_dict)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1.0/<start>")
def start(start):
    try:
        # Create our session (link) from Python to the DB
        session = Session(engine)

        # Perform a query to retrieve the temperature data for the given start date
        temp_data = session.query(func.min(measure.tobs), func.avg(measure.tobs), func.max(measure.tobs)).\
            filter(measure.date >= start).all()

        session.close()

        # Extract the temperature data from the query results
        min_temp, avg_temp, max_temp = temp_data[0]

        # Create a JSON list of the temperature data
        temp_list = [
            {"Minimum Temperature": min_temp},
            {"Average Temperature": avg_temp},
            {"Maximum Temperature": max_temp}
        ]

        return jsonify(temp_list)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    try:
        # Create our session (link) from Python to the DB
        session = Session(engine)

        # Perform a query to retrieve the temperature data for the given date range
        temp_data = session.query(func.min(measure.tobs), func.avg(measure.tobs), func.max(measure.tobs)).\
            filter(measure.date >= start).filter(measure.date <= end).all()

        session.close()

        # Extract the temperature data from the query results
        min_temp, avg_temp, max_temp = temp_data[0]

        # Create a JSON list of the temperature data
        temp_list = [
            {"Minimum Temperature": min_temp},
            {"Average Temperature": avg_temp},
            {"Maximum Temperature": max_temp}
        ]

        return jsonify(temp_list)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
    
if __name__ == '__main__':
    app.run(debug=True)

        
        
        
        
        
        