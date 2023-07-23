from __future__ import print_function
import os.path
import io
import os
import pandas as pd
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
logging.basicConfig(level=logging.INFO,filename="logs.log",filemode="a")

class DriveDownloader:
    """Downloads all files containing the keyword "repeaters" in their name from Google Drive"""

    SCOPES = ['https://www.googleapis.com/auth/drive']

    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
    
    @staticmethod
    def variable_reader():
        """Reads the excel file to find out which dates are going to be evaluated, the 
        sportsman's dni and final conclusion"""
        df=pd.read_excel("input.xlsx")
        dni=int(df.loc[df['concepto'] == 'DNI', 'valor'].item())
        dni=f"'{dni}'"
        fecha1=str(df.loc[df['concepto'] == 'fecha1', 'valor'].item())
        fecha2=str(df.loc[df['concepto'] == 'fecha2', 'valor'].item())
        conclusion=str(df.loc[df['concepto'] == 'Conclusion Final', 'valor'].item()).replace("\n", "<br>")
        methodology=str(df.loc[df['concepto'] == 'Metodologia', 'valor'].item()).replace("\n", "<br>")
        objective=str(df.loc[df['concepto'] == 'Objetivo', 'valor'].item()).replace("\n", "<br>")
        intro=str(df.loc[df['concepto'] == 'Introduccion', 'valor'].item()).replace("\n", "<br>")
        return dni, fecha1, fecha2, intro, methodology, objective, conclusion

    @classmethod
    def download_files(cls,dni):
        try:
            creds = cls._get_credentials()
        except:
            flow = InstalledAppFlow.from_client_secrets_file(
            os.path.join(os.getcwd(), "downloader", "credentials.json"), DriveDownloader.SCOPES)
            creds = flow.run_local_server(port=0)
            service = build('drive', 'v3', credentials=creds)
        try:
            # Search for all files containing a specific DNI in their name
            query = f"name contains {dni} and trashed = false"
            results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])

            if not items:
                print('No se encontraron archivos con este DNI y fechas en drive')
                logging.error("No files with this DNI and dates were found on drive")
                return

            logging.info("Descargando archivos")
            for item in items:
                logging.info(u'{0} ({1})'.format(item['name'], item['id']))
                cls._download_file(cls,service=service, file_id=item['id'], file_name=item['name'],dni=dni)
        except HttpError as error:
            logging.warning(f'An error occurred -- Do you have a folder named after the DNI you are searching for?? --:\n {error}')
        try:
            # Downloads the form
            file_id="1-86qfugj7xR5G6iFmMra_U4foagMTTK85U1M9sSHj2M"
            file_name="evaluacion_leo_mirri.csv"
            cls._download_form(cls,service, file_id, file_name)
        except HttpError as error:
            print(f'An error occurred: {error}')
            logging.error(f'An error occurred: {error}')

    def _get_credentials(self):
        """Gets valid user credentials from storage."""
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        return creds

    def _download_file(self, service, file_id, file_name,dni):
        """Downloads a file from Google Drive."""
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
    
        while done is False:
            status, done = downloader.next_chunk()
            logging.info(f'Downloading {file_name}: {int(status.progress() * 100)}.')
        fh.seek(0)
        dni_int=dni.replace("'", "")
        directory = f"{os.getcwd()}/{dni_int}"
        if not os.path.exists(directory):
            os.makedirs(directory)

        file_path = os.path.join(directory, file_name)
        with open(file_path, 'wb') as f:
            f.write(fh.read())

    def _download_form(self, service, file_id, file_name):
        """Downloads a file from Google Drive."""
        request = service.files().export_media(fileId=file_id, mimeType='text/csv')
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False

        while done is False:
            status, done = downloader.next_chunk()
            logging.info(f'Downloading {file_name}: {int(status.progress() * 100)}%')
        
        fh.seek(0)
        directory = os.getcwd()
        file_path = os.path.join(directory, file_name)
        
        with open(file_path, 'wb') as f:
            f.write(fh.read())

        logging.info(f"File '{file_name}' has been downloaded successfully.")
