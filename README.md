# InspectOMOP

<table>
<tr>
  <td>Latest Release</td>
  <td>
    <a href="https://pypi.org/project/inspectomop/">
    <img src="https://img.shields.io/pypi/v/inspectomop.svg" alt="latest release" />
    </a>
  </td>
</tr>
<tr>
  <td>Package Status</td>
  <td>
		<a href="https://pypi.org/project/inspectomop/">
		<img src="https://img.shields.io/pypi/status/inspectomop.svg" alt="status" /></td>
		</a>
</tr>
<tr>
  <td>License</td>
  <td>
    <a href="https://github.com/jbadger3/inspectomop/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/jbadger3/inspectomop.svg" alt="license" />
    </a>
</td>
</tr>
<tr>
  <td>Usage Stats</td>
  <td>
    <img src="https://img.shields.io/pypi/dm/InspectOMOP.svg" alt="usage" />
    </a>
</td>
</tr>
</table>

## What is it?

**inspectomop** is a lightweight python 3 package that assists in the extraction of electronic health record(EHR) data from relational databases following the OHDSI OMOP Common Data Model(CDM) standard v>=5.  

* OHDSI: Observational Health Data Sciences and Informatics
* OMOP: Observation Medical Outcomes Partnership

## Why was this built?
A large portion of data science research is spent on ETL (Extraction, Transformation, and Loading).  If the data are stored in a relational database, the first step includes deciphering the database schema and figuring out how to write SQL queries that will properly gather the information of interest.  This can be both laborious and time consuming.  **inspectomop** attempts to simplify extracting data from the OMOP CDM with an API that is easy to use, extensible, and SQL dialect agnostic.

One of the main benefits of adopting a CDM such as OMOP is that it promotes the sharing of ideas and methodology.  Queries in **inspectomop** are simple python functions so using sqlAlchemy any user can create custom queries that can be shared across institutions and database management systems.

```sh
def my_query(inputs, inspector):

    # create SQL agnostic query usually of the form

    statement = select([columns]).where(inputs == criteria)

    return inspector.execute(statement)
```

## Who is this for?

**inspectomop** is for any python 3 programmer with an interest in interfacing with an EHR relational database formatted to follow the OMOP CDM standard.

The OHDSI group has developed an excellent library of tools and methods written in R, but there are few, if any tools, for the python community.


## Features
- SQL dialect agnostic thanks to SQLAlchemy allowing for a variety of compatible database back ends
- automatic reflection of DB tables to dot accessible python objects for easy traversal and inspection
- preloaded with standard queries from the OHDSI group
- results returnable as pandas dataframes or dataframe chunks for queries with a large number of rows
- extensibility with custom queries built from simple python functions

## SQL Dialect Compatibility

Below is a table comparing SQL dialect support for **inspectomop** versus the R SQLRender package written and maintained by the OHDSI group.  

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

Note: Compatibility is primarily based on the availability of dialects written for SQLAlchemy.  Most have not bee explicitly tested by the author with the exception of SQLite v2.6.0 and SQL Server 2016 Service Pack 1 (13.0.4001.0).  However, success stories and troubleshooting questions are welcome!

#### \* BigQuery : python DB-API, but no sqlalchemy dialect as of 8/17/2018 (https://github.com/GoogleCloudPlatform/google-cloud-python/issues/3603)
#### \* Impala : external dialect available via [impyla](https://pypi.org/project/impyla/) package
#### \* Netezza : python DB-API, but no sqlalchemy dialect as of 8/17/2018
#### \* Redshift : external dialect available via [sqlalchemy-redshift](https://pypi.org/project/sqlalchemy-redshift/) package

# Where to get it
* install from PyPI using pip with
```sh
pip install inspectomop
```
# Dependencies
- [SQLAlchemy v>=1.2](https://www.sqlalchemy.org)
- [Pandas](https://pandas.pydata.org)

\* Developed using SQLAlchemy 1.2.1 and Pandas 0.22.0

# Documentation
Read the official [documentation](https://inpsectomop.readthedocs.io/en/master/) hosted on readthedocs for more information on usage and examples.

# License
Feel free to fork, copy, share and contribute.  This software released under [GNU Affero GPL v3.0](https://github.com/jbadger3/inspectomop/tree/maste/LICENSE.md)  
