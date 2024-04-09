# Trabajo de Fin de Grado
Alba Sánchez Sánchez.   
Universidad Carlos III de Madrid.  
Curso 2022-23
## Context
This project downloads basic information about Spanish universities based on the html structure of the following link.
```
https://www.educacion.gob.es/ruct/consultaestudios?actual=estudios
```
## Installation
To install this project, follow these steps:

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Create and activate a virtual environment.
4. Install the required dependencies using `pip install -r requirements.txt`.

## Usage
Run the main script using the following command:
```bash
    python ReadingPipe.py [--destination_path DESTINATION_PATH] [--basico] [--data] [--competences COMPETENCES] [--module] [--method] [--system]  [--pdf] [--university UNIVERSITY]
```
 where:  
    * `--destination_path`is the path to save the data in parquet format.  
    * `--basico` is to download basic information about universities degrees.  
    * `--data`   is to download the start date of university degrees.  
    * `--competences` is to download the table of competencies of each university. Op: T (transversal), G (General), E (Específica), choose one, two or all three  
    * `--module`  is to download a table of subjects for each university degree.   
    * `--method` is to download a table of methods used in each university degree.  
    * `--system` is to download a table of the information systems used in each university degree  
    * `--pdf` is to download the PDF of each study plan.  
    * `--university` is to choose the number of the university that is read (only one).By default All, list of the universities in data_read.
## Directory Structure

The repository is organized as follows:

```bash
ReadingPipe /
├── data_read/
│   ├── Iden.txt
    ├── List_of_universities.txt
│   └──Uni.txt   
├── NLPipe/
├── topicmodeler/    
├── src/
│   ├── info_titul.py
│   └── utils.py
│ 
├── output 
│   └── pdf_output
├──  ifconfig.py
├──  gitmodules.txt
├── LICENSE
├── ReadingPipe.py
├── README.md
└──requirements.txt
```