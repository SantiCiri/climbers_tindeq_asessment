import pandas as pd
from string import Template
import weasyprint
import pdfkit
import plotly.graph_objs as go
import plotly.io as pio
import webbrowser
from selenium import webdriver
from datetime import datetime, timedelta
import os
import logging
logging.basicConfig(level=logging.INFO,filename="logs.log",filemode="a")

class Reporter:
    """Builds a report in html powered by plotly"""
    def __init__(self, dni, fecha1, fecha2, intro,methodology,objective,conclusion):
        self.dni=int(dni.replace("'", ""))
        self.fecha1=fecha1
        self.fecha2=fecha2
        self.intro=intro
        self.methodology=methodology
        self.objective=objective
        self.conclusion=conclusion
    
    def read_form(self):
        df=pd.read_csv("evaluacion_leo_mirri.csv")
        df["Marca temporal"]=pd.to_datetime(df["Marca temporal"], format="%d/%m/%Y %H:%M:%S")
        #start_date = pd.to_datetime(self.fecha1, format="%d_%m_%Y")
        #end_date = pd.to_datetime(self.fecha2, format="%d_%m_%Y")
        #df = df[(df["Marca temporal"] >= start_date) & (df["Marca temporal"] <= end_date)]
        full_name_position=df.index[df["DNI (solo numeros)"]==self.dni].tolist()[0]
        self.full_name = df["Nombre y Apellido"].iloc[full_name_position]
        return self.full_name
    
    @staticmethod
    def create_html(dni,titulo, secciones, introduccion, objetivo,metodologia, resultados, conclusiones, graficos):
        dni=dni.replace("'", "")
        #Beautifies plots
        graficos_str = ''
        for plot in graficos:
            plot = f'<div style="margin: -150px; padding: 5px; width: 100%;">{plot}</div>'
            graficos_str += plot
        # Plantilla HTML
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{titulo}a</title>
        </head>
        <body>
            <h1 style="text-align: center;">{titulo}</h1>
            <h2>{secciones[0]}</h2>
            <p>{introduccion}</p>
            
            <h2>{secciones[1]}</h2>
            <p>{objetivo}</p>
            
            <h2>{secciones[2]}</h2>
            <p>{metodologia}</p>
            
            <h2>{secciones[3]}</h2>
            <p>{resultados}</p>
            
            <h2>{secciones[4]}</h2>
            <p>{conclusiones}</p>
            
            <!-- Aquí se insertan los gráficos -->
            <div style="display: flex; flex-wrap: wrap; justify-content: center; align-items: flex-start; margin-top: 150px;">
            {graficos_str}
            </div>

        </body>
        </html>
        """

        # Ruta del archivo HTML y PDF
        archivo_html = os.path.join(dni, "reporte web.html")
        archivo_pdf = os.path.join(dni, "reporte movil.pdf")

        # Guardar el contenido HTML en un archivo
        with open(archivo_html, "w", encoding="utf-8") as file:
            file.write(html_template)
        webbrowser.open(archivo_html)

        # Convertir el archivo HTML a PDF
        weasyprint.HTML(archivo_html).write_pdf(archivo_pdf)

        # Convertir el archivo HTML a PDF usando pdfkit
        pdfkit.from_file(archivo_html, archivo_pdf)