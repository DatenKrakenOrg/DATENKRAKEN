# Uptime monitoring

In order to get the uptime of the database, a cronjob can be used.
Since a cronjob is already in use by the backup strategy of the database, it is straight forward to setup up another one.
The [Quality Goals](/arc42/01. Introduction and Goals) state that the uptime needs to be measured every minute the system is running.
Therefore the cronjob will run a script that creates an entry into a CSV-File every minute.
This entry contains the start Unix timestamp of the database and the current timestamp, when the start timestamp was requested.
The start Unix timestamp of the database is retrieved via a request to the database, since postgres has an internal timer, which keeps track of the startup timestamp.

If the database is not reachable because of unexpected failure, the script will write the default value zero into the CSV-File.
