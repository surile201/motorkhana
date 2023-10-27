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
    connection = mysql.connector.connect(user=connect.dbuser,
                                         password=connect.dbpass, host=connect.dbhost,
                                         database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn


@app.route("/")
def home():
    return render_template("base.html")


@app.route("/listdrivers")
def listdrivers():
    connection = getCursor()
    connection.execute("""
        SELECT driver.driver_id, driver.first_name, driver.surname, driver.date_of_birth, driver.age, driver.caregiver, car.model, car.drive_class 
        FROM driver
        JOIN car ON driver.car = car.car_num
        ORDER BY driver.surname, driver.first_name;
    """)
    driverList = connection.fetchall()
    return render_template("driverlist.html", driver_list=driverList)


@app.route("/listcourses")
def listcourses():
    connection = getCursor()
    connection.execute("SELECT * FROM course;")
    courseList = connection.fetchall()
    return render_template("courselist.html", course_list=courseList)


@app.route("/driverdetails/<int:driver_id>")
def driverdetails(driver_id):
    cursor = getCursor()
    cursor.execute("SELECT driver_id, first_name, surname FROM driver")
    driver_data = cursor.fetchall()
    drivers = [{"driver_id": driver[0], "name": f"{driver[1]} {driver[2]}"}
               for driver in driver_data]
    cursor.execute("""
        SELECT driver.driver_id, driver.first_name, driver.surname, car.model, car.drive_class
        FROM driver
        JOIN car ON driver.car = car.car_num
        WHERE driver.driver_id = %s
    """, (driver_id,))
    driver = cursor.fetchone()
    driver_details = {
        'driver_id': driver[0],
        'name': f"{driver[1]} {driver[2]}",
        'car_model': driver[3],
        'drive_class': driver[4]
    }
    cursor.execute("""
    SELECT run.dr_id, run.crs_id, run.run_num, course.name AS course_name, run.*
    FROM run
    JOIN course ON run.crs_id = course.course_id
    WHERE run.dr_id = %s
""", (driver_id,))
    runs = cursor.fetchall()
    run_details = []

    for run in runs:
        dr_id = run[0]
        crs_id = run[1]
        run_num = run[2]
        course_name = run[3]
        seconds = run[7] if run[7] is not None else 0
        cones = run[8] if run[8] is not None else 0
        wd = run[9] if run[9] is not None else 0
        total_time = seconds + cones * 5 + wd * 10

        run_details.append({
            'dr_id': dr_id,
            'crs_id': crs_id,
            'run_num': run_num,
            'course_name': course_name,
            'seconds': seconds,
            'cones': cones,
            'wd': wd,
            'total_time': total_time
        })
    return render_template("driverdetails.html", driver=driver_details, runs=run_details, drivers=drivers)


@app.route("/graph")
def showgraph():
    connection = getCursor()
    connection.execute('''
    WITH BestRuns AS (
        SELECT 
            dr_id,
            crs_ID,
            MIN(seconds + cones * 5 + wd * 10) as best_second_per_course
        FROM 
            run
        GROUP BY
            dr_id, crs_ID
    ), OverallResult AS (
        SELECT 
            dr_id,
            SUM(best_second_per_course) as total_second
        FROM 
            BestRuns
        WHERE 
            crs_ID IN ('A', 'B', 'C', 'D', 'E', 'F')
        GROUP BY 
            dr_id
        HAVING 
            COUNT(DISTINCT crs_ID) = 6
    )
    SELECT 
        d.driver_id, d.first_name, d.surname, overall.total_second
    FROM
        driver d
    JOIN
        OverallResult overall ON d.driver_id = overall.dr_id
    ORDER BY
        overall.total_second DESC
    LIMIT 5;
    '''
                       )
    drivers = connection.fetchall()
    names = [f"{driver[1]} {driver[2]}" for driver in drivers]
    seconds = [driver[3] for driver in drivers]
    return render_template("top5graph.html", names=names, scores=seconds)

    # Insert code to get top 5 drivers overall, ordered by their final results.
    # Use that to construct 2 lists: bestDriverList containing the names, resultsList containing the final result values
    # Names should include their ID and a trailing space, eg '133 Oliver Ngatai '


@app.route("/results")
def results():
    connection = getCursor()
    connection.execute("""
    SELECT 
    d.driver_id,
    d.first_name,
    d.surname,
    d.age,
    c.model AS car_model,
    r.crs_id,
    MIN(r.seconds) AS best_second
    FROM driver AS d
    JOIN car AS c ON d.car = c.car_num
    LEFT JOIN run AS r ON d.driver_id = r.dr_id
    GROUP BY d.driver_id, d.first_name, d.surname, d.age, c.model, r.crs_id;
    """)
    results = connection.fetchall()
    drivers_data = {}
    for result in results:
        driver_id = result[0]
        full_name = f"{result[1]} {result[2]}" + (" (J)" if result[3] and result[3] < 25 else "")
        if driver_id not in drivers_data:
            drivers_data[driver_id] = {
                'driver_id': driver_id,
                'full_name': full_name,
                'car_model': result[4],
                'courses': {},
                'overall': 0
            }
        best_second = result[6] if result[6] else 'DNF'
        course_id = result[5]

        drivers_data[driver_id]['courses'][course_id] = best_second

        if best_second == 'DNF':
            drivers_data[driver_id]['overall'] = 'NQ'
        elif drivers_data[driver_id]['overall'] != 'NQ':
            drivers_data[driver_id]['overall'] += best_second
    drivers_list = list(drivers_data.values())
    drivers_list.sort(key=lambda x: (x['overall'] == 'NQ', x['overall']))
    top_ids = [driver['driver_id'] for driver in drivers_list[:5]]
    return render_template("results.html", drivers=drivers_list, top_ids=top_ids)


# Admin code


@app.route("/driverjr")
def juniordrivers():
    cursor = getCursor()
    cursor.execute("""
        SELECT driver.driver_id, driver.first_name, driver.surname, driver.age, driver.caregiver
        FROM driver
        WHERE driver.age < 25
        ORDER BY driver.age DESC, driver.surname, driver.first_name;
    """)
    juniorDriverList = cursor.fetchall()
    drivers = [{'id': driver[0], 'first_name': driver[1], 'surname': driver[2],
                'age': driver[3], 'caregiver': driver[4]} for driver in juniorDriverList]

    return render_template("driverjr.html", junior_drivers=drivers)


@app.route("/search", methods=['GET', 'POST'])
def searchdrivers():
    drivers = []
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        cursor = getCursor()
        query = """
            SELECT driver.first_name, driver.surname
            FROM driver
            WHERE driver.first_name LIKE %s OR driver.surname LIKE %s
        """
        cursor.execute(query, ('%' + search_term +
                       '%', '%' + search_term + '%'))
        results = cursor.fetchall()
        print(results)
        drivers = [{'first_name': result[0], 'last_name': result[1]}
                   for result in results]
    return render_template("search.html", drivers=drivers)


@app.route('/edit_run/<int:dr_id>/<crs_id>/<int:run_num>', methods=['GET'])
def edit_run(dr_id, crs_id, run_num):
    cursor = getCursor()
    cursor.execute(
        "SELECT * FROM run WHERE dr_id = %s AND crs_id = %s AND run_num = %s", (dr_id, crs_id, run_num))
    run_data = cursor.fetchone()
    run_details = {
        "dr_id": run_data[0],
        "crs_id": run_data[1],
        "run_num": run_data[2],
        "seconds": run_data[3],
        "cones": run_data[4],
        "wd": run_data[5]
    }
    return render_template('edit_run.html', run=run_details)


@app.route('/update_run/<int:dr_id>/<crs_id>/<int:run_num>', methods=['POST'])
def update_run(dr_id, crs_id, run_num):
    cursor = getCursor()
    seconds = request.form.get('seconds')
    cones = request.form.get('cones')
    wd = request.form.get('wd')
    cursor.execute("""
        UPDATE run 
        SET seconds = %s, cones = %s, wd = %s
        WHERE dr_id = %s AND crs_id = %s AND run_num = %s
    """, (seconds, cones, wd, dr_id, crs_id, run_num))
    return redirect(url_for('driverdetails', driver_id=dr_id))


@app.route('/add_driver', methods=['GET'])
def add_driver_form():
    cursor = getCursor()
    cursor.execute("SELECT car_num, model FROM car")
    cars = cursor.fetchall()
    cursor.execute(
        "SELECT driver_id, first_name, surname FROM driver WHERE age >= 25 OR age IS NULL")
    caregivers = cursor.fetchall()
    caregiver_list = [{"driver_id": caregiver[0], "first_name": caregiver[1],
                       "surname":caregiver[2]} for caregiver in caregivers]
    car_list = [{"car_num": car[0], "model": car[1]} for car in cars]
    return render_template('add_driver.html', cars=car_list, caregivers=caregiver_list)


@app.route('/add_driver', methods=['POST'])
def add_driver():
    cursor = getCursor()
    first_name = request.form.get('first_name')
    surname = request.form.get('surname')
    car = request.form.get('car')
    if request.form.get('is_junior') == 'on':
        date_of_birth = request.form.get('dob')
        caregiver = request.form.get('caregiver')
        birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d")
        today = datetime.today()
        age = today.year - birth_date.year - \
            ((today.month, today.day) < (birth_date.month, birth_date.day))
    else:
        date_of_birth = None
        caregiver = None
        age = None

    cursor.execute("""
        INSERT INTO driver (first_name, surname, date_of_birth, age, caregiver, car)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (first_name, surname, date_of_birth, age, caregiver, car))

    cursor.execute("SELECT LAST_INSERT_ID()")
    new_driver_id = cursor.fetchone()[0]

    for crs_id_ascii in range(ord('A'), ord('G')):
        crs_id = chr(crs_id_ascii)
        for run_num in [1, 2]:
            cursor.execute("""
                INSERT INTO run (dr_id, crs_id, run_num, seconds, cones, wd)
                VALUES (%s, %s, %s, NULL, NULL, 0)
            """, (new_driver_id, crs_id, run_num))

    return redirect(url_for('driverdetails', driver_id=new_driver_id))
