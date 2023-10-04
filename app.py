from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)

dbconn = None
connection = None

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

@app.route("/")
def home():
    return render_template("base.html")

@app.route("/listdrivers")
def listdrivers():
    connection = getCursor()
    connection.execute("SELECT * FROM driver;")
    driverList = connection.fetchall()
    print(driverList)
    return render_template("driverlist.html", driver_list = driverList)    

@app.route("/listcourses")
def listcourses():
    connection = getCursor()
    connection.execute("SELECT * FROM course;")
    courseList = connection.fetchall()
    return render_template("courselist.html", course_list = courseList)

@app.route("/graph")
def showgraph():
    connection = getCursor()
    # Insert code to get top 5 drivers overall, ordered by their final results.
    # Use that to construct 2 lists: bestDriverList containing the names, resultsList containing the final result values
    # Names should include their ID and a trailing space, eg '133 Oliver Ngatai '
    connection.execute('''WITH OverallResults as (Select dr_id,SUM(seconds + cones * 5 + Wd * 10) as total_second
                    FROM run GROUP BY dr_id
                    HAVING COUNT(crs_ID)= 6)
                    SELECT d.driver_id,d.name,or.total_second
                    FROM driver d JOIN OverallResults or ON d.driver_id = or.dr_id
                    ORDER BY or.total_second DESC 
                    LIMIT 5;
    ''')
    driverList = connection.fetchall()
    bestDriverList = []
    resultsList = []
    for driver in driverList:
        bestDriverList.append(str(driver[0]) + " " + driver[1] + " ")
        resultsList.append(driver[2])

    return render_template("top5graph.html", name_list = bestDriverList, value_list = resultsList)

