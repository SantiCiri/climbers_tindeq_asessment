from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import plotly.graph_objs as go
import plotly.subplots as sp
import plotly.express as px
import pandas as pd
import numpy as np
import os
import re
import glob
from datetime import datetime, timedelta
import logging
logging.basicConfig(level=logging.INFO,filename="logs.log",filemode="a")

class Dataset_Builder():
    def __init__(self,dni,climbers_weight,climbers_cfd=None,climbers_rfd=None,climbers_max_strength=None):
        self.dni=int(dni.replace("'", ""))
        df=pd.read_csv("evaluacion_escalada.csv")
        df["Marca temporal"]=pd.to_datetime(df["Marca temporal"], format="%d/%m/%Y %H:%M:%S")
        df=df[df["DNI"].isin([self.dni])]
        self.values= df.to_dict(orient='records')[0]
        self.climbers_max_strength=climbers_max_strength
        self.climbers_rfd=climbers_rfd
        self.climbers_weight=climbers_weight
        self.climbers_cfd=climbers_cfd

    def save_evaluation_data(self):
        #Reads the .csv with climber's data and adds a new row with the new data
        #Returns:
        #Updated .csv
        
        #Creates a .csv if it does not exist yet
        if not os.path.isfile("dataset.csv"):
            df = pd.DataFrame()
            df.to_csv("dataset.csv")
        
        #Read de dataset.csv
        df=pd.read_csv("dataset.csv")

        #If df is empty, then evaluation id = 1, else, make it auto incremental
        if df.empty: id_evaluacion=1
        else: id_evaluacion = df['id_evaluacion'].max() + 1

        #Takes the dictionary with the values of the new analysis and adds the variables taken from tindeq
        self.values={**self.values,**{'id_evaluacion':id_evaluacion,'fuerza máxima (% peso)':self.climbers_max_strength,'rfd (% peso/s)':self.climbers_rfd,
                            'peso (kg)':self.climbers_weight,'cfd (% peso)':self.climbers_cfd}}
        #Corrects the pull up column to measure it in Body Weight %
        self.values['Dominada maxima (% peso corporal)'] = self.values.pop('Dominada maxima (kg incluyendo peso corporal)', None)
        self.values['Dominada maxima (% peso corporal)'] /= self.climbers_weight
        # Joins the new data with the previous
        df = pd.concat([df,pd.DataFrame(self.values, index=[0])])
        # Reposition the column id_evaluacion to the first position
        df.insert(0, 'id_evaluacion', df.pop('id_evaluacion'))
        # Drop the columns that contain Unnamed
        df = df.drop(columns=[col for col in df.columns if "Unnamed" in col])
        # Save the updated df
        df.to_csv("dataset.csv")




