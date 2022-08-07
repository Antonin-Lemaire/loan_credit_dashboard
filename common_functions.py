from pydantic import BaseModel
import numpy as np
import pandas as pd


class ClientInput(BaseModel):
    id: int


class Prediction(BaseModel):
    pred: float


class ClassifierAPI:
    def __init__(self, model, explainer):
        self.model = model
        self.explainer = explainer

    def predict(self, data):
        output = self.model.predict_proba(data)
        return output

    def explain(self, data: pd.DataFrame):
        context = self.explainer.explain_instance(data.values.T[0], self.model.predict, num_features=len(data.columns))
        return context


class Instance:
    def __init__(self, id, df):
        self.feats = ['DAYS_BIRTH', 'DAYS_EMPLOYED', 'REGION_RATING_CLIENT', 'REGION_RATING_CLIENT_W_CITY',
                      'EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3', 'NAME_INCOME_TYPE_Working',
                      'NAME_EDUCATION_TYPE_Higher education', 'BURO_DAYS_CREDIT_MIN', 'BURO_DAYS_CREDIT_MEAN',
                      'BURO_DAYS_CREDIT_UPDATE_MEAN', 'BURO_CREDIT_ACTIVE_Active_MEAN',
                      'BURO_CREDIT_ACTIVE_Closed_MEAN', 'PREV_NAME_CONTRACT_STATUS_Approved_MEAN',
                      'PREV_NAME_CONTRACT_STATUS_Refused_MEAN', 'PREV_CODE_REJECT_REASON_XAP_MEAN',
                      'PREV_NAME_PRODUCT_TYPE_walk-in_MEAN', 'CC_CNT_DRAWINGS_ATM_CURRENT_MEAN',
                      'CC_CNT_DRAWINGS_CURRENT_MAX']
        self.id = id
        self.columns = [f for f in df.columns if f not in ['TARGET', 'SK_ID_CURR',
                                                           'SK_ID_BUREAU', 'SK_ID_PREV', 'index']]
        self.values = df.loc[id, self.feats]
