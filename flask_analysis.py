import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
measurement_table = Base.classes.measurement
station_table = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
# Saved globals
most_active_station = 'USC00519281'
most_recent_date = '2017-08-23'
previous_year = '2016-08-23'
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# List all routes that are available.
@app.route("/")
def home():
    return (
        f'Available Routes:<br/>'
        f' /api/v1.0/precipitation<br/>'
        f' /api/v1.0/stations<br/>'
        f' /api/v1.0/tobs<br/>'
        f' /api/v1.0/<start><br/>'
        f' /api/v1.0/<start>/<end>'
    )
# Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def prcp():
    all_data = session.query(measurement_table.date, measurement_table.prcp).\
               order_by(measurement_table.date).all()
    prcp_data = dict(all_data)
    return jsonify(prcp_data)
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    stations_data = session.query(station_table.name, station_table.station).all()
    stations_list = list(np.ravel(stations_data))
    return jsonify(stations_list)
# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    tobs_data = session.query(measurement_table.date, measurement_table.tobs).\
                filter(measurement_table.date >= previous_year).\
                filter(measurement_table.station == most_active_station).\
                order_by(measurement_table.date).all()
    tobs_list = list(np.ravel(tobs_data))
    return jsonify(tobs_list)
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def start(start):
    start_data = session.query(func.min(measurement_table.tobs),\
                               func.avg(measurement_table.tobs),\
                               func.max(measurement_table.tobs)).\
                 filter(measurement_table.date >= start).all()
    stat_list = list(np.ravel(start_data))
    return jsonify(stat_list)

# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    between_date_data = session.query(func.min(measurement_table.tobs),\
                                      func.avg(measurement_table.tobs),\
                                      func.max(measurement_table.tobs)).\
                        filter(measurement_table.date >= start).\
                        filter(measurement_table.date <= end).all()
    between_date_list = list(np.ravel(between_date_data))
    return jsonify(between_date_list)

# Close session
session.close()


if __name__ == "__main__":
    app.run(debug=True)
