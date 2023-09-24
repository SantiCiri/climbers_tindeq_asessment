import pandas as pd
import weasyprint
import pdfkit
import webbrowser
import os
import logging
logging.basicConfig(level=logging.INFO,filename="logs.log",filemode="a")

class Reporter:
    """Builds a report in html powered by plotly"""
    def __init__(self):
        pass

    @staticmethod
    def read_dataset(dni):
        dni=int(dni.replace("'", ""))
        df=pd.read_csv("dataset.csv")
        df["Marca temporal"]=pd.to_datetime(df["Marca temporal"], format="%d/%m/%Y %H:%M:%S")
        df=df[df["DNI"].isin([dni])]
        df = df.drop_duplicates(subset=['DNI'], keep='last')
        mail= df.at[0, "Dirección de correo electrónico"]
        name= df.at[0, "Nombre"]
        surname= df.at[0, "Apellido"]
        birthdate=df.at[0, "Fecha de Nacimiento"]
        height= df.at[0, "Altura en cm"]
        style= df.at[0, "Estilo preferido"]
        IRCRA_onsight= df.at[0, "Grado IRCRA a vista"]
        IRCRA_redpoint= df.at[0, "Grado IRCRA ensayado"]
        climbers_max_pullup= df.at[0, "Dominada maxima (kg incluyendo peso corporal)"]
        sex=df.at[0, "Sexo"]
        return df,mail,name,surname,birthdate, height,style,IRCRA_onsight,IRCRA_redpoint,climbers_max_pullup,sex

    @staticmethod
    #Actualizar esta funcion para que saque los resultados del dataset.csv
    def create_html(dni,fecha2,titulo, secciones, introduccion, objetivo,metodologia, resultados, conclusiones, graficos):
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
        if not os.path.exists(os.path.join(dni, fecha2)):os.makedirs(os.path.join(dni, fecha2))
        archivo_html = os.path.join(dni,fecha2, "reporte web.html")
        archivo_pdf = os.path.join(dni,fecha2, "reporte movil.pdf")

        # Guardar el contenido HTML en un archivo
        with open(archivo_html, "w", encoding="utf-8") as file:
            file.write(html_template)
        webbrowser.open(archivo_html)

        # Convertir el archivo HTML a PDF usando weasyprint
        weasyprint.HTML(archivo_html).write_pdf(archivo_pdf)

        # Convertir el archivo HTML a PDF usando pdfkit
        #pdfkit.from_file(archivo_html, archivo_pdf)

        logging.info("Report created succesfully")