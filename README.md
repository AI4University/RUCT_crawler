# Bachelor's Thesis in Data Science and Engineering 

- **Author**: Lucía Cordero Sánchez
- **Institution**: Universidad Carlos III de Madrid.  
- **Date**: September 2023 - September 2024
- **Defended on**: September 2024

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
    python ReadingPipe.py [--destination_path DESTINATION_PATH] [--basico] [--data] [--competences COMPETENCES] [--method] [--system] [--activities] [--module] [--materias] [--asignaturas] [--university UNIVERSITY]
```
where:

* `--destination_path` is the path to save the data in parquet format.

* `--basico` downloads basic information about universities degrees.

* `--data` downloads the start date of university degrees.

* `--competences` downloads the table of competencies of each university. Op: T (transversal), G (General), E (Específica), choose one, two, or all three.

* `--method` downloads a table of methodologies used in each university degree.

* `--system` downloads a table of the information systems used in each university degree.

* `--activities` downloads a table of the activities from each university degree.

* `--module` downloads a table of modules (level 1 of the study plan) from each university degree.

* `--materias` downloads a table of the modules (level 2 of the study plan) from each university degree.

* `--asignaturas` downloads a table of the subjects (level 3 of the study plan) from each university degree.

* `--university` is to choose the number of the university that is read (only one). By default, All.

You can choose any combination of arguments to scrape the information at your desired level of granularity.

## Directory Structure

The repository is organized as follows:

```bash
├── ReadingPipe.py
│
├── Docs/
│   ├── TFG_Lucía_Cordero_Sánchez.pdf
│
├── data/
│   ├── identificadores_grados_final.txt
│   └── identificadores_universidades.txt
│
├── src/
│   ├── info_titul.py
│   └── utils.py
│   └── testing-pipeline.ipynb
│ 
├── logfile.log
├── inconfig.py
├── inconfig.cfg
├── README.md
├── LICENSE
└──requirements.txt
```
