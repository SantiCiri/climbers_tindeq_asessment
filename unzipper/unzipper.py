import os
import zipfile
import shutil
import re
import logging
logging.basicConfig(level=logging.INFO,filename="logs.log",filemode="a")

class Unzipper:
    """unzips all .zips that have just been downloaded"""
    def __init__(self, dni):
        dni_int=dni.replace("'", "")
        self.dir_path = f"{os.getcwd()}/{dni_int}"
    
    def unzip_repeaters(self):
        for file_name in (f for f in os.listdir(self.dir_path) if f.endswith('.zip') and not f.startswith('.')):
            match = re.search(r"(\d{1,2}_\d{1,2}_\d{4})", file_name)
            if match:
                 fecha = match.group(1)
            else: 
                 print("No se encontró la fecha")
                 logging.error("Could not find the date")                 
            date, month, year = fecha.split("_")
            date = f"{date.zfill(2)}_{month.zfill(2)}_{year}"
            exercise=re.search(r"&(.*)\.zip", file_name).group(1)
            full_file_dir = os.path.join(self.dir_path,date,exercise)
            if not os.path.exists(full_file_dir):
                os.makedirs(full_file_dir)
            with zipfile.ZipFile(self.dir_path+"/"+file_name, 'r') as zip_ref:
                zip_ref.extractall(full_file_dir)
            os.remove(self.dir_path+"/"+file_name)

    def move_csvs(self):
        #For rfd and balanz
        if not any("rfd" in path for path in os.listdir(self.dir_path)):
            logging.error("No RFD")
        if not any("balanza" in path for path in os.listdir(self.dir_path)):
            logging.error("No Balance")
            print("NO HAY BALANZA --- NO HAY BALANZA --- NO HAY BALANZA")
        if not any("cf_test" in path for path in os.listdir(self.dir_path)):
            logging.error("No CFD")
            print("NO HAY CFD --- NO HAY CFD --- NO HAY CFD")
        for file_name in (f for f in os.listdir(self.dir_path) if not f.startswith('.')):
            if "rfd" in file_name:
                date=file_name[18:28]
                exercise="rfd"
                full_file_dir = os.path.join(self.dir_path,date,exercise)
                if not os.path.exists(full_file_dir):
                    os.makedirs(full_file_dir)
                shutil.move(os.path.join(self.dir_path,file_name),os.path.join(full_file_dir,file_name))
                logging.info("Found and placed correctly RFD")
            if "balanza" in file_name:
                    date=file_name[32:42]
                    exercise="balanza"
                    full_file_dir = os.path.join(self.dir_path,date,exercise)
                    if not os.path.exists(full_file_dir):
                        os.makedirs(full_file_dir)
                    shutil.move(os.path.join(self.dir_path,file_name),os.path.join(full_file_dir,file_name))
                    logging.info("Found and placed correctly Balance")
            if "cf_test" in file_name:
                    date=file_name[-23:-13]
                    exercise="cf"
                    full_file_dir = os.path.join(self.dir_path,date,"cfd")
                    if not os.path.exists(full_file_dir):
                        os.makedirs(full_file_dir)
                    shutil.move(os.path.join(self.dir_path,file_name),os.path.join(full_file_dir,"data_set_1.csv"))
                    logging.info("Found and placed correctly CFD")