from downloader.downloader import DriveDownloader
from unzipper.unzipper import Unzipper
from repeaters_analytics.analytics import Cfd,Calc_from_repeaters,Rfd,Balance
from build_report.reporter import Reporter
from dataset_builder.dataset_builder import Dataset_Builder

if __name__ == '__main__':
    rfd_fig=None
    #Lee la información del excel input
    dni, fecha1, fecha2, intro, methodology, objective, conclusion=DriveDownloader.variable_reader()
    #descarga los archivos de ese DNI en una carpeta con ese DNI
    DriveDownloader.download_files(dni=dni)
    #descomprime todos los archivos de la carpeta de ese DNI
    unzip=Unzipper(dni)
    unzip.unzip_repeaters()
    unzip.move_csvs()

    weight=Balance(fecha1=fecha1,fecha2=fecha2,dni=dni)
    climbers_weight=weight.get_climbers_weight()
    rfd=Rfd(fecha1=fecha1,fecha2=fecha2,dni=dni)
    climbers_rfd=rfd.get_climbers_rfd()/climbers_weight
    rfd_fig=rfd.plot_rfd()
    cfd=Cfd(dni=dni,fecha1=fecha1,fecha2=fecha2,climbers_weight=climbers_weight)
    climbers_cfd=cfd.climbers_cfd/climbers_weight
    cfd.calc_perc_body_mass()
    cfd.remove_rests()
    cfd.get_max_strength()
    cfd.fit_model()
    cfd.predict_cfd()
    cfd_plot=cfd.plot()
    repeaters=Calc_from_repeaters(dni=dni,fecha1=fecha1, fecha2=fecha2,rfd_fig=rfd_fig)
    repeaters_plot=repeaters.plot_exercises()
    dataset=Dataset_Builder(dni=dni,climbers_rfd=climbers_rfd,climbers_weight=climbers_weight,climbers_cfd=climbers_cfd)
    dataset.save_evaluation_data()



    """
    df,mail,name,surname,birthdate, height,style,IRCRA_onsight,IRCRA_redpoint,climbers_max_pullup,sex=Reporter().read_form(dni=dni)
    Reporter().create_html(dni=dni,
                         fecha2=fecha2,
                         titulo = f"Informe {name} {surname} al {fecha2.replace('_','/')}",
                         secciones = ["Introducción", "Objetivo", "Metodología", "Resultados", "Conclusiones"],
                         introduccion=intro,
                         objetivo = objective,
                         metodologia=methodology,
                         resultados = "",
                         conclusiones = conclusion,
                         graficos = [repeaters_plot.to_html(include_plotlyjs="cdn").replace("\n",""),
                                     cfd_plot.to_html(include_plotlyjs="cdn").replace("\n","")])
                                     """

