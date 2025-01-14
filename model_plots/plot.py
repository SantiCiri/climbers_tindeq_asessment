import plotly.graph_objs as go
import logging

class Global_plots:
    """Plots all plots to compare athelte vs population"""

    def __init__(self,style):
        self.ircra_depo = {11:"6a", 12:"6a+", 13:"6b", 14:"6b+", 15:"6c", 16:"6c+", 17:"7a", 18:"7a+", 19:"7b", 20:"7b+", 21:"7c", 
                      22:"7c+", 23:"8a", 24:"8a+", 25:"8b", 26:"8b+", 27:"8c", 28:"8c+", 29:"9a", 30:"9a+", 31:"9b", 32:"9b+"}
        self.ircra_bulder = {17:"V3", 18:"V4", 19:"V5", 20:"V6", 21:"V7", 22:"V7,5", 23:"V8", 24:"V9", 25:"V10", 26:"V11", 
                       27:"V12", 28:"V13", 29:"V13,5", 30:"V14", 31:"V15", 32:"V16"}
        if style=="Boulder":
            self.tickvals=list(self.ircra_bulder.keys())
            self.ticktext=list(self.ircra_bulder.values())
        else:
            self.tickvals=list(self.ircra_depo.keys())
            self.ticktext=list(self.ircra_depo.values())
        
    def mvc_global_plotter(self,sexo):
        #Valores de x a plotear
        x_values = list(range(17, 33))
        if sexo=="Masculino":
            #El modelo
            median = [(5.25 *x + 33.5 ) for x in x_values]
            sup_limit=[5.35 *x + 69.9 for x in x_values]
            inf_limit= [5.05 *x + 0.561 for x in x_values]
        elif sexo=="Femenino":
            #El modelo
            median = [5.6934 *x + 16.63 for x in x_values]
            sup_limit=[ 5.561*x + 28.17 for x in x_values]
            inf_limit= [5.82653*x + 5.09 for x in x_values]

        # Define the trace for the scatter plot
        trace_median = go.Scatter(x=x_values,y=median,mode='lines',name='Mediana')
        trace_sup_limit = go.Scatter(x=x_values,y=sup_limit, mode='lines',name='Percentil 95' )
        trace_inf_limit = go.Scatter(x=x_values,y=inf_limit, mode='lines',name='Percentil 5' )
        # Define the scatter plot layout
        layout = go.Layout(
            title=f'Fuerza máxima como % de peso corporal según grado de escalada para {sexo}',
            xaxis=dict(title='grado de escalada',
                    tickmode='array',
                    tickvals=self.tickvals,
                    ticktext=self.ticktext),
            yaxis=dict(title='Fuerza máxima como % de peso'))

        # Create the scatter plot figure
        fig = go.Figure(data=[trace_median,trace_inf_limit,trace_sup_limit], layout=layout)
        fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,font=dict(size=16),xanchor="right",x=1))
        logging.info("MVC population plot has been created")
        # return the scatter plot
        return fig
    
    def cfd_global_plotter(self):
        #Valores de x a plotear
        x_values = list(range(11, 33))
        #El modelo
        y_values = [(1.9375*x - 1.75 ) for x in x_values]

        # Define the trace for the scatter plot
        trace = go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines',
            name='Valores modelo de fuerza máxima'
        )
        # Define the scatter plot layout
        layout = go.Layout(
            title='Fuerza crítica como % de peso corporal según grado de escalada',
            xaxis=dict(title='grado de escalada',
                       tickmode='array',
                       tickvals=self.tickvals,
                       ticktext=self.ticktext),
            yaxis=dict(title='fuerza petado como % de peso corporal'))
        # Create the scatter plot figure
        fig = go.Figure(data=[trace], layout=layout)
        fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,font=dict(size=16)))
        logging.info("CFD population plot has been created")
        # Display the scatter plot
        return fig
