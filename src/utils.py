import errno
import time
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

#1. Primera parte:

#Extrae todos los identificativos de todas las universidades que hay en la web y lo introduce en una lista
def universidades(opciones):
     time.sleep(2)
     soup = BeautifulSoup(requests.get('https://www.educacion.gob.es/ruct/consultaestudios?actual=estudios',verify=False).text, 'lxml')
     time.sleep(2)
     opciones=[elem['value'] for elem in soup.find(id ='codigoUniversidad').find_all('option') if elem['value'] !="" ]
     return opciones

#Creacion de identificadores para los urls: dado el numero lee tablas del numero hasta 1 y todos sus identificadores de la url que te manda

"""
cad: número máximo de páginas para las tablas
"""
def creacion_identificadores(cad,url_tablas):
     identificadores=[]
     numtablas = []
     while cad > 0:
          numtablas.append(str(cad))
          cad = cad - 1
     for i in numtablas:
          soup = BeautifulSoup(requests.get(re.sub('codigotablas', i, url_tablas),verify=False).text, 'lxml')
            # recorre toda la tabla, titulación por titulación
          enlace_siguiente = soup.find_all(class_="ver")
          for sep in enlace_siguiente:
               # mirar esto del indice para sacar el id de cada titulación
               subcadena = str(sep)[str(sep).index('cod=') + 4:str(sep).index('&amp')]
               if subcadena != None:
                    identificadores.append(subcadena)
     return identificadores


#lectura de identificadores de todas las universidades de todas las tablas: Por cada universidad lee el numero max de tabla
#saca todos los identificativos de esa universidad y los concatena con los que ya tiene.

"""
opciones: lista de IDs de cada universidad
"""
def creacion_tablas(url_tabla,opciones):
     cadena=""
     # sustituyo cada valor de id de cada universidad en la url_tabla
     url_uni = re.sub('universidad', opciones, url_tabla)

     # sustituyo el valor 'universidad' por cada id de cada universidad en la url_tabla, obteniendo un soup de las tablas para cada universidad
     soup = BeautifulSoup(requests.get(re.sub('universidad', opciones, url_tabla),verify=False).text, 'lxml')

     # num es un soup con todos los enlaces a cada una de las páginas de tablas existentes,
     # cada elemento de num es una página
     num = soup.findAll(class_="pagelinks")

     if not num: #si no hay elementos de clase pageLinks, solo hay una página de tablas
          cad=1 # cad: número de páginas de tablas
     else:
          for i in num:
               y = i.find_all('a') #entras en los elementos de la página
               cadena = str(y[len(y) - 1]) # cadena es el elemento de la última página existente
          #cad = última página de tablas = número de páginas con tablas
          #cad = int(cadena[cadena.index("-p=") + 3:cadena.index("&amp;ambito=&amp;")])
          cad = int(re.search(r'-p=(\d+)', cadena).group(1))

     identificadores = creacion_identificadores(cad, url_uni)
     list =[identificadores,cad]
     return list

def obtener_modulos(url_base, codigoin):
    url = url_base.replace('codigoin', codigoin)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    modulos = []
    # Encontrar la tabla con id 'modulo'
    tabla_modulos = soup.find('table', {'id': 'modulo'})
    if tabla_modulos:
        # Iterar sobre las filas del cuerpo de la tabla
        for fila in tabla_modulos.find('tbody').find_all('tr'):
            # Extraer la primera celda (que contiene la ID del módulo)
            celdas = fila.find_all('td')
            if celdas:
                modulo_id = celdas[0].text.strip()
                modulos.append(modulo_id)
    return modulos

def obtener_materias_por_modulo(url):
     response = requests.get(url)
     soup = BeautifulSoup(response.content, 'html.parser')
     ids_materias = []
     nombres_materias = []

     # Encontrar la tabla con id 'materia'
     tabla_materias = soup.find('table', {'id': 'materia'})
     if tabla_materias:
          # Iterar sobre las filas del cuerpo de la tabla
          for fila in tabla_materias.find('tbody').find_all('tr'):
               # Extraer la primera celda (que contiene la ID de la materia) y la segunda (que contiene el nombre)
               celdas = fila.find_all('td')
               if celdas:
                    materia_id = celdas[0].text.strip()
                    materia_nombre = celdas[1].text.strip()
                    ids_materias.append(materia_id)
                    nombres_materias.append(materia_nombre)

     return ids_materias, nombres_materias


def obtener_materias_por_modulos(url_base, codigoin, ids_modulos):
     diccionario_materias = {}
     nombres_materias = []

     for codModulo in ids_modulos:
          url = url_base.replace('codigoModulo', str(codModulo)).replace('codigoin', codigoin)
          ids_materias, nombres = obtener_materias_por_modulo(url)
          diccionario_materias[codModulo] = ids_materias
          nombres_materias.extend(nombres)

     return diccionario_materias, nombres_materias


def obtener_datos_asignatura(url_base, codModulo, codMateria, codigoin):
     url = url_base.replace('codigoModulo', str(codModulo)).replace('codigoMateria', str(codMateria)).replace(
          'codigoin', codigoin)
     response = requests.get(url)
     soup = BeautifulSoup(response.content, 'html.parser')
     asignaturas = []  # hacer fuera para iteraciones consecutivas

     # Encontrar la tabla con id 'asignatura'
     tabla_asignaturas = soup.find('table', {'id': 'asignatura'})
     if tabla_asignaturas:
          # Iterar sobre las filas del cuerpo de la tabla
          for fila in tabla_asignaturas.find('tbody').find_all('tr'):
               # Extraer la segunda celda (que contiene el nombre de la asignatura)
               celdas = fila.find_all('td')
               if celdas:
                    asignatura_nombre = celdas[1].text.strip()
                    asignaturas.append(asignatura_nombre)

     return asignaturas


def limpiar_texto(texto):
     # Eliminar saltos de línea y caracteres especiales
     texto_limpio = re.sub(r'\s+', ' ', texto)  # Reemplazar cualquier espacio en blanco (incluye \n, \t) por un espacio
     texto_limpio = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s]', '',
                           texto_limpio)  # Eliminar caracteres especiales, excepto letras y números
     return texto_limpio.strip()


def obtener_contenidos_modulo(url_base, codModulo, codMateria, codigoin):
     url = url_base.replace('codigoModulo', str(codModulo)).replace('codigoMateria', str(codMateria)).replace(
          'codigoin', codigoin)

     response = requests.get(url)
     soup = BeautifulSoup(response.content, 'html.parser')

     # Extract the "Contenidos de la materia" section
     contents_section = soup.find('fieldset', id='datosMateria_contenidos').find('div', class_='texto-editor')

     # Combine all the contents into a single string, joined by a delimiter like newlines or spaces
     combined_contents = ' '.join([limpiar_texto(content.text) for content in contents_section if content.text.strip()])

     return combined_contents