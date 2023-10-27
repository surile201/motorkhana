# Structure

## Templates
* base.html: main template for navigating to other templates. Route: /
* add_driver.html: the template used for adding the driver. 
    * Route: /
    * After adding driver, the system will navigate to driver details and passes new driver's information to driver details to display
* courselist.html: the template used for displaying all courses. 
    * Route: /listcourses. 
    * Data passed: courseList (list of courses from database)
* driverdetails.html: template used for displaying driver details. 
    * Route: /driverdetails/<int:driver_id> . 
    * Data passed: driver_details (details of the driver), runs (details of the run).
    * Fromt his template, the system can navigate to edit run information and pass run details and driver details to update results for driver
* driverjr.html: the template used for displaying the list of junior drivers. 
    * Route: /driverjr
    * Data passed: junior_drivers (list of junior drivers)
* driverlist.html: the template used for displaying the list of drivers. 
    * Route: /listdrivers. 
    * Data passed: driverList (list of drivers from database)
    * From this template, the system can navigate to driver details to show all information about driver.
* edit_run.html: the template used for editing run information.
    * Route: /edit_run/<int:dr_id>/<crs_id>/<int:run_num>
    * Data passed: run details for editing and then pass driver details to update results for the driver.
* results.html: the template used for displaying results. 
    * Route: /results. 
    * Data passed: results_list (result for each driver), 
* search.html: the template used for searching drivers
    * Route: /search
    * Data passed: drivers (driver details for query database)
* top5graph.html: the template used for displaying bar charts. 
    * Route: /graph. 
    * Data passed: names (name of the driver), seconds (total seconds for each driver)

## Assumption
* Use Bootstrap to display the junior drivers in yellow -> I assume to highlight the cell containing the junior driver's name in the table

## Design Idea
* I create one template and one backend function for one feature. By doing that, I can easily manage my work, minimise bugs and easily debug.
* I use table and basic bootstrap properties to make the front end better and more straightforward. The data also can be displayed clearly
* In the search function, I use GET and POST methods to send data to the backend and receive the result from the backend. In search function, I have to send name from front end to backend server to query, so that I use POST to send data. Then, I use GET method to get data from backend.
* In the add driver function, I use POST method to send and store driver data in backend.

## Database Question

* What SQL statement creates the car table and defines its three fields/columns? (Copy and paste the relevant lines of SQL)

    * CREATE TABLE IF NOT EXISTS car
    (
    car_num INT PRIMARY KEY NOT NULL,
    model VARCHAR(20) NOT NULL,
    drive_class VARCHAR(3) NOT NULL
    );

* Which line of SQL code sets up the relationship between the car and driver tables?

    * FOREIGN KEY (car) REFERENCES car(car_num)
    ON UPDATE CASCADE
    ON DELETE CASCADE

* Which 3 lines of SQL code insert the Mini and GR Yaris details into the car table?

    * INSERT INTO car VALUES
    (11,'Mini','FWD'),
    (17,'GR Yaris','4WD'),

* Suppose the club wanted to set a default value of ‘RWD’ for the driver_class field. What specific change would you need to make to the SQL to do this? (Do not implement this change in your app.)

    * Change drive_class VARCHAR(3) NOT NULL to drive_class VARCHAR(3) NOT NULL DEFAULT 'RWD'

* Suppose logins were implemented. Why is it important for drivers and the club admin to access different routes? As part of your answer, give two specific examples of problems that could occur if all of the web app  facilities were available to everyone.
    * Accessing different routes based on drivers and the club admin is extremely important to ensure the security, sensitive content and database management. Two Specific problems:
        ** If drivers and guests can access the database, they can add, modify and delete information, such as driver details, car details, and results. It may lead to incorrect results and other problems for competition.

        **  Users can also use admin management tools such as system settings, user management or database reset. Hence, some will take this advantage to break the competition.