import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import json
import requests
import seaborn as sns
import os
import numpy as np


def request_prediction(model_uri, client):
    """

    Parameters
    ----------
    model_uri : string
    The address where the api is hosted
    client : pd.DataFrame
    One line of a pandas dataframe [1:20]

    Returns
    -------
    response : for some reason, it's a string.
    The server answer as probability [x, y], where y is the one we're after.
    """

    response = requests.post(model_uri + 'predict',
                             data=client.to_json())
    response = json.loads(response.content.decode('utf-8'))
    return response


def request_map(model_uri, client):
    """

    Parameters
    ----------
    model_uri : str
    The address where the api is hosted
    client : pd.DataFrame
    One line of a pandas dataframe [1:20]

    Returns
    -------
    response : dict
    A map of each feature weight in the previous prediction from the api
    """
    answer = requests.post(model_uri + 'context_map',
                           data=client.to_json())
    response = json.loads(answer.content.decode('utf-8'))
    response = json.loads(response)
    return response


def modus_operandi():
    # Starts by checking the required files exist, otherwise asks for an upload
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

    # first display, filter for indicators, client selection
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
        feats_to_display = st.multiselect('Select indicators to display:', feats)
        if len(feats_to_display) > 0:
            st.table(client[feats_to_display])

        # Next up is the prediction part, doing an api request and interpreting it
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

            # Context is doing an api request for the Lime explainer, and interpreting it
            context_button = st.checkbox('Context')
            if context_button:
                explanation = request_map(API_URI, client)
                explanation_list = explanation['1']
                explanation_array = [explanation_list[x] for x in range(0, len(explanation_list))]
                features = [feats[explanation_array[y][0]] for y in range(0, len(explanation_array))]
                weights = [explanation_array[y][1] for y in range(0, len(explanation_array))]
                explanation_df = pd.DataFrame(data={'variable': features,
                                                    'weight': weights})
                pos_df = explanation_df[explanation_df['weight'] < 0].sort_values(by='weight', ascending=True)
                neg_df = explanation_df[explanation_df['weight'] > 0].sort_values(by='weight', ascending=False)
                st.write('Please note that variables at the bottom have little to no impact for this client')
                st.write('Variables to work on, from most harmful to least harmful')
                st.table(neg_df['variable'])
                st.write('Variables in favor of the client, from least beneficial to most beneficial')
                st.table(pos_df['variable'])

        # Comparison will check that the comparison file is there,
        # then display boxplots of each indicator with a reference to the selected client.
        comparison = st.checkbox('Compare to other clients')
        if comparison:
            df_comp = None
            if not os.path.exists('train.csv'):
                data_file_train = st.file_uploader('Please upload train.csv file', type=['csv'])
                if data_file_train is not None:
                    df_comp = pd.read_csv(data_file_train).reset_index()
            else:
                df_comp = pd.read_csv('train.csv').reset_index()
            print('loading data complete')
            if df is None:
                return
            choice = st.multiselect('Select indicators', feats)
            if len(choice) != 0:
                st.write('0 is the group that repaid its loan, 1 is the group that defaulted')
                st.write('The red line represents the selected client')
                st.write('the client is considered most similar to the group with the closest median mark (green)')
                for v in choice:
                    if 'DAYS' in v:
                        df_comp[v] = df_comp[v].abs()
                    fig, ax = plt.subplots()
                    df_comp.boxplot(column=[v], by='TARGET', ax=ax)
                    ax.axhline(df.loc[client_id, v], color='r')

                    st.pyplot(fig)
                    st.write(v)



if __name__ == '__main__':
    modus_operandi()
