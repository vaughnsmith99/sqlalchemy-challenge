import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
msmt = Base.classes.measurement
stat = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
root_name = "/api/v1.0/"

#################################################
# Flask Routes
#################################################

@app.route("/")
def routes():
    return f'''
            <!DOCTYPE HTML>
            <html>
            <body>
            
            <h1>Welcome to the API for Hawaii Climate!</h1>
            <h2>Here are the available routes:</h2>

            <ul>
            <li><a href="{root_name}precipitation">Precipitation - {root_name}precipitation</a></li>
            <li><a href="{root_name}stations">Stations - {root_name}stations</a></li>
            <li><a href="{root_name}tobs">Tobs - {root_name}tobs</a></li>
            <li>If you want to filter by the start date: {root_name}[yyyy-mm-dd]</li>
            <li>If you want to filter by the start and end dates: {root_name}[yyyy-mm-dd]/[yyyy-mm-dd]</li>
            </ul>

            </body>
            </html>)'''

# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(msmt.date, msmt.prcp).all()
    session.close()
    prec = list(np.ravel(results))
    dct = {prec[i]: prec[i + 1] for i in range(0, len(prec))}
    print(dct)
    return jsonify(dct)

# Return a JSON list of stations from the dataset.   
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(stat.name).all()
    session.close()
    stat_list = list(np.ravel(results))
    dalist = [str(stat_list[i]) for i in range(0, len(stat_list))]
    print(dalist)
    return jsonify(dalist)

@app.route("/api/v1.0/tobs")
# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
def tobs():
    session = Session(engine)
    recent = session.query(msmt.date).order_by(msmt.date.desc()).first()
    session.close()
    _12mo = dt.datetime.strptime(recent[0], '%Y-%m-%d').date()

    # Calculate the date one year from the last date in data set.
    one_yr_ago = _12mo - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    msmt_date_tobs = [msmt.date,msmt.tobs]
    msmt_date_tobs_query = session.query(*msmt_date_tobs).\
                                                            filter(msmt.date>=one_yr_ago).all()
    return jsonify(msmt_date_tobs_query)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
@app.route("/api/v1.0/<start>")
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

def start(start):
    session = Session(engine)
    date_query = session.query(msmt.date).filter(msmt.date >= start)
    session.close()
    readable = dt.datetime.strptime(date_query, '%Y-%m-%d').date()
    return jsonify(readable)

@app.route("/api/v1.0/<start>/<end>")
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

def start_end(start, end):
    session = Session(engine)
    date_query = session.query(msmt.date).filter(msmt.date >= start).\
        filter(msmt.date <= end)
    session.close()
    print(date_query)
    return jsonify(date_query)

if(__name__=='__main__'):
    app.run(debug=True)