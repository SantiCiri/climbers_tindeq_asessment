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

class Balance():
    def __init__(self,fecha1,fecha2,dni):
        path = os.getcwd()
        self.dni=dni.replace("'", "")
        start_date = datetime.strptime(fecha1, "%d_%m_%Y").date()
        end_date = datetime.strptime(fecha2, "%d_%m_%Y").date()
        # Construct a regular expression pattern to match the date range between fecha1 and fecha2
        self.date_range_pattern = r"\b(" + "|".join([(start_date + timedelta(days=i)).strftime("%d_%m_%Y") for i in range((end_date - start_date).days + 1)]) + r")\b"
        # Construct a regular expression pattern to match dates in the format "day_month_year"
        self.date_pattern = r"\b(\d{2}_\d{2}_\d{4})\b"
        # Search for CSV files matching the given dni in the specified path
        for path in glob.glob(os.path.join(path,dni[1:-1], "*","balanza","*.csv")):
            match=re.search(self.date_pattern, path)
            if match:
                date = match.group(1)
                if re.search(self.date_range_pattern, date):
                    # Read the CSV file into a pandas DataFrame, skipping the first 3 rows and using the fourth row as the header
                    self.balance_df = pd.read_csv(path,skiprows=3,header=0)

    def get_climbers_weight(self):
        """
        Retrieves the average weight of climbers from the balance data.
        Returns:
        - climbers_weight (float): The average weight of climbers.
        Extracts a subset of the balance DataFrame, calculates the mean weight, and returns it as the average weight of climber"""
        df2 = self.balance_df.iloc[:int(len(self.balance_df)*0.8)].iloc[int(len(self.balance_df)*0.2):]
        self.climbers_weight = round(df2["weight"].mean(),2)
        logging.info("Peso de escalador calculado")
        return self.climbers_weight

class Rfd():
    def __init__(self,dni,fecha1,fecha2):
        path = os.getcwd()
        self.dni=dni.replace("'", "")
        start_date = datetime.strptime(fecha1, "%d_%m_%Y").date()
        end_date = datetime.strptime(fecha2, "%d_%m_%Y").date()
        # Construct a regular expression pattern to match the date range between fecha1 and fecha2
        self.date_range_pattern = r"\b(" + "|".join([(start_date + timedelta(days=i)).strftime("%d_%m_%Y") for i in range((end_date - start_date).days + 1)]) + r")\b"
        # Construct a regular expression pattern to match dates in the format "day_month_year"
        self.date_pattern = r"\b(\d{2}_\d{2}_\d{4})\b"
        # Search for CSV files matching the given dni in the specified path
        for path in glob.glob(os.path.join(path,dni[1:-1], "*","rfd","*.csv")):
            match=re.search(self.date_pattern, path)
            if match:
                date = match.group(1)
                if re.search(self.date_range_pattern, date):
                    # Read the CSV file into a pandas DataFrame, skipping the first 2 rows and using the third row as the header
                    self.rfd_df = pd.read_csv(path,skiprows=2,header=0)
    def get_climbers_rfd(self):
        """Retrieves the Rfd value of climbers. rfd calculated as the force in kg/s made the first 200ms after making 0,4kg of force.
        Returns:
        - climbers_rfd (float): The Rfd value of climbers."""
        
        # Find the index where the weight is at least 0.4 kg
        start_index = self.rfd_df[self.rfd_df['weight'] >= 0.4].index.min()

        # Filter the DataFrame for the first 0.2 seconds after at least 0.4 kg weight is recorded
        end_time = self.rfd_df.loc[start_index, 'time'] + 0.2
        df = self.rfd_df[(self.rfd_df['time'] >= self.rfd_df.loc[start_index, 'time']) & (self.rfd_df['time'] <= end_time)]

        # Capture min and max weight and corresponding times
        self.min_weight = df['weight'].min()
        self.max_weight = df['weight'].max()
        self.min_time = df.loc[df['weight'].idxmin(), 'time']
        self.max_time = df.loc[df['weight'].idxmax(), 'time']

        # Calculate the differences
        weight_difference = self.max_weight - self.min_weight
        time_difference = self.max_time - self.min_time

        self.climbers_rfd=round(weight_difference/time_difference)
        logging.info("RFD calculado")
        return self.climbers_rfd
    
    def plot_rfd(self):
        # Create the figure
        rfd_fig = go.Figure()
        rfd_fig.add_trace(go.Scatter(x=self.rfd_df['time'], y=self.rfd_df['weight'], mode='lines',name="Fuerza de contacto (RFD)"))
        rfd_fig.add_trace(go.Scatter(x=[self.min_time, self.max_time], y=[self.min_weight,self.max_weight], 
                                    mode='lines', line=dict(color='red'),name="Potencia"))
        rfd_fig.update_layout(title=f'Potencia = {self.climbers_rfd} kg/s',
                              xaxis_title='Tiempo (segundos)', yaxis_title='Fuerza (Kg)')
        return rfd_fig

class Calc_from_repeaters():
    def __init__(self,dni,fecha1,fecha2,rfd_fig=None):
        #get the working path
        self.path = "/".join(os.getcwd().split("/")[:-1])
        self.dni=dni.replace("'", "")
        self.start_date = datetime.strptime(fecha1, "%d_%m_%Y").date()
        self.end_date = datetime.strptime(fecha2, "%d_%m_%Y").date()
        self.rfd_fig=rfd_fig
    
    def _csv_wrapper(self,dni,start_date,end_date):
        date_range_pattern = r"\b(" + "|".join([(start_date + timedelta(days=i)).strftime("%d_%m_%Y") for i in range((end_date - start_date).days + 1)]) + r")\b"
        date_pattern = r"\b(\d{2}_\d{2}_\d{4})\b"
        exercises_path=[]
        path = os.getcwd()
        paths=glob.glob(os.path.join(path,dni, "*","*der","*.csv"))
        paths.extend(glob.glob(os.path.join(path,dni, "*","*izq","*.csv")))
        for i in paths:
            match=re.search(date_pattern, i)
            if match:
                date = match.group(1)
                if re.search(date_range_pattern, date):
                    exercises_path.append(i)
        #Extracts the exercises that have been tested and downloaded
        exercises=[]
        for path in exercises_path:
            exercise=path.split("/")[-2]
            exercises.append(exercise)
        exercises=list(dict.fromkeys(exercises))
        #empty list that will be filled with every repeater exercise
        repeaters_path=[]
        #for each exercise
        for exercise in exercises:

            #keep only the path that correspond to one exercise
            csv_files = [x for x in exercises_path if exercise in x]
            #sort in order to concatenate them in order in the future
            csv_files.sort()
            #Make a df out of the info_data.csv
            info_data=pd.read_csv([x for x in csv_files if "info" in x][0])
            #Extract the pause between sets stored in the info_data df
            pause_btw_sets= info_data['pause btw. sets'].iloc[0]

            # Leer los conjuntos de datos data_set_* y agregar la constante a la columna "time"
            dataframes = []
            for file in csv_files:
                if "data_set" in file:
                    data_set_number=int(file.split("data_set_")[1].split(".csv")[0])
                    df=pd.read_csv(file)
                    #Handles that the header might be on the 4th row
                    if 'time' in df.columns:pass
                    else: df=pd.read_csv(file,skiprows=4,header=0)
                    #If the data set number is not the fist one, it adds the corresponding rest time
                    if data_set_number>1:
                        df["time"]=df["time"]+last_time+pause_btw_sets
                    #Captures the new last_time to continue the loop
                    last_time= df['time'].iloc[-1]
                    dataframes.append(df)

            # Concat all the dfs from one exercise into a single one
            merged_data = pd.concat(dataframes).sort_values(by=['time'])
            #Save the exercise in its folder
            repeater_path = str("/"+"/".join(file.split('/')[1:-1] + ["repeaters.csv"]))
            merged_data.to_csv(repeater_path)
            repeaters_path.append(repeater_path)
        return repeaters_path
    
    def indicator_extractor(self):
        self.repeaters_path=self._csv_wrapper(self.dni,self.start_date,self.end_date)
        exercise_mvc_dicc={}
        #for each exercise that can be evaluated
        for df_path in self.repeaters_path:
            #define the regex pattern to extract the exercise name (without the evaluated side)
            exercise_code_pattern = r'/([^/]+)-(der|izq)/'
            exercise_side_pattern= r'/(?P<desired_string>[^/]+)/[^/]+$'
            #check if there is a match in the df_path (checking if the path and csv exist) and extracting the exercise's name
            match_exercise_code = re.search(exercise_code_pattern, df_path)
            match_exercise_side = re.search(exercise_side_pattern, df_path)
            #if there is an exercise in the list,
            if match_exercise_code:
                #save the exercise's name into variable exercise_code
                #exercise_code = match_exercise_code.group(1).replace("-", "_")
                exercise_side = match_exercise_side.group(1)
                #and build the pandas df
                self.df = pd.read_csv(df_path)
                if "flex-dedo" in exercise_side:
                    #gets the minimum force in the 5sec post maximum. done following Torr 2020 The reliability and validity of a method for the assessment of sport rock climber's isometric finger strength
                    mvc=self.df.loc[(self.df['time'] >= self.df['time'][self.df['weight'].idxmax()]) & (self.df['time'] <= self.df['time'][self.df['weight'].idxmax()] + 5), 'weight'].min()
                else: mvc=self.df['weight'].max()
                # Multiplies by 2 because Torr 2020 used both hands
                exercise_mvc_dicc[exercise_side]=mvc*2
        return exercise_mvc_dicc
    
    def plot_exercises(self):
        self.repeaters_path=self._csv_wrapper(self.dni,self.start_date,self.end_date)
        if self.rfd_fig != None: plots=[self.rfd_fig]
        else: plots=[]
        #for each exercise that can be evaluated
        for df_path in self.repeaters_path:
            #define the regex pattern to extract the exercise name (without the evaluated side)
            exercise_code_pattern = r'/([^/]+)-(der|izq)/'
            exercise_side_pattern= r'/(?P<desired_string>[^/]+)/[^/]+$'
            #check if there is a match in the df_path (checking if the path and csv exist) and extracting the exercise's name
            match_exercise_code = re.search(exercise_code_pattern, df_path)
            match_exercise_side = re.search(exercise_side_pattern, df_path)
            #if there is an exercise in the list,
            if match_exercise_code:
                #save the exercise's name into variable exercise_code
                exercise_code = match_exercise_code.group(1).replace("-", "_")
                exercise_side=match_exercise_side.group(1)
                #and build the pandas df
                self.df = pd.read_csv(df_path)
                if globals().get(exercise_code) not in plots:
                    globals()[exercise_code] = go.Figure()
                    globals()[exercise_side] = go.Scatter(x=self.df['time'], y=self.df['weight'], mode='markers',marker_size=3, name=exercise_side)
                    globals()[exercise_code].add_trace(globals()[exercise_side])
                    globals()[exercise_code].update_layout(title=exercise_code, xaxis_title="Tiempo (seg)",
                                                            yaxis_title="Peso (kg)")
                    plots.append(globals()[exercise_code])
                else:
                    globals()[exercise_side] = go.Scatter(x=self.df['time'], y=self.df['weight'], mode='markers',marker_size=3, name=exercise_side)
                    globals()[exercise_code].add_trace(globals()[exercise_side])
                    globals()[exercise_code].update_layout(title=exercise_code, xaxis_title="Tiempo (seg)",
                                                            yaxis_title="Peso (kg)")
        # get length of lists 'plots'
        num_plots = len(plots)
        # Create the subplots with the desired grid arrangement
        cols = 2
        rows=int(num_plots/cols)
        #rounds up if rows is a float
        #if isinstance(rows, int)==False:rows=int(rows)+1
        fig = sp.make_subplots(rows=rows, cols=cols)
        # Add the plots to the subplots
        for i,plot in enumerate(plots,start=1):
            # Get the plot's layout
            layout = plot['layout']
            row = (i-1) // cols + 1
            col = (i-1) % cols + 1
            title_text = layout.title.text if layout.title else ''
            # Update the subplot figure's layout with the plot's layout
            fig.add_trace(plot.data[0], row=row, col=col)
            try:
                fig.add_trace(plot.data[1], row=row, col=col)
            except:
                logging.error(f"Missing values for one side of {title_text}]")
                print(f"faltan los datos de un lado de {title_text}")
            # Find the maximum value in the trace data
            data = plot['data']
            max_y_value = max(np.max(trace.y) for trace in data if 'y' in trace)
            max_x_value = max(np.max(trace.x) for trace in data if 'x' in trace)
            # Update the legend position to the top
            fig.update_layout(legend=dict(orientation='h', yanchor='top', y=1.1,font=dict(size=16)))
            # Make plots taller
            height=row*450
            fig.update_layout(height=height)

            # Add title annotation to the subplot
            fig.add_annotation(
                text=title_text,
                xref="paper", yref="paper",
                x=max_x_value*0.2, y=max_y_value*0.85,
                xanchor='left', yanchor='bottom',
                font=dict(size=16),
                showarrow=False,
                row=row, col=col
            )
        return fig

class Cfd():
    def __init__(self,fecha1,fecha2,dni,climbers_weight):
        path = os.getcwd()
        self.climbers_weight=climbers_weight
        start_date = datetime.strptime(fecha1, "%d_%m_%Y").date()
        end_date = datetime.strptime(fecha2, "%d_%m_%Y").date()
        self.date_range_pattern = r"\b(" + "|".join([(start_date + timedelta(days=i)).strftime("%d_%m_%Y") for i in range((end_date - start_date).days + 1)]) + r")\b"
        self.date_pattern = r"\b(\d{2}_\d{2}_\d{4})\b"
        for path in glob.glob(os.path.join(path,dni[1:-1], "*","cfd","data_set_1.csv")):
            match=re.search(self.date_pattern, path)
            if match:
                date = match.group(1)
                if re.search(self.date_range_pattern, date):
                    self.cfd_df = pd.read_csv(path,skiprows=3)
                    self.climbers_cfd=pd.read_csv(path).loc[0, "critical force"]

    def get_climbers_weight(self):
        df2 = self.balance_df.iloc[:int(len(self.balance_df)*0.8)].iloc[int(len(self.balance_df)*0.2):]
        self.climbers_weight = df2["weight"].mean()

    def calc_perc_body_mass(self):
        self.cfd_df["perc_body_mass"]=self.cfd_df["weight"]/self.climbers_weight

    def remove_rests(self):
        comienzos = list(range(6, int(len(self.cfd_df)), 10))
        finales = list(range(11, int(len(self.cfd_df)), 10))
        intervalos=[(0,1)]
        for comienzo,final in zip(comienzos,finales):
            intervalo = (comienzo, final)
            intervalos.append(intervalo)
        self.weighted_df=self.cfd_df
        for intervalo in intervalos:
            self.weighted_df=self.weighted_df.drop(self.weighted_df.index[(self.weighted_df['time']>= intervalo[0]) & (self.weighted_df['time'] <= intervalo[1])])

    def get_max_strength(self):
        first_seconds = self.cfd_df[((self.cfd_df["time"] > 2) & (self.cfd_df["time"] < 5))]
        self.max_strength = first_seconds["perc_body_mass"].mean()

    def fit_model(self):
        X = self.weighted_df[["time"]]
        y = self.weighted_df["perc_body_mass"]
        self.poly = PolynomialFeatures(degree=2)
        X_poly = self.poly.fit_transform(X)
        self.model = LinearRegression()
        self.model.fit(X_poly, y)

    def predict_cfd(self):
        X = self.cfd_df[["time"]]
        X_poly = self.poly.fit_transform(X)
        self.y_pred = self.model.predict(X_poly)
        self.critical_force=min(self.y_pred)

    def plot(self):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self.cfd_df['time'], y=self.cfd_df['perc_body_mass'], mode='lines',name="Fuerza Instantánea"))
        max_time = self.cfd_df['time'].max()
        for i in range(0, int(max_time)+1, 10):
            fig.add_trace(go.Scatter(x=[i, i], y=[0, self.cfd_df['perc_body_mass'].max()], mode='lines', line=dict(dash='dash'),showlegend=False))

        for i in range(7, int(max_time)+1, 10):
            fig.add_trace(go.Scatter(x=[i, i], y=[0, self.cfd_df['perc_body_mass'].max()], mode='lines', line=dict(dash='dash'),showlegend=False))

        fig.add_trace(px.line(x=self.cfd_df["time"], y=self.y_pred).data[0])
        fig.add_trace(go.Scatter(x=[0, 7], y=[self.max_strength,self.max_strength], mode='lines', line=dict(color='red'),name="Fuerza Maxima"))
        fig.update_layout(title=f'Desarrollo de fuerza critica. A la izquierda la fuerza maxima y a la derecha la fuerza petado <br> Fuerza Maxima = {int(self.max_strength*100)}% Fuerza Crítica = {int(self.climbers_cfd*100/self.climbers_weight)}%',
                           xaxis_title='Tiempo (segundos)', yaxis_title='Fuerza (% de masa corporal)',legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1, font=dict(size=16)))
        return fig