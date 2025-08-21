# NFR testability
There are three [Quality Goals](/arc42/01. Introduction and Goals) which need to be tested.

## NFR 1.1 
The criteria from the NFR 1.1 states that the measured sensor data must reach the bronze layer of the database within 5 minutes.
The silver and gold layers are based on the bronze layer, therefore only a few calculations are needed for the bronze data to be viewable inside of the those layers.
Therefore the time, which is needed for the the data transfer from bronze to silver and from silver to gold is negligible.
This is the reasoning, why the time measurement between sensor and bronze is  accurate enough to evaluate the NFR 1.1.

For the established measurement scope, the validity of the data transfertime with the limit of 5 minutes can be evaluated now.
A function in the frontend takes care of the validation of this NFR.
The function should take the timestamp of the sensor data and creates a comparison between the current timestamp across multiple sensortypes.
The NFR 1.1 is valid, if all comparisons result in a time difference below 5 minutes.
The frontend should also display the result of the comparisons.

## NFR 1.2
To measure the quality goal for the NFR 1.2, a script is used to determine the uptime of the database.
In order to calculate the uptime a log of the uptime is needed. The [Uptime Monitoring](/indepth/uptime-monitoring) is already covered.
Therefore the already exsitent CSV-File needs to be evaluated, such that an uptime for the last week can be calculated.
To achieve this, a python script is used to read the CSV-File and relatively calculate a weekly uptime based on this file.

## NFR 3.1
The NFR 3.1 is a criterea for accessibility. The Quantification of a accessibility criteria is usually difficult.
There isn't any existing data or collectable logs for the quantification for this non functional requirement.
A usual best practice for UI-Testing and validation are user tests.
Thats the reason why this project is also relying on user tests to quantify the NFR 3.1.

| Metric                     | How to Measure                                                                                                                     |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **Task completion rate**   | Percentage of users able to complete key tasks (e.g., navigate dashboard, use filters, submit forms) **without using a keyboard**. |
| **Time to complete tasks** | Average time users take to finish a task with mouse/trackpad alone. Compare against expected baseline.                             |
| **Error rate**             | Number of times a user fails or misclicks because a function isn’t accessible without keyboard.                                    |
| **UI coverage**            | Percentage of interactive elements reachable and usable without a keyboard.                                                        |
| **Shortcut reliance**      | Number of functions that **cannot** be accessed without keyboard shortcuts. Should be 0 for this NFR.                              |
