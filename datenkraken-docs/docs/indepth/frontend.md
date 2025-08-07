# Frontend Documentation

This Document describes how the frontend works and what role every necessary file plays. It will also be explained how to start it. 

## General Information 
The Frontend is coded using a variety of Librarys like for example Streamlit. Instead of installing every Dependency individually, the user can run the command 'uv sync' (if uv is installed). After that the command 'uv run streamlit run app.py' starts the frontend (Only if ran from inside the frontend folder). If everything was done correctly, a new browser window will automatically pop up, showing the content.

## app.py 
App.py represents the main/landing page. It functions as a generel and quick overview over the rooms which are being meassured. It shows the current value ov every meassured parameter and the current status of the room which is defined by the 'worst' current value. That means that if one Parameter is in the critical range, the room status is displayed as critical. 

## pages
The folder 'pages' withholds the detailed views of the corresponding rooms. Streamlit automatically creates a sidebar with a navigation to switch between the files inside pages. The Content which the views show is defined in an external file called functions.py. That way adding rooms is kept simple. 

## functions.py/status_engine.py 
Most of the logic and functions needed for the frontend is defined in these two files. Considering their similar purpose these two files can be combined into one file. However the functions are seperated into two files, since they are used in two different places, serving two different tasks. 'status_engine.py' helps evaluating the collected Data and returns the respective status of each parameter as well as recommendations based on the results. 'functions.py' uses the logic in 'status_engine.py' and defines its own logic to create the functions needed for the frontend. 
