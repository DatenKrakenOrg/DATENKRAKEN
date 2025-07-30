# Backup Strategy

This document will describe how we choose to backup our database in case of unexpected crashes or unrecoverable states.

## Expectation from the Backup Strategy
1. No interference with current dataflow
2. Everything is inside the backup
3. The data backup is written automatically via a cronjob or systemd-unit
4. The data restoring is performed manually or with a manually exectuable script
5. A Backup with a timestamp is created every 6H

# Implementation
To meet the expectations and criterias, which are needed in order to have a successful backup strategy, there are two ways to solve this  
1. cronjob
2. Systemd-Unit

Although systemd units are more complex to configure, they offer more options for controlling them.
In theory a systemd-unit would also be suitable for backing up the data.  
Nevertheless in the scope of the project it is not possible to run those systemd-units, even in user-space, because of lack of privilege.
Therefore a cronjob is used in order to run the backup bashscript.
The entire backup process produces a GZip file as a result, which contains the database dump.
The restore process is **not** automatic.  
To ensure that the data is not only stored on the server's hard disk in the event of a total failure, the dumps are also archived on individual devices of the members of this project.
