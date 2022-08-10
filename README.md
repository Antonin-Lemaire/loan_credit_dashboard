# loan_credit_dashboard
Dashboard hosted on streamlit.
https://antonin-lemaire-loan-credit-dashboard-dashboard-api-pe5dbq.streamlitapp.com/

It allows for visualisation of data loaded locally or on the web app, and request predictions and explanations from the api.

## Organisation

The main file is dashboard_api.py.
It will request some fonctions from common_functions.py.
Kernel.py is not used in production, though if for some reason test.csv and train.csv start failing or disappear it is used to generate them again.

## Local requirements

To use it locally, you will need dashboard_api.py, common_functions.py and either Kernel.py or the .csv files.

If you went with Kernel.py, please ensure you have ~3GB of free space.
Kernel will use 7GB of RAM to run, for about 10 to 15 minutes.
You can delete the "Inputs" folder that appeared once it finished running.

Make sure to run dashboard_api.py in the same folder as the csv files and common_fonctions.py

This version of the dashboard will connect to the api hosted on heroku.
If you wish to use a locally hosted api, replace the variable API_URI by the local address. (default 127.0.0.1/8000/)

## Usage

To install local requirements open a python console and run: 
pip install -r requirements.txt

To run the Kernel and generate the csv files, open terminal in its folder and run:
python3 Kernel.py

To run the local dashboard:
streamlit run dashboard_api.py


