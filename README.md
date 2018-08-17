# InspectOMOP

---

## What is it?

**inspectomop** is a lightweight python package designed to assist data scientists with running queries against databases following the OHDSI OMOP Common Data Model.  

## Why was this built?

A large portion of data science research is spent on ETL (Extraction, Transformation, and Loading).  During the extraction phase if the data is stored in a relational database this involves writing SQL queries to gather information specific to the research question at hand.  

A large portion of research in data science involves data munging; the process of taking raw data in one format and transforming it to a more suitable form for downstream tasks.  

## Who is this for?



`OHDSI: Observational Health Data Sciences and Informatics`
`OMOP: Observation Medical Outcomes Partnership` 
# Main Features

- Automatic 

# SQL Dialect Compatibility

| dialect | inspectomop (python) | SQLRender (R) | 
| ----  | ---                   | ---       |
| BigQuery | No \* | Yes |
| Impala | Yes \* | Yes |
| Netezza | No \* | Yes |
| Oracle | Yes | Yes |
| PostgreSQL | Yes | Yes |
| Redshift | Yes \* | Yes
| SQL Server | Yes | Yes |
| SQLite | Yes | Unknown  |

\* 
- BigQuery : python DB-API, but no sqlalchemy dialect as of 8/17/2018 (https://github.com/GoogleCloudPlatform/google-cloud-python/issues/3603)
- Impala : external dialect available via [impyla](https://pypi.org/project/impyla/) package
- Redshift : external dialect available via [sqlalchemy-redshift](https://pypi.org/project/sqlalchemy-redshift/) package


# Where to get it

# Dependencies
- [SQLAlchemy](https://www.sqlalchemy.org) 
- [Pandas](https://pandas.pydata.org)

\* Developed using SQLAlchemy 1.2.1 and Pandas 0.22.0

# License


