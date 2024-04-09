import argparse
import configparser
import src.info_titul
from src.utils import creacion_tablas,universidades
import os.path as path
import logging
import urllib3
import sys
import pathlib
from bs4 import BeautifulSoup
import requests
import pandas as pd
import pyarrow
import fastparquet
from tabula import read_pdf
#import openpyxl
import urllib3
import pyarrow.parquet as pq
import pyarrow as pa
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def main():

     #Read input arguments
     parser = argparse.ArgumentParser(
        description="ReadingPipe")
     parser.add_argument("--destination_path", type=str, default=None,
                         required=True, help="Path to save the data parquet")
     parser.add_argument('--basico', default=False,
                         action='store_true',help="Download basic information about universities degrees.")
     parser.add_argument("--data", default=False,
                         action='store_true',help="Download the start date of university degrees.")
     parser.add_argument("--competences", type=str, default=None,
                         required=False,
                         help="Table of competencies that you want  to read,op: T (trasnverse), G (General), E (Specific)")
     parser.add_argument("--module",default=False,
                         action='store_true', help="Download a table of subjects for each university degree.")
     parser.add_argument("--method", default=False,
                         action='store_true',help="Download a table of methods used in each university degree")
     parser.add_argument("--system", default=False,
                         action='store_true' ,help="Download a table of the information systems used in each university degree")
     parser.add_argument("--pdf", default=False,
                         action='store_true',
                         help="Download the PDF of each study plan")
     parser.add_argument("--university", type=str, default="All",
                         required=False, help="Number of the university that is read(only one). By default all")

     args = parser.parse_args()
     configuracion = configparser.ConfigParser()
     configuracion.read('inconfig.cfg')
     ubicacion = ".\\pdf_output"

     #Create logger object
     logging.basicConfig(filename='logfile.log', level=logging.INFO)
     logger = logging.getLogger('ReadingPipeline')

     #Initialization

     destination_path = pathlib.Path(args.destination_path)
     list_compt=[]
     if args.competences != None:
         if len(args.competences)>3:
             logger.error(
                 f"-- {args.competences} exceed size ")
             sys.exit()
         elif len(args.competences)==3:
             if 'T' and 'G' and 'E' in args.competences:
                 list_compt = args.competences
             else:
                 logger.error(
                     f"-- {args.competences} are not recognized ")
                 sys.exit()
         else:
             for i in args.competences:
                 if i !='T' and i!='G' and i!='E':
                     logger.error(
                         f"-- {args.competences} are not recognized ")
                     sys.exit()
                 else:
                     list_compt = args.competences

     competencias = [configuracion['competencias']['url'], list_compt]

     #Read list of data
     list_data=[]
     if args.basico:
         list_data.append(configuracion['basico']['url'])
     if args.data:
         list_data.append(configuracion['calendario']['url'])
     if args.module:
         list_data.append(configuracion['modulo']['url'])
     if args.method:
         list_data.append(configuracion['metodologia']['url'])
     if args.system:
         list_data.append(configuracion['sistemaforma']['url'])

     if args.pdf:
         pdf = configuracion['pdf']['url']
     else:
         pdf = ""

     if args.university == "All":
         opciones = universidades([])
     else:
         opciones = args.university

     principal = configuracion['principal']['url']

     # Read existing data from files
     with open('data\\Uni.txt', 'r') as f:
          titulaciones = f.read()
     with open("data\\Iden.txt", 'r') as f:
          identificadores = f.read()

     #'.\output\Data_example.parquet'
     # Processing data:
     for op in opciones:
          if f"-{op}-" not in titulaciones:
               list = creacion_tablas(configuracion['principal']['url'], op)
               for i in list[0]:
                    if f"-{i}-" not in identificadores:
                         df_id =src.info_titul.DatosWeb.control(list_data, i, competencias, principal, op, list[1],
                                                        pdf, ubicacion)

                         print(df_id)
                         if path.exists(destination_path):
                             df = pd.read_parquet(destination_path)
                             # concatenar:
                             dfs = [df, df_id]
                             df_concat = pd.concat(dfs,ignore_index=True)
                             df_concat = df_concat.rename_axis('id').reset_index()
                             df_concat.set_index('id', inplace=True)
                             df_concat.astype(str).to_parquet(destination_path)
                         else:
                             df_id.astype(str).to_parquet(destination_path)

                         with open("data\\Iden.txt", mode="a") as f:
                            f.write(f"-{i}-")

                    else:
                         logging.info(f"Identifier {i} already exists in file Ide.txt for {op}")

               with open("data\\Uni.txt", mode="a") as f:
                  f.write(f"-{op}-")
                  logging.info(f"Added title {op} to file Uni.txt")
          else:
               logging.info(f"Title {op} already exists in file Uni.txt")
          print(op)

#Execute main
if __name__ == '__main__':
    main()
