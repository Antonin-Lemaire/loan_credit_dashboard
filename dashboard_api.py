import streamlit as st
import pandas as pd
import numpy as np
import dill
import json
import requests
from common_functions import ClassifierAPI
import matplotlib.pyplot as plt
import seaborn as sns
from common_functions import ClientInput
from flask import jsonify
import os
import Kernel


def request_prediction(model_uri, client):
    headers = {"Content-Type": "application/json"}

    response = requests.post(
        model_uri + 'predict', data=jsonify(client))
    response = json.loads(response.content.decode('utf-8'))
    return response


# def request_index(model_uri):
#     answer = requests.post(model_uri + 'get_clients')
#     answer = json.loads(answer.content.decode('utf-8'))
#     return answer['list_of_ids']


def get_neighbours(model_uri):
    neighs = requests.get(model_uri + 'get_neighbours')
    neighs = json.loads(neighs.content.decode('utf-8'))
    neighs_data = pd.DataFrame(neighs)
    return neighs_data


def modus_operandi():
    df = None
    if not os.path.exists('test.csv'):
        data_file = st.file_uploader('Please upload test.csv file', type=['csv'])
        if data_file is not None:
            df = pd.read_csv(data_file).reset_index()
    else:
        df = pd.read_csv('test.csv').reset_index()
    print('loading data complete')
    if df is None:
        return
    API_URI = 'http://127.0.0.1:8000/'

    st.title('Loan credit default risk')

    choices = df.index
    client_id = st.selectbox('Select client ID',
                             choices)
    if client_id is not None:
        client = df[df['index'] == client_id]
        st.table(client)
        predict_button = st.checkbox('Predict')
        if predict_button:
            pred = request_prediction(API_URI, client)
            risk = pred['value']
            st.write('This client\'s risk of defaulting on his loan is {:.2f}'.format(risk))
            if risk > 0.55:
                st.write('Loan denied')
            elif risk < 0.35:
                st.write('Loan granted')
            else:
                st.write('This client\'s case requires further expertise')

            explanation = pred['context']
            fig = explanation.as_pyplot_figure()
            st.pyplot(fig)
        comparison = st.checkbox('Compare to neighbouring clients')
        if comparison:
            df_neighbours = get_neighbours(API_URI)
            selection = [v for v in df.columns if 'TARGET' not in v]
            choice = st.selectbox('Select indicator', selection)
            fig = sns.boxplot(x=df_neighbours[choice].groupby(by='TARGET'))
            st.pyplot(fig)
            st.write()


if __name__ == '__main__':

    modus_operandi()
