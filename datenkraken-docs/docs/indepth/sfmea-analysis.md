# SFMEA

# Components - Functinalities of the System
- Arduino
- Subscription script
- Database
- UI -> Work in progress, because of LRM

---

# Classification
1. Deployment 
2. Runtime Failures
3. Design/Conceptional Mistakes


<table cellspacing="0" cellpadding="8">
  <thead>
    <tr>
      <th>ID</th>
      <th>Component</th>
      <th>Failure Mode</th>
      <th>Failure mode</th>
      <th>Cause of Failure</th>
      <th>Effect of Failure</th>
    </tr>
  </thead>
  <tbody>
    <!-- Arduino -->
    <tr>
      <td>FA1</td>
      <td>Arduino</td>
      <td>Data Missing</td>
      <td>Loss of function</td>
      <td>Power loss, sensor hardware error</td>
      <td>End effect: Database, UI, Subscriber script</td>
    </tr>
    <tr>
      <td>FA2</td>
      <td>Arduino</td>
      <td>Data Inaccurate</td>
      <td>Incorrect function</td>
      <td>Power loss, Sensor inaccuracy</td>
      <td>End effect: Database, UI, Subscriber script</td>
    </tr>
    <tr>
      <td>FA3</td>
      <td>Arduino</td>
      <td>Data Timeless</td>
      <td>Erroneous function</td>
      <td>Power loss, NTP Server not reachable</td>
      <td>End effect: Database, UI, Subscriber script</td>
    </tr>
    <tr>
      <td>FA4</td>
      <td>Arduino</td>
      <td>Erroneous/Inconsistent Datapoints</td>
      <td>Loss of function</td>
      <td>Power loss, Unexpected Environmental influences</td>
      <td>End effect: Database, UI, Subscriber script</td>
    </tr>
    <tr>
      <td>FA5</td>
      <td>Arduino</td>
      <td>Data cannot be transferred</td>
      <td>Erroneous function</td>
      <td>Power loss, Server not reachable</td>
      <td>End effect: Database, UI, Subscriber script</td>
    </tr>
    <!-- Subscription Script -->
    <tr>
      <td>FA6</td>
      <td>Subscription Script</td>
      <td>Data cannot be received (from MQTT-Server)</td>
      <td>Loss of function</td>
      <td>Arduino down</td>
      <td>End effect: Database, UI</td>
    </tr>
    <tr>
      <td>FA7</td>
      <td>Subscription Script</td>
      <td>Data cannot be transferred (to the database)</td>
      <td>Erroneous function</td>
      <td>Database connection error, Database down</td>
      <td>End effect: Database, UI</td>
    </tr>
    <!-- Database -->
    <tr>
      <td>FA8</td>
      <td>Database</td>
      <td>Not available (permanent)</td>
      <td>Loss of function</td>
      <td>DHBW-Server down/crashed</td>
      <td>End effect: Database, UI, Subscriber script</td>
    </tr>
    <tr>
      <td>FA9</td>
      <td>Database</td>
      <td>Not available (temporary)</td>
      <td>Loss of function</td>
      <td>Restart / Maintenance / Overload</td>
      <td>End effect: Database, UI, Subscriber script</td>
    </tr>
    <tr>
      <td>FA10</td>
      <td>Database</td>
      <td>Faulty data cleaning</td>
      <td>Incorrect function</td>
      <td>Incorrect scripting code</td>
      <td>End effect: Database, UI, Subscriber script</td>
    </tr>
    <tr>
      <td>FA11</td>
      <td>Database</td>
      <td>Reading not possible</td>
      <td>Incorrect function</td>
      <td>Query issue / Permission issue</td>
      <td>End effect: Database, UI, Subscriber script</td>
    </tr>
    <tr>
      <td>FA12</td>
      <td>Database</td>
      <td>Writing not possible</td>
      <td>Incorrect function</td>
      <td>Disk full / Permission issue</td>
      <td>End effect: Database, UI, Subscriber script</td>
    </tr>
  </tbody>
</table>

# Risk and Criticality
1. (S)everity can be rated in a scope of 1 (No effect) - 10 (Severe System Failure)
2. (O)ccurrence can be rated in a likelyhood of 1 (Failure unlikely) - 10 (Failure is almost inevitable)
3. (D)etectability can be rated in a scope of detectable from 1 (certain to be detected) - 10 (Not likely to be detected)  
Risk priority number (RPN) = S * O * D, The higher the RPN, the more critical the failure mode.
<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>Component</th>
      <th>Failure Mode</th>
      <th>Failure mode</th>
      <th>Cause of Failure</th>
      <th>Effect of Failure</th>
      <th>Severity</th>
      <th>Occurrence</th>
      <th>Detection</th>
      <th>RPN (S×O×D)</th>
    </tr>
  </thead>
  <tbody>
    <!-- Arduino -->
    <tr>
      <td>FA1</td>
      <td>Arduino</td>
      <td>Data Missing</td>
      <td>Loss of function</td>
      <td>Power loss, sensor hardware error</td>
      <td>End effect: Database, UI, Subscriber script</td>
      <td>8</td>
      <td>5</td>
      <td>4</td>
      <td>160</td>
    </tr>
    <tr>
      <td>FA2</td>
      <td>Arduino</td>
      <td>Data Inaccurate</td>
      <td>Incorrect function</td>
      <td>Power loss, Sensor inaccuracy</td>
      <td>End effect: Database, UI, Subscriber script</td>
      <td>7</td>
      <td>6</td>
      <td>5</td>
      <td>210</td>
    </tr>
    <tr>
      <td>FA3</td>
      <td>Arduino</td>
      <td>Data Timeless</td>
      <td>Erroneous function</td>
      <td>Power loss, NTP Server not reachable</td>
      <td>End effect: Database, UI, Subscriber script</td>
      <td>6</td>
      <td>4</td>
      <td>6</td>
      <td>144</td>
    </tr>
    <tr>
      <td>FA4</td>
      <td>Arduino</td>
      <td>Erroneous/Inconsistent Datapoints</td>
      <td>Loss of function</td>
      <td>Power loss, Unexpected Environmental influences</td>
      <td>End effect: Database, UI, Subscriber script</td>
      <td>7</td>
      <td>5</td>
      <td>5</td>
      <td>175</td>
    </tr>
    <tr>
      <td>FA5</td>
      <td>Arduino</td>
      <td>Data cannot be transferred</td>
      <td>Erroneous function</td>
      <td>Power loss, Server not reachable</td>
      <td>End effect: Database, UI, Subscriber script</td>
      <td>8</td>
      <td>4</td>
      <td>6</td>
      <td>192</td>
    </tr>
    <!-- Subscription Script -->
    <tr>
      <td>FA6</td>
      <td>Subscription Script</td>
      <td>Data cannot be received (from MQTT-Server)</td>
      <td>Loss of function</td>
      <td>Arduino down</td>
      <td>End effect: Database, UI</td>
      <td>9</td>
      <td>3</td>
      <td>7</td>
      <td>189</td>
    </tr>
    <tr>
      <td>FA7</td>
      <td>Subscription Script</td>
      <td>Data cannot be transferred (to the database)</td>
      <td>Erroneous function</td>
      <td>Database connection error, Database down</td>
      <td>End effect: Database, UI</td>
      <td>9</td>
      <td>4</td>
      <td>6</td>
      <td>216</td>
    </tr>
    <!-- Database -->
    <tr>
      <td>FA8</td>
      <td>Database</td>
      <td>Not available (permanent)</td>
      <td>Loss of function</td>
      <td>DHBW-Server down/crashed</td>
      <td>End effect: Database, UI, Subscriber script</td>
      <td>10</td>
      <td>2</td>
      <td>2</td>
      <td>40</td>
    </tr>
    <tr>
      <td>FA9</td>
      <td>Database</td>
      <td>Not available (temporary)</td>
      <td>Loss of function</td>
      <td>Restart / Maintenance / Overload</td>
      <td>End effect: Database, UI, Subscriber script</td>
      <td>7</td>
      <td>5</td>
      <td>6</td>
      <td>210</td>
    </tr>
    <tr>
      <td>FA10</td>
      <td>Database</td>
      <td>Faulty data cleaning</td>
      <td>Incorrect function</td>
      <td>Incorrect scripting code</td>
      <td>End effect: Database, UI, Subscriber script</td>
      <td>6</td>
      <td>4</td>
      <td>5</td>
      <td>120</td>
    </tr>
    <tr>
      <td>FA11</td>
      <td>Database</td>
      <td>Reading not possible</td>
      <td>Incorrect function</td>
      <td>Query issue / Permission issue</td>
      <td>End effect: Database, UI, Subscriber script</td>
      <td>9</td>
      <td>3</td>
      <td>3</td>
      <td>81</td>
    </tr>
    <tr>
      <td>FA12</td>
      <td>Database</td>
      <td>Writing not possible</td>
      <td>Incorrect function</td>
      <td>Disk full / Permission issue</td>
      <td>End effect: Database, UI, Subscriber script</td>
      <td>9</td>
      <td>4</td>
      <td>3</td>
      <td>108</td>
    </tr>
  </tbody>
</table>

# Detection means
- EVIDENT: The failure is readily detected during operation.
- DORMANT: The failure can be detected when maintenance is performed.
- HIDDEN: The failure is not detected unless intentionally sought, for instance, by testing the system.
<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>Component</th>
      <th>Failure Mode</th>
      <th>Detection measure</th>
    </tr>
  </thead>
  <tbody>
    <!-- Arduino -->
    <tr>
      <td>FA1</td>
      <td>Arduino</td>
      <td>Data Missing</td>
      <td>Dormant</td>
    </tr>
    <tr>
      <td>FA2</td>
      <td>Arduino</td>
      <td>Data Inaccurate</td>
      <td>Dormant</td>
    </tr>
    <tr>
      <td>FA3</td>
      <td>Arduino</td>
      <td>Data Timeless</td>
      <td>Dormant</td>
    </tr>
    <tr>
      <td>FA4</td>
      <td>Arduino</td>
      <td>Erroneous/Inconsistent Datapoints</td>
      <td>Dormant</td>
    </tr>
    <tr>
      <td>FA5</td>
      <td>Arduino</td>
      <td>Data cannot be transferred</td>
      <td>Dormant</td>
    </tr>
    <!-- Subscription Script -->
    <tr>
      <td>FA6</td>
      <td>Subscription Script</td>
      <td>Data cannot be received (from MQTT-Server)</td>
      <td>Hidden</td>
    </tr>
    <tr>
      <td>FA7</td>
      <td>Subscription Script</td>
      <td>Data cannot be transferred (to the database)</td>
      <td>Hidden</td>
    </tr>
    <!-- Database -->
    <tr>
      <td>FA8</td>
      <td>Database</td>
      <td>Not available (permanent)</td>
      <td>Evident</td>
    </tr>
    <tr>
      <td>FA9</td>
      <td>Database</td>
      <td>Not available (temporary)</td>
      <td>Evident</td>
    </tr>
    <tr>
      <td>FA10</td>
      <td>Database</td>
      <td>Faulty data cleaning</td>
      <td>Evident</td>
    </tr>
    <tr>
      <td>FA11</td>
      <td>Database</td>
      <td>Reading not possible</td>
      <td>Evident</td>
    </tr>
    <tr>
      <td>FA12</td>
      <td>Database</td>
      <td>Writing not possible</td>
      <td>Evident</td>
    </tr>
  </tbody>
</table>

# Corrective Actions  
<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>Priority</th>
      <th>Component</th>
      <th>Failure Mode</th>
      <th>RPN</th>
      <th>Suggested Corrective Action</th>
    </tr>
  </thead>
  <tbody>
    <!-- High Priority -->
    <tr>
      <td>FA7</td>
      <td><strong>High</strong></td>
      <td>Subscription Script</td>
      <td>Data cannot be transferred (to the database)</td>
      <td>216</td>
      <td>Implement retry logic, use a message queue or buffer in case of failure</td>
    </tr>
    <tr>
      <td>FA2</td>
      <td><strong>High</strong></td>
      <td>Arduino</td>
      <td>Data Inaccurate</td>
      <td>210</td>
      <td>Calibrate sensors regularly; add data validation checks</td>
    </tr>
    <tr>
      <td>FA9</td>
      <td><strong>High</strong></td>
      <td>Database</td>
      <td>Not available (temporary)</td>
      <td>210</td>
      <td>Introduce local caching; add reconnect and retry strategies</td>
    </tr>
    <!-- Medium Priority -->
    <tr>
      <td>FA5</td>
      <td><strong>Medium</strong></td>
      <td>Arduino</td>
      <td>Data cannot be transferred</td>
      <td>192</td>
      <td>Add ACK checks; implement timeout and retransmission logic</td>
    </tr>
    <tr>
      <td>FA6</td>
      <td><strong>Medium</strong></td>
      <td>Subscription Script</td>
      <td>Data cannot be received (from MQTT-Server)</td>
      <td>189</td>
      <td>Auto-reconnect on failure; improve server health monitoring</td>
    </tr>
    <tr>
      <td>FA4</td>
      <td><strong>Medium</strong></td>
      <td>Arduino</td>
      <td>Erroneous/Inconsistent Datapoints</td>
      <td>175</td>
      <td>Include timestamp validation, sequence number and anomaly detection logic</td>
    </tr>
    <!-- Monitor -->
    <tr>
      <td>FA10</td>
      <td><strong>Monitor</strong></td>
      <td>Database</td>
      <td>Faulty data cleaning</td>
      <td>120</td>
      <td>Strengthen QA/test coverage; use data integrity checks</td>
    </tr>
    <tr>
      <td>FA12</td>
      <td><strong>Monitor</strong></td>
      <td>Database</td>
      <td>Writing not possible</td>
      <td>108</td>
      <td>Introduce write verification; enable rollback and logging</td>
    </tr>
  </tbody>
</table>

# Summary
This FMEA analyzes the failure modes in a sensor-to-database pipeline involving Arduino hardware, MQTT-based data transmission, and a backend database.

Components analyzed include the Arduino sensor board, subscription script (MQTT), and the central database. The analysis focuses on data integrity, availability, and flow consistency.

The highest RPN (216) was found in the Subscription Script, failing to transfer data to the database.

Arduino inaccuracies and temporary database unavailability also scored critical RPNs of 210.
Detection was often rated poor for transient errors and silent data corruption. 
Each failure mode was rated by Severity (S), Occurrence (O), and Detection (D), each on a scale from 1–10. The Risk Priority Number (RPN) was calculated as RPN = S × O × D. Detection types were classified as Evident, Dormant, or Hidden.

## List actions for top risks
- Improve retry and queuing logic in the Subscription Script.
- Calibrate and validate Arduino sensor input more frequently.
- Implement local caching and robust reconnect logic for database access.

If implemented, these corrective actions are expected to reduce RPN scores by improving detection and reducing occurrence likelihood. This contributes to a more robust and certifiable data pipeline.
