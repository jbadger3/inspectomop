.. inspectomop documentation master file

=======================
Welcome to InspectOMOP!
=======================

**Date**: |today| **Version**: |version|

**inspecotmop** is a database agnostic lightweight `python 3 <https://www.python.org>`__ package that assists with abstracting data from electronic health record (EHR) databases that follow the OMOP common data model (CDM).  The `source <https://github.com/jbadger3/inspectomop>`__ is available on GitHub.  Feel free to contribute or fork!

* OHDSI: Observational Health Data Sciences and Informatics
* OMOP: Observation Medical Outcomes Partnership

Background
~~~~~~~~~~

Interoperability is an important goal in healthcare and medical informatics research.  In an ideal world, one would be able to download the source code for a published project and only have to change a handful of lines of code to repeat an experiment, but this is far from the case.  Repeating experiments in medical informatics, especially when utilizing EHR data requires spending an inordinate amount of time on ETL (Extraction, Transformation, and Loading).  Why?  Part of the reason is that health care data can be recorded using any number of medical vocabularies, ontologies, and data formats which prohibits direct communication and necessitates an intermediate step of data mapping and normalization.  This can be achieved by adopting a common data model such as the OMOP CDM from the `OHDSI group <https://www.ohdsi.org>`__ and serving the data using a relational database management systems (RDBMS), but creates a new interoperability problem.  RDBMS typically use structured query language (SQL) as a fundamental mechanism for abstracting data and SQL itself is not universally portable across systems.  This is the problem **inspectomop** addresses.  **Inspectomop** utilizes `SQLAlchemy <https://www.sqlalchemy.org>`__ to act as a universal translator of SQL dialects and makes sharing end-to-end informatics projects possible.

.. figure:: inspectomop_diagram.png
   :scale: 25
   :align: center
   :alt: interoperability diagram

   **Interoperability problems and solutions:** **P1.** Data cannot be directly shared between EHRs.  **S1.**  Adopt the OMOP CDM  **P2.** SQL queries are not universally portable across RDBMs. **S2.** InspectOMOP, an SQL dialect agnostic python package.

Table of Contents
=================

.. toctree::
   :maxdepth: 3

   installation
   usage
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Acknowledgements
================

* This package builds off of amazing open source packages from the python community.  Many thanks to the developers and maintainers of pandas, SQLAlchemy, and numpy.

* A big thank you to the `OHDSI group <https://www.ohdsi.org>`__ for their continued efforts on improving the OMOP CDM and developing outstanding tools to advance the field of medical informatics.

* Most of the queries included in **inspectomop** were derived from the `OMOP-Queries <https://github.com/OHDSI/OMOP-Queries>`__ repository on GitHub.

* Test data were taken from a 1k sample of patients from the `SynPUF  <https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/SynPUFs/DE_Syn_PUF.html>`__ dataset converted by to the OMOP CDM and provided by `LTS Computing LLC <http://www.ltscomputingllc.com>`__
