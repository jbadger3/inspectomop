# InspectOMOP


## What is it?

**inspectomop** is a lightweight python 3 package that assists extracting electronic health record(EHR) data from relational databases following the OHDSI OMOP Common Data Model(CDM) standard v>=5.  

* OHDSI: Observational Health Data Sciences and Informatics
* OMOP: Observation Medical Outcomes Partnership

## Why was this built?
A large portion of data science research is spent on ETL (Extraction, Transformation, and Loading).  If the data are stored in a relational database, this typically means the extraction phase includes deciphering the database schema and figuring out how to write SQL queries that will properly gather the information of interest.  This can be both laborious and time consuming.  **inspectomop** attempts to simplify extracting data from the OMOP CDM with an API that is easy to use, extensible, and SQL dialect agnostic. 

## Developement of **inspectomop** follow three simple dictums:

1.  Research is more fun when less time is spent data wrangling  

2.  Don't reinvent the wheel

3.  Caring is sharing

One of the main benefits of adopting a CDM such as OMOP is that it promotes the sharing of ideas and methodology.  Queries in **inspectomop** are simple python functions of the format:

`def my_query(inputs, inspector, retrun_columns='all'):
    # create SQL agnostic query usually of the form
    statement = select([columns]).where(inputs == criteria)
    return inspector.execute(statement)`

Therefore, using sqlAlchemy any user can create custom queries  that can be shared accross intitutions and database management systems.


## Who is this for?

Short and simple: Python 3 programmers with an interest in interfacing with an EHR relational database formatted to follow the OMOP CDM standard.

The OHDSI group has developed and excellent library of tools written in R, but there are few, if any tools, for the python community.


## Features
- SQL dialect agnostic thanks to SQLAlchemy allowing for a variety of compatible database back ends 
- automatic relection of DB tables to dot accesable python objects for easy traversal and inspection
- preloaded with standard queries from the OHDSI group
- results returnable as pandas dataframes or dataframe chuncks for queries with a large number of rows
- extensibility withwith custom queries built from simple python functions

## SQL Dialect Compatibility

##### Below is a table comparing SQL dialect support for **inspectomop** versus the R SQLRender package written and maintained by the OHDSI group.  Note: compatibility is based solely on the availability of dialects written for SQLAlchemy and has not been explicitly tested by the author.  However, success stories, or troubleshooting questions are welcome!

| dialect | inspectomop (python) | SQLRender (R) |
| --- | --- | --- | 
| BigQuery | No \* | Yes |
| Impala | Yes \* | Yes |
| Netezza | No \* | Yes |
| Oracle | Yes | Yes |
| PostgreSQL | Yes | Yes |
| Redshift | Yes \* | Yes
| SQL Server | Yes | Yes |
| SQLite | Yes | Unknown |

#### \* BigQuery : python DB-API, but no sqlalchemy dialect as of 8/17/2018 (https://github.com/GoogleCloudPlatform/google-cloud-python/issues/3603)
#### \* Impala : external dialect available via [impyla](https://pypi.org/project/impyla/) package
#### \* Netezza : python DB-API, but no sqlalchemy dialect as of 8/17/2018
#### \* Redshift : external dialect available via [sqlalchemy-redshift](https://pypi.org/project/sqlalchemy-redshift/) package

# Where to get it

# Dependencies
- [SQLAlchemy](https://www.sqlalchemy.org) 
- [Pandas](https://pandas.pydata.org)

\* Developed using SQLAlchemy 1.2.1 and Pandas 0.22.0

# License


