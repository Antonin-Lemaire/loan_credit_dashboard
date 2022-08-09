import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import json
import requests
import seaborn as sns
import os


def request_prediction(model_uri, client):
    response = requests.post(model_uri + 'predict',
                             data=client.to_json())
    print(client.to_json())
    response = json.loads(response.content.decode('utf-8'))
    return response


def request_context(model_uri, client):
    answer = requests.post(model_uri + 'context',
                           data=client.to_json())
    answer = answer.content
    return answer


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
    API_URI = 'https://loan-credit-default-risk-api.herokuapp.com/'

    st.title('Loan credit default risk')

    choices = df.index
    client_id = st.selectbox('Select client ID',
                             choices)
    feats = ['DAYS_BIRTH', 'DAYS_EMPLOYED', 'REGION_RATING_CLIENT',
             'REGION_RATING_CLIENT_W_CITY', 'EXT_SOURCE_1', 'EXT_SOURCE_2',
             'EXT_SOURCE_3', 'NAME_INCOME_TYPE_Working',
             'NAME_EDUCATION_TYPE_Higher education', 'BURO_DAYS_CREDIT_MIN',
             'BURO_DAYS_CREDIT_MEAN', 'BURO_DAYS_CREDIT_UPDATE_MEAN',
             'BURO_CREDIT_ACTIVE_Active_MEAN', 'BURO_CREDIT_ACTIVE_Closed_MEAN',
             'PREV_NAME_CONTRACT_STATUS_Approved_MEAN',
             'PREV_NAME_CONTRACT_STATUS_Refused_MEAN',
             'PREV_CODE_REJECT_REASON_XAP_MEAN', 'PREV_NAME_PRODUCT_TYPE_walk-in_MEAN',
             'CC_CNT_DRAWINGS_ATM_CURRENT_MEAN', 'CC_CNT_DRAWINGS_CURRENT_MAX']
    if client_id is not None:
        client = df.iloc[client_id, :]
        client = client[feats]
        st.table(client)
        predict_button = st.checkbox('Predict')
        if predict_button:
            pred = request_prediction(API_URI, client)
            pred = pred.split(',')
            risk = float(pred[1][:-2])
            st.write('This client\'s risk of defaulting on his loan is {:.2f}'.format(risk))
            if risk > 0.55:
                st.write('Loan denied')
            elif risk < 0.35:
                st.write('Loan granted')
            else:
                st.write('This client\'s case requires further expertise')
            context_button = st.checkbox('Context')
            if context_button:
                explanation = request_context(API_URI, client)

                st.image(explanation)
        comparison = st.checkbox('Compare to other clients')
        if comparison:
            choice = st.selectbox('Select indicator', feats)
            fig, ax = plt.subplots()
            ax.boxplot(x=df[choice])
            ax.scatter([1], df.loc[client_id, choice], marker='x', s=400, color='r')
            st.pyplot(fig)
            st.write()


if __name__ == '__main__':
    modus_operandi()
