import pandas as pd
import weasyprint
import pdfkit
import webbrowser
import os
import plotly.graph_objs as go
import logging
logging.basicConfig(level=logging.INFO,filename="logs.log",filemode="a")

class Reporter:
    """Builds a report in html powered by plotly"""
    def __init__(self,dni):
        self.ircra_depo = {11:"6a", 12:"6a+", 13:"6b", 14:"6b+", 15:"6c", 16:"6c+", 17:"7a", 18:"7a+", 19:"7b", 20:"7b+", 21:"7c", 
                      22:"7c+", 23:"8a", 24:"8a+", 25:"8b", 26:"8b+", 27:"8c", 28:"8c+", 29:"9a", 30:"9a+", 31:"9b", 32:"9b+"}
        self.ircra_bulder = {17:"V3", 18:"V4", 19:"V5", 20:"V6", 21:"V7", 22:"V7,5", 23:"V8", 24:"V9", 25:"V10", 26:"V11", 
                       27:"V12", 28:"V13", 29:"V13,5", 30:"V14", 31:"V15", 32:"V16"}
        self.dni=int(dni.replace("'", ""))
        df=pd.read_csv("dataset.csv", index_col=0)
        df=df[df["DNI"].isin([self.dni])]
        df=df.sort_values(by=['id_evaluacion']).drop_duplicates(subset=['DNI'],keep="last")
        df["Marca temporal"]=pd.to_datetime(df["Marca temporal"], format="%d/%m/%Y %H:%M:%S")
        self.values= df.to_dict(orient='records')[0]
            
    def create_html(self,fecha2, secciones, introduccion, objetivo,metodologia, graficos):
        logging.info(f"Data in reporting: {self.values}")
        #Remove keys to build the results
        self.resultados=self.values.copy()
        keys_to_remove = ['id_evaluacion','Marca temporal','Dirección de correo electrónico','DNI','Nombre','Apellido','Fecha de Nacimiento',
                          'Altura en cm','Estilo preferido','Sexo','Años Escalando','Mano hábil']
        for key in keys_to_remove: self.resultados.pop(key, None)

        name=self.values["Nombre"]
        surname=self.values["Apellido"]
        sexo=self.values["Sexo"]
        if self.values['Estilo preferido']=="Deportiva":
            redpoint_grade=next((k for k, v in self.ircra_depo.items() if v == self.values['Grado IRCRA ensayado']), None)
        elif self.values['Estilo preferido']=="Boulder":
            redpoint_grade=next((k for k, v in self.ircra_bulder.items() if v == self.values['Grado IRCRA ensayado']), None)

        climbers_cfd=self.values['cfd (% peso)']
        if self.values['Mano hábil']=="Derecha":
            climbers_mvc=self.values[f'flex-dedo-der']
        elif self.values['Mano hábil']=="Izquierda":
            climbers_mvc=self.values[f'flex-dedo-izq']
        title = f"Informe {name} {surname} al {fecha2.replace('_','/')}"

        for plot in graficos:
            if plot.layout.title.text == 'Fuerza crítica como % de peso corporal según grado de escalada':
                plot.add_trace(go.Scatter(x=[redpoint_grade], y=[climbers_cfd], mode='markers', name=f'{name} {surname}'))
            if plot.layout.title.text == f'Fuerza máxima como % de peso corporal según grado de escalada para {sexo}':
                plot.add_trace(go.Scatter(x=[redpoint_grade], y=[climbers_mvc], mode='markers', name=f'{name} {surname}'))

        #Beautifies plots
        str_plot = ''
        for plot in graficos:
            html_plot=plot.to_html(include_plotlyjs="cdn").replace("\n", "")
            str_plot += f'<div style="justify-content: center; margin: auto; width: 100%;">{html_plot}</div>'
        
        #make table Results
        html_table = "<table><tr><th>Indicador</th><th>Valor</th></tr>"
        for key, value in self.resultados.items():
            html_table += f"<tr><td>{key}</td><td>{value}</td></tr>"
        html_table += "</table>"

        # Plantilla HTML
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
        </head>
        <body>
            <h1 style="text-align: center;">{title}</h1>
            <h2>{secciones[0]}</h2>
            <p>{introduccion}</p>
            
            <h2>{secciones[1]}</h2>
            <p>{objetivo}</p>
            
            <h2>{secciones[2]}</h2>
            <p>{metodologia}</p>
            
            <h2>{secciones[3]}</h2>
            <p>{html_table}</p>
            
            <!-- Aquí se insertan los gráficos -->
            <div style="display: flex; flex-wrap: wrap; justify-content: center; margin-top: 0px;">
                {str_plot}
        </body>
        </html>
        """

        # Ruta del archivo HTML y PDF
        if not os.path.exists(os.path.join(str(self.dni), fecha2)):os.makedirs(os.path.join(str(self.dni), fecha2))
        archivo_html = os.path.join(str(self.dni), f"reporte web {fecha2}.html")
        archivo_pdf = os.path.join(str(self.dni), f"reporte movil {fecha2}.pdf")

        # Guardar el contenido HTML en un archivo
        with open(archivo_html, "w", encoding="utf-8") as file:
            file.write(html_template)
        webbrowser.open(archivo_html)

        # Convertir el archivo HTML a PDF usando weasyprint
        weasyprint.HTML(archivo_html).write_pdf(archivo_pdf)

        # Convertir el archivo HTML a PDF usando pdfkit
        #pdfkit.from_file(archivo_html, archivo_pdf)

        logging.info("Report created succesfully")