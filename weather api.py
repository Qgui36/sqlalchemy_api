import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
   )

year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Perform a query to retrieve the last 12 months of precipitation data.
    results=session.query(Measurement.date,func.sum(Measurement.prcp)).group_by(Measurement.date).filter(Measurement.date>year_ago).all()
    # Create a dictionary from the row data and append to a list of date_prcp
    date_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        date_prcp.append(prcp_dict)

    return jsonify(date_prcp)
 
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    # Query all stations
    results = session.query(func.distinct(Station.station)).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def temp():
    # find the most active station
    active_station=session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    most_act_stat = active_station[0]
    # Perform a query to retrieve the last 12 months of temperature data from the most acitve station.
    results=session.query(Measurement.date, Measurement.tobs).filter(Measurement.station==most_act_stat).filter(Measurement.date>year_ago).all()
    # Create a dictionary from the row data and append to a list of date_temp
    date_temp = []
    for date, temp in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = temp
        date_temp.append(temp_dict)

    return jsonify(date_temp)

@app.route("/api/v1.0/<start_date>")
def start(start_date):

    # Perform a query to retrieve minimum temperature, the average temperature, and the max temperature
    # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    return jsonify(results[0])

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date,end_date):
    # Perform a query to retrieve minimum temperature, the average temperature, and the max temperature
    # When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)

