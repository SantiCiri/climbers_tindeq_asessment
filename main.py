from downloader.downloader import DriveDownloader
from unzipper.unzipper import Unzipper
from repeaters_analytics.analytics import Cfd,Calc_from_repeaters,Rfd,Balance
from build_report.reporter import Reporter

if __name__ == '__main__':
    rfd_fig=None
    #descarga los archivos de ese DNI en una carpeta con ese DNI
    downloader = DriveDownloader()
    #Lee el DNI del excel
    dni, fecha1, fecha2, intro,methodology,objective,conclusion=downloader.variable_reader()
    downloader.download_files(dni=dni)
    #descomprime todos los archivos de la carpeta de ese DNI
    
    unzip=Unzipper(dni)
    unzip.unzip_repeaters()
    unzip.move_csvs()

    weight=Balance(fecha1=fecha1,fecha2=fecha2,dni=dni)
    climbers_weight=weight.get_climbers_weight()
    rfd=Rfd(fecha1=fecha1,fecha2=fecha2,dni=dni)
    climbers_rfd=rfd.get_climbers_rfd()
    rfd_fig=rfd.plot_rfd()
    cfd=Cfd(dni=dni,fecha1=fecha1,fecha2=fecha2,climbers_weight=climbers_weight)
    cfd.calc_perc_body_mass()
    cfd.remove_rests()
    climbers_max_strength=cfd.get_max_strength()
    cfd.fit_model()
    climbers_cf=cfd.predict_cfd()
    repeaters=Calc_from_repeaters(dni=dni,fecha1=fecha1, fecha2=fecha2,rfd_fig=rfd_fig)
    repeaters_plot=repeaters.plot_exercises()
    reporter=Reporter(dni, fecha1, fecha2, intro,methodology,objective,conclusion)
    full_name=reporter.read_form()
    reporter.create_html(dni=dni,
                         titulo = f"Informe {full_name} al {fecha2}",
                         secciones = ["Introducción", "Objetivo", "Metodología", "Resultados", "Conclusiones"],
                         objetivo = "El objetivo de este informe es analizar el rendimiento del producto X en el mercado.",
                         resultados = "Los resultados muestran un incremento del 20% en las ventas durante el último trimestre.",
                         conclusiones = "En conclusión, el producto X tiene un desempeño favorable y se espera un crecimiento continuo en el futuro.",
                         graficos = [repeaters_plot.to_html(include_plotlyjs="cdn")])

