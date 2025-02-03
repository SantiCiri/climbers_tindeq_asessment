from downloader.downloader import DriveDownloader
from unzipper.unzipper import Unzipper
from repeaters_analytics.analytics import Cfd,Calc_from_repeaters,Rfd,Balance
from build_report.reporter import Reporter
from dataset_builder.dataset_builder import Dataset_Builder
from model_plots.plot import Global_plots

if __name__ == '__main__':
    rfd_fig=None
    #Lee la información del excel input
    dni, fecha, intro, methodology, objective, conclusion=DriveDownloader.variable_reader()
    #descarga los archivos de ese DNI en una carpeta con ese DNI
    DriveDownloader.download_files(dni=dni)
    #descomprime todos los archivos de la carpeta de ese DNI
    unzip=Unzipper(dni)
    unzip.unzip_repeaters()
    unzip.move_csvs()

    weight=Balance(fecha=fecha,dni=dni)

    climbers_weight=weight.get_climbers_weight(fecha=fecha)

    rfd=Rfd(fecha=fecha,dni=dni)
    climbers_rfd=rfd.get_climbers_rfd()*100/climbers_weight
    rfd_fig=rfd.plot_rfd()
    cfd=Cfd(dni=dni,fecha=fecha,climbers_weight=climbers_weight)
    climbers_cfd=cfd.climbers_cfd*100/climbers_weight
    cfd.calc_perc_body_mass()
    cfd.remove_rests()
    cfd.get_max_strength()
    cfd.fit_model()
    cfd.predict_cfd()
    cfd_plot=cfd.plot()
    repeaters=Calc_from_repeaters(dni=dni,fecha=fecha,rfd_fig=rfd_fig)
    repeaters_plot=repeaters.plot_exercises()
    exercise_mvc_dicc=repeaters.indicator_extractor()
    dataset=Dataset_Builder(dni=dni,climbers_rfd=climbers_rfd,climbers_weight=climbers_weight,climbers_cfd=climbers_cfd,
                            exercise_mvc_dicc=exercise_mvc_dicc)
    dataset.save_evaluation_data()

    reporter=Reporter(dni=dni)
    population_plots=Global_plots(style=reporter.values["Estilo preferido"])
    mvc_global_plot=population_plots.mvc_global_plotter(sexo=reporter.values["Sexo"])
    cfd_global_plot=population_plots.cfd_global_plotter()

    reporter.create_html(fecha=fecha,
                         secciones = ["Introducción", "Objetivo", "Metodología", "Resultados", "Conclusiones"],
                         introduccion=intro,
                         objetivo = objective,
                         metodologia=methodology,
                         graficos = [repeaters_plot,cfd_plot,cfd_global_plot,mvc_global_plot])

