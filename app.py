# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt

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
Base.prepare(autoload_with=engine)
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB

session= Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Function Difining
def get_year_ago_date():
    session = Session(engine)
    latest_date = session.query(func.max(Measurement.date)).scalar()
    session.close()
    return dt.datetime.strptime(latest_date, "%Y-%m-%d") - dt.timedelta(days=365)


@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Welcome!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>")


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    recentdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recentdate = dt.date(2017,8,23)
    year_from_lastdate = (recentdate - dt.timedelta(days = 365))
    prcpquery = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_from_lastdate).all()
    session.close()

    if not prcpquery:
        return jsonify({"error": "No Precipitation Data Found."})

    precipitation_data = {date: prcp for date, prcp in prcpquery}

    return jsonify(precipitation_data)



@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station = session.query(Station.name).all()
    session.close()

    if not station:
        return jsonify({"error": "No Data Found."})

    station_list = list(np.ravel(station))

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    year_ago_date = get_year_ago_date()

    tobs_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= year_ago_date).all()
    session.close()

    if not tobs_results:
        return jsonify({"error" : "No temperature observation data found."})
    
    tobs_data = [{"date": date, "temperature": tobs} for date, tobs in tobs_results]

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    Start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= Start_date).all()
    session.close()
    # Convert list of tuples into normal list
    if not temp_data or temp_data[0][0] is None:
        return jsonify({"error": "No temperature data found for the given start date."})

    min_temp, max_temp, avg_temp = temp_data[0]

    # Format the results as a dictionary
    temp_data_output = {
        "Start Date": start,
        "Minimum Temperature": min_temp,
        "Maximum Temperature": max_temp,
        "Average Temperature": avg_temp
    }

    return jsonify(temp_data_output)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    Start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    End_date = dt.datetime.strptime(end, "%Y-%m-%d")
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).all()
    session.close()
    # Convert list of tuples into normal list
    if not temp_data or temp_data[0][0] is None:
        return jsonify({"error": "No temperature data found for the given start date."})

    min_temp, max_temp, avg_temp = temp_data[0]

    # Format the results as a dictionary
    temp_data_output = {
        "Start Date": start,
        "End Date": end,
        "Minimum Temperature": min_temp,
        "Maximum Temperature": max_temp,
        "Average Temperature": avg_temp
    }

    return jsonify(temp_data_output)

if __name__ == '__main__':
    app.run(debug=True)