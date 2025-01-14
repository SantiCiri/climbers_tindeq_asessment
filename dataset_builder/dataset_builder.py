from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import plotly.graph_objs as go
import plotly.subplots as sp
import plotly.express as px
import pandas as pd
import math
import numpy as np
import os
import re
import glob
from datetime import datetime, timedelta
import logging
logging.basicConfig(level=logging.INFO,filename="logs.log",filemode="a")

class Dataset_Builder():
    def __init__(self,dni,climbers_weight,climbers_cfd=None,climbers_rfd=None,exercise_mvc_dicc=None):
        self.dni=int(dni.replace("'", ""))
        df=pd.read_csv("evaluacion_escalada.csv")
        df=df[df["DNI"].isin([self.dni])]
        df=df.sort_values(by=['Marca temporal']).drop_duplicates(subset=['DNI'],keep="last")
        self.values= df.to_dict(orient='records')[0]
        self.climbers_rfd=climbers_rfd
        self.climbers_weight=climbers_weight
        self.climbers_cfd=climbers_cfd
        self.exercise_mvc_dicc=exercise_mvc_dicc

    def save_evaluation_data(self):
        #Reads the .csv with climber's data and adds a new row with the new data
        #Returns:
        #Updated .csv
        
        def round_3sf(number):
            if number == 0:
                return 0.0
            else:
                return round(number, 3 - int(math.floor(math.log10(abs(number)))) - 1)

        #Creates a .csv if it does not exist yet
        if not os.path.isfile("dataset.csv"):
            df = pd.DataFrame()
            df.to_csv("dataset.csv")
        
        #Read de dataset.csv
        df=pd.read_csv("dataset.csv",index_col=0)

        #If df is empty, then evaluation id = 1, else, make it auto incremental
        if df.empty: id_evaluacion=1
        else: id_evaluacion = df['id_evaluacion'].max() + 1

        #Corrects the pull up column to measure it in Body Weight %
        self.values['Dominada maxima (% peso corporal)'] = self.values.pop('Dominada maxima (kg que puede sumar)', None)
        self.values['Dominada maxima (% peso corporal)']=self.values['Dominada maxima (% peso corporal)'].replace(',', '.')
        self.values['Dominada maxima (% peso corporal)'] = round_3sf((float(self.values['Dominada maxima (% peso corporal)']) + self.climbers_weight)/self.climbers_weight)*100

        #Divides every value in mvc_dicc by the climber's weight
        for key in self.exercise_mvc_dicc:
            self.exercise_mvc_dicc[key] = round_3sf(self.exercise_mvc_dicc[key]*100/ self.climbers_weight)
        
        self.climbers_rfd=round_3sf(self.climbers_rfd)
        self.climbers_cfd=round_3sf(self.climbers_cfd)

        #Takes the dictionary with the values of the new analysis and adds the variables taken from tindeq
        self.values={**self.values,**self.exercise_mvc_dicc,**{'id_evaluacion':id_evaluacion,'rfd (% peso/s)':self.climbers_rfd,
                            'peso (kg)':self.climbers_weight,'cfd (% peso)':self.climbers_cfd}}

        # Joins the new data with the previous
        df = pd.concat([df,pd.DataFrame([self.values])])
        # Reposition the column id_evaluacion to the first position
        df.insert(0, 'id_evaluacion', df.pop('id_evaluacion'))
        # Save the updated df
        df.to_csv("dataset.csv")
        logging.info("Data saved to dataset.csv succesfully")

            
