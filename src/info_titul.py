import ReadingPipe
import errno
import time
import pandas as pd
import lxml
import logging
import re
import requests
from bs4 import BeautifulSoup
from src.utils import obtener_modulos, obtener_materias_por_modulos, obtener_datos_asignatura, obtener_contenidos_modulo
from concurrent.futures import ThreadPoolExecutor, as_completed

class DatosWeb():
    """
         Clase para comprobar que los enlaces a url, lista , id estan correctos
              -extraer datos basicos
              -tablas de competencias,modulo,formacion,metodologia
              -fecha de calendario

    """
    def __init__(self,logger=None):
        self._logger = logger or logging.getLogger(__name__)

    def control(lista, id, competencias, principal, op, max_tabla):
        """
        # list_data, i, competencias, principal, op, list[1]
        :param lista: lista de urls base del config file
        :param id: identificador de la titulación
        :param competencias: array con formato [url base de las competencias, competencias pedidas en el comando de entrada]
        :param principal: url base de la página principal para consultar una universidad
        :param op: identificador de la universidad
        :param max_tabla: número máximo de páginas con tablas para cada universidad y titulación
        :return:
        """
        df = pd.DataFrame()

        for i in lista:
        # Se procesan todas las URLs de la lista una a una
          DatosWeb._Mode(i, id, df)
        # Procesa la URL base de la página principal para consultar la universidad
        DatosWeb._Mode(principal, id, op, max_tabla, df)
        # Procesar las competencias: competencias[0] es la URL base y competencias[1] las competencias pedidas en el comando de entrada
        DatosWeb._Mode(competencias[0], id, competencias[1], df)

        return df


    def _Mode(*args):
        """
        Control de tipo de url que llega para leer
        :param args: url_base, identificador, lista de competencias, dataframe
        """
        mode_1 = 'basicos'
        mode_2 = 'competencias.palabratipocomp'
        mode_3 = 'calendarioImplantacion.cronograma'
        mode_4 = 'planificacion.modulos'
        mode_5 = 'planificacion.metodologias'
        mode_6 = 'planificacion.sistemas'
        mode_7 = 'planificacion.actividades'
        mode_8 = 'planificacion.materias'
        mode_9 = 'planificacion.materias.datos'
        mode_10 = 'planificacion.materias.contenidos'

        mode_url_to_func = {
          mode_1: DatosWeb.get_basic_data, #--basico
          mode_2: DatosWeb.get_competencies, #--competences
          mode_3: DatosWeb.get_year, #--data
          mode_4: DatosWeb.get_info, #--module
          mode_5: DatosWeb.get_info, #--method
          mode_6: DatosWeb.get_info, #--system
          mode_7: DatosWeb.get_info, #--actividades
          mode_8: DatosWeb.get_materias,
          mode_9: DatosWeb.get_asignaturas,
          mode_10: DatosWeb.get_contenidos,

        }

        if len(args)==3: # (url base, identificador universidad, dataframe al que van los resultados)
           # mode_url = str(args[0])[str(args[0]).index('actual=menu.solicitud.') + 22:str(args[0]).index('&')]
           base_index = str(args[0]).index('actual=menu.solicitud.') + 22
           end_index = str(args[0]).index('&', base_index) if '&' in str(args[0])[base_index:] else len(str(args[0]))
           mode_url = str(args[0])[base_index:end_index]

           func = mode_url_to_func[mode_url]

           if mode_url == mode_1:
                df_int = func(args[0], args[1])
                args[2]['Nombre'] = df_int['Nombre']
                args[2]['Conjunto'] = df_int['Conjunto']
                args[2]['Rama'] = df_int['Rama']
                args[2]['Habilita'] = df_int['Habilita']
                args[2]['Vinculacion'] = df_int['Vinculacion']
                args[2]['Codigo de Agencia'] = df_int['Codigo de Agencia']

           if mode_url == mode_3:
            # Ejemplo:
            # func(args[0], args[1]) = DatosWeb.get_year(args[0], args[1])

                args[2]['calendario'] = func(args[0], args[1])
                time.sleep(2)

           if mode_url == mode_4:
                    #print(func(args[0], args[1]))
                    args[2]['Modulo'] = func(args[0], args[1])
                    time.sleep(2)

           if mode_url == mode_5:
                    args[2]['Metodologia'] = func(args[0], args[1])
                    time.sleep(2)

           if mode_url == mode_6:
                    args[2]['Sistema de Formacion'] = func(args[0], args[1])

           if mode_url == mode_7:
               args[2]['Actividades'] = func(args[0], args[1])
               time.sleep(2)

           if mode_url == mode_8:
               materias = func(args[0], args[1])
               #print(materias)

               if 'Materias' in args[2].columns:
                   args[2]['Materias'] = args[2]['Materias'].apply(lambda x: materias)
               else:
                   args[2]['Materias'] = [materias]

               time.sleep(2)

           if mode_url == mode_9:
               asignaturas = func(args[0], args[1])
               #print(args[0], "\n", args[1], "\n", args[2])

               if 'Asignaturas' in args[2].columns:
                   args[2]['Asignaturas'] = args[2]['Asignaturas'].apply(lambda x: asignaturas)
               else:
                   args[2]['Asignaturas'] = [asignaturas]  # Asignar una lista vacía si no hay materias
           time.sleep(2)

           if mode_url == mode_10:
               contenidos = func(args[0], args[1])
               #print(args[0], "\n", args[1], "\n", args[2])

               if 'Contenidos' in args[2].columns:
                   args[2]['Contenidos'] = args[2]['Contenidos'].apply(lambda x: contenidos)
               else:
                   args[2]['Contenidos'] = [contenidos]  # Asignar una lista vacía si no hay contenidos
           time.sleep(2)

        elif len(args)==4: # (url base, identificador, array competencias, dataframe)

           #mode_url = str(args[0])[str(args[0]).index('actual=menu.solicitud.') + 22:str(args[0]).index('&')]
           base_index = str(args[0]).index('actual=menu.solicitud.') + 22
           end_index = str(args[0]).index('&', base_index) if '&' in str(args[0])[base_index:] else len(str(args[0]))
           mode_url = str(args[0])[base_index:end_index]

           func = mode_url_to_func[mode_url]
           if mode_url == mode_2:
                if args[2]:
                     for tipodecomp in args[2]:
                          nombre_competencia=""
                          if tipodecomp == 'G':
                               nombre_competencia = "Competencias Generales"

                          elif tipodecomp == 'T':
                               nombre_competencia = "Competencias Transversales"

                          elif tipodecomp == 'E':
                               nombre_competencia = "Competencias Especificas"
                          args[3][nombre_competencia] = func(args[0],args[1],nombre_competencia)
                          time.sleep(6)

        elif len(args)==5: # (url base, identificador, array competencias, dataframe, universidad, estado)
          args[4]['Universidad'] = DatosWeb.get_status(args[0], args[1], args[2], args[3], 'Universidad')
          time.sleep(3)
          args[4]['Estado'] = DatosWeb.get_status(args[0], args[1], args[2], args[3], 'Estado')



    def basico(url,var,id):
        """
        :url: URL
        :var: variable that we aim to extract
        :id: university ID
        :return: extracts the value from 'var' variable for a given URL and university id.

        """
        soup = BeautifulSoup(requests.get(re.sub('codigoin', id, url),verify=False).text, 'lxml')
        try:
          out = soup.findAll(attrs={"name": var})[0]['value']
        except Exception as e:
            out = "No encontrado"
            logging.info(f"This data doesn't exist")
        return out

    def get_basic_data(url,id):
        """
        :param url:  url basica de datos primarios; Nombre, agencia, conjunto, Rama
        :param id:   identificador de la titulacion indicada
        :return:     dataframe de los datos asociados al id
        """
        time.sleep(4)
        variables = ["denominacion", "conjunto", "rama.codigo", "habilita", "vinculado", "codigoAgencia"]
        output = [DatosWeb.basico(url, var, id) for var in variables]
        df_basic_data = pd.DataFrame([output], index=[id],
                            columns=['Nombre', 'Conjunto', 'Rama', 'Habilita', 'Vinculacion', 'Codigo de Agencia'])
        return df_basic_data


    def get_year(url, id):
        """
        :param url:  url que indica la fecha de inicio de la titulacion
        :param id:   identificador de la titulacion indicada
        :return:     diccionario con la fecha asociada al identificador
        """
        sleep_duration = 4
        time.sleep(sleep_duration)
        fecha_in = DatosWeb.basico(url, "curso_Inicio", id)
        return {id: fecha_in}


    def get_competencies(url,id,nombre_compt):
        """
        :param url: url asociada a la parte de las tablas de competencias
        :param id: identificador de la titulacion indicada
        :param nombre_compt: clase de competencia que se lee; especifica, general o transversal (E, G o T)
        :return: diccionario del id asociado a una lista de competencias
        """

        competencies = {
          "Competencias Generales": {"palabra": "generales", "tipo": "G"},
          "Competencias Transversales": {"palabra": "transversales", "tipo": "T"},
          "Competencias Especificas": {"palabra": "especificas", "tipo": "E"}
        }
        url_params = competencies.get(nombre_compt)
        # sustituir el identificador de la titulación en la url base para competencias
        t_competencias = re.sub('codigoin', id, url)
        if url_params:
          # sustituir el tipo de competencia en la url t_competencias
          t_competencias = re.sub('palabratipocomp', url_params["palabra"], t_competencias)
          t_competencias = requests.get(re.sub('tipodecomp', url_params["tipo"], t_competencias), verify=False)
          soup = BeautifulSoup(t_competencias.text, 'lxml')
        try:
          df_sistemaforma = pd.read_html(str(soup.select('table')[0]))[0]
          info = df_sistemaforma['Denominación'].tolist()
        except Exception as e:
           info = 'No encontrado'
        return {id:info}


    def get_info(url,id):
        """
        :param url: url que puede leer sistemas de formacion de titulacion, modulos y metodologias existentes asociados al id
        :param id: identificador de la titulacion indicada
        :return: diccionario del id asociado a una lista de competencias
        """
        sleep_duration = 4
        time.sleep(sleep_duration)
        soup = BeautifulSoup(requests.get(re.sub('codigoin', id, url),verify=False).text, 'lxml')
        try:
           data = pd.read_html(str(soup.select('table')[0]))[0]
           info = data['Denominación'].tolist()
        except Exception as e:
            info ="No encontrado"

        return {id : info}

     #Creacion de la tabla inicial de la url que se le pasa y guarda nombre, uni,estado.
    def get_status(url_tabla,id,op,max_tabla,col):
        """
        :param url_tabla:  url general donde aparecen todas las titulaciones
        :param id:         id que busco para completar los datos
        :param op:         código de universidad donde estoy
        :param max_tabla:        numero de tablas maxi
        :param col:        leo columna "Universidad" o columna "Estado"
        :return:           diccionario donde se asocia el id a la info guardada
        """
        sleep_duration = 4
        dic = {}
        for i in range(1, max_tabla + 1):
          url = re.sub('codigotablas', str(i), re.sub('universidad', op, url_tabla))
          try:
              soup = BeautifulSoup(requests.get(url, verify=False).text, 'lxml')
              df_tabla = pd.read_html(str(soup.select('table')[0]))[0]
              for codigo in df_tabla["Código"]:
                  try:
                      if str(codigo) == id[0:7]:
                          info = df_tabla.loc[df_tabla['Código'] == codigo][col].tolist()
                          dic[id] = info
                          return {id : info}
                  except Exception as e:
                      return {id : "No encontrado"}
          except Exception as e:
              print(f"Error while retrieving table {i}: {e}")
        time.sleep(sleep_duration)
        return dic

    def get_materias(url_base, id):
        url_modulos = 'https://www.educacion.gob.es/ruct/solicitud/modulos?actual=menu.solicitud.planificacion.modulos&cod=codigoin'
        ids_modulos = obtener_modulos(url_modulos, id)

        diccionario_materias, nombres_materias = {}, []
        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = [executor.submit(obtener_materias_por_modulos, url_base, id, [modulo]) for modulo in ids_modulos]

            for future in as_completed(futures):
                try:
                    parcial_diccionario_materias, parcial_nombres_materias = future.result()
                    diccionario_materias.update(parcial_diccionario_materias)
                    nombres_materias.extend(parcial_nombres_materias)
                except Exception as e:
                    print(f"Error obtaining materias: {e}")

        return nombres_materias

    def get_asignaturas(url_base, id):
        url_base_modulos = 'https://www.educacion.gob.es/ruct/solicitud/modulos?actual=menu.solicitud.planificacion.modulos&cod=codigoin'
        url_base_materias = 'https://www.educacion.gob.es/ruct/solicitud/datosModulo?codModulo=codigoModulo&actual=menu.solicitud.planificacion.materias&cod=codigoin'

        ids_modulos = obtener_modulos(url_base_modulos, id)
        diccionario_materias, _ = obtener_materias_por_modulos(url_base_materias, id, ids_modulos)

        todas_asignaturas = []
        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = []
            for codModulo, ids_materias in diccionario_materias.items():
                for codMateria in ids_materias:
                    futures.append(executor.submit(obtener_datos_asignatura, url_base, codModulo, codMateria, id))

            for future in as_completed(futures):
                try:
                    asignaturas = future.result()
                    todas_asignaturas.extend(asignaturas)
                except Exception as e:
                    todas_asignaturas = "No encontrado"
                    print(f"Error obtaining asignaturas: {e}")

        return todas_asignaturas


    def get_contenidos(url_base, id):
        url_base_modulos = 'https://www.educacion.gob.es/ruct/solicitud/modulos?actual=menu.solicitud.planificacion.modulos&cod=codigoin'
        url_base_materias = 'https://www.educacion.gob.es/ruct/solicitud/datosModulo?codModulo=codigoModulo&actual=menu.solicitud.planificacion.materias&cod=codigoin'
        ids_modulos = obtener_modulos(url_base_modulos, id)
        diccionario_materias, _ = obtener_materias_por_modulos(url_base_materias, id, ids_modulos)

        contenidos_lista = []
        with ThreadPoolExecutor(max_workers=16) as executor:  # Usar 16 hilos para aprovechar el rendimiento de la M2
            futures = []
            for codModulo, ids_materias in diccionario_materias.items():
                for codMateria in ids_materias:
                    futures.append(executor.submit(obtener_contenidos_modulo, url_base, codModulo, codMateria, id))

            for future in as_completed(futures):
                try:
                    contenidos = future.result()
                    contenidos_lista.append(contenidos)
                except Exception as e:
                    print(f"Error obtaining contents: {e}")

        return contenidos_lista