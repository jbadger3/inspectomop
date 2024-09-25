.. _usage:

=====
Usage
=====

There is a tiny SQLite database (1.4 MB) included with **inspectomop** to give first-time users a limited experimental playground and the ability to run code from the examples below.

.. note::
   InspectOMOP does **NOT** contain EHR data from real patients.  The data are entirely synthetic and come from the `SynPUF <https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/SynPUFs/DE_Syn_PUF.html>`__ dataset released by Centers for Medicaid and Medicare Services (CMS).

Connecting to a database
========================

:py:class:`.Inspector` objects are in charge of interfacing with the backend database, extracting the available OMOP CDM tables, and performing queries.

Inspectors require a single parameter, `connection_url`, for instantiation:

.. ipython:: python

   import inspectomop as iomop
   connection_url = iomop.test.test_connection_url()
   inspector = iomop.Inspector(connection_url)

`connection_url` is a database URL defined by `SQLAlchemy <https://docs.sqlalchemy.org/en/latest/>`__ that describes how to connect to your database.  A database URL has three main components: a dialect, driver, and URL.  The dialect indicates what type of backend DB you wish to connect to.  You can use any supported by SQLAlchemy (MySql, SQLite, Postgres, etc.) out-of-the-box or a dialect written by a third party.  See the full list `here <https://docs.sqlalchemy.org/en/latest/dialects/index.html>`__.  The driver indicates which python DBAPI library you wish to use to run your queries.  The SQLAlchemy dialects often contain a default DBAPI, so this may or may not be necessary depending on your configuration. Finally, the URL indicates where to look for the database and includes options for supplying a username and password.

::

  'dialect+driver://username:password@host:port/database'

.. note::

   See the SQLAlchemy docs on `engine configuration <https://docs.sqlalchemy.org/en/latest/core/engines.html>`__ for more details.

Here is an example URL for MySQL:

.. ipython:: python

   mysql_url = 'mysql://johnny:appleseed@localhost/omop'

and one for SQLite:

.. ipython:: python

   sql_url = 'sqlite:////abs/path/to/tiny_omop_test.sqlite3'

As you can see SQLite URLs are slightly different.  They include an extra '/' and thus will have '///' for relative paths and '////' for absolute paths.


Inspecting a database
=====================

Accessing tables
~~~~~~~~~~~~~~~~

The tables property of an :py:class:`.Inspector` contains a dictionary of associated OMOP tables that are accessible by table name.

.. ipython:: python

   inspector.tables.keys()
   person = inspector.tables['person']


Accessing table columns
~~~~~~~~~~~~~~~~~~~~~~~
The columns in each table object are dot accessible and can be assigned to variables to construct query statements.


.. ipython:: python

   from sqlalchemy import select

   person_id = person.person_id
   statement = select(person_id)
   print(statement)

Complete table descriptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can also get a description of all columns within a table, the data types, etc.

.. ipython:: python

   inspector.table_info('person')

Running built-in queries
========================

A basic example
~~~~~~~~~~~~~~~

There are a variety of built in queries available in the :ref:`queries` submodule.  A typical query takes arguments for inputs (concept_ids, keywords, etc.), an :py:class:`.Inspector` to run the query against, and optionally a list of columns to subset from the default columns returned by the query.


.. ipython:: python
   :okwarning:

   # retrieve concepts for a list of concept_ids
   from inspectomop.queries.general import concepts_for_concept_ids

   concept_ids = [2, 3, 4, 7, 8, 10, 46287342, 46271022]
   return_columns = ['concept_name', 'concept_id']
   statement = concepts_for_concept_ids(concept_ids, inspector, return_columns=return_columns)

   with inspector.connect() as connection:
      results = connection.execute(statement).all()
   results

.. note::

    You can get a list of columns a query returns by looking at the `return_columns` parameter in the docstring for each query.

Specifying how results are returned
===================================

By default all queries return an :py:class:`sqlalchemy.sql.expression.Executable` statement that can be evaluated in a connection context 
from :py:meth:`.Inspector.connect` in a fashion identical to SQLAlchemy. 

See the `SQLAlchemy Unified Tutorial <https://docs.sqlalchemy.org/en/20/tutorial/index.html>`_.

Working directly with statements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. ipython:: python

   statement = concepts_for_concept_ids(concept_ids, inspector)
   with inspector.connect() as connection:
      results = connection.execute(statement)
      #get the return column names
      results.keys()
      #get one row
      results.fetchone()
      #get many rows
      two_results = results.fetchmany(2)
      len(two_results)

      #iterating over rows
      for row in two_results:
         print(row[:2])

Returning results as Pandas DataFrames
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to the typical database cursor methods like .fetchone() and .fetchall() :py:class:`inspectomop.Results` objects
also have two handy methods, .as_pandas() and .as_pandas_chunks() for returning results as pandas DataFrames.

.. ipython:: python

   #return the results as as a dataframe
   with inspector.connect() as connection:
      results = connection.execute(concepts_for_concept_ids(concept_ids, inspector)).as_pandas()
   results[['concept_name','vocabulary_id']]

   #return the results in chunks
   chunksize = 3
   with inspector.connect() as connection:
      results = connection.execute(concepts_for_concept_ids(concept_ids, inspector)).as_pandas_chunks(chunksize)
      for num, chunk in enumerate(results):
         print('chunk {}'.format(num + 1))
         print(chunk['concept_name'])

Creating custom queries
=======================

From SQLAlchemy SQL Expressions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Statements built out of constructs from SQLAlchemy's *SQL Expression API* make queries backend-neutral paving the way for sharable code that can be used in a plug-and-play fashion.  While there is no guarantee that `every` query will work with `every` backend, most of the basic selects, joins, etc should run without issue.

SQLAlchemy is extremely powerful, but like any software package, has a bit of a learning curve.  It is highly recommended that users read the `SQLAlchemy Unified Tutorial <https://docs.sqlalchemy.org/en/20/tutorial/index.html>`__ and note the warning below.

Below are a few simple examples of using SQLAlchemy expression language constructs for running queries on the OMOP CDM.

.. warning::

   Tables from Inspector.tables are actually mapped to ORM objects.  These are *NOT* the same as `Table` objects from the SQLAlchemy Core API, although they can be used in nearly identical fashion in SQL Expressions with the following caveat about accessing table columns:

   .. ipython:: python
      :okexcept:

      from sqlalchemy import alias
      p = inspector.tables['person']
      p_alias = alias(inspector.tables['person'], 'p_alias')
      # p is an automapped ORM object with dot accessible columns
      p
      p.person_id

      # p_alias is an Alias object.
      # Columns must be accessed using .c.column
      p_alias
      p_alias.c.person_id

      # and so this fails
      p_alias.person_id

   *Explanation:* Using a portion of the SQLAlchemy ORM to infer table structure was a conscious design decision.  Although it makes for a bit of confusion when constructing queries with SQL expressions users that work in an interactive development environment (iPython, Jupyter Notebooks, etc.) get the benefit of dot accessible column properties.  In addition, automapping alleviates compatibility issues that would inevitably arise with hard-coded table structures on future versions of the OMOP CDM.

Select all of the conditions for person 1:

.. ipython:: python

   from sqlalchemy import select, and_
   
   c = inspector.tables['concept']
   co = inspector.tables['condition_occurrence']
   person_id = 1
   statement = select(co.condition_start_date, co.condition_concept_id, c.concept_name).\
               where(and_(\
                   co.person_id == person_id,\
                   co.condition_concept_id == c.concept_id))
   print(statement)
   with inspector.connect() as con:
      results = con.execute(statement).as_pandas()
   results 

Count the number of inpatient and outpatient visits for each person broken down by visit type and sorted by person_id:

.. ipython:: python

   from sqlalchemy import join, func

   vo = inspector.tables['visit_occurrence']
   j = join(vo, c, vo.visit_concept_id == c.concept_id)
   j2 = join(j, p, vo.person_id == p.person_id)
   visit_types = ['Inpatient Visit','Outpatient Visit']

   statement = select(p.person_id, func.count(vo.visit_occurrence_id).label('num_visits'), c.concept_name.label('visit_type')).\
               select_from(j2).\
               where(c.concept_name.in_(visit_types)).\
               group_by(p.person_id, c.concept_name).\
               order_by(p.person_id)
   with inspector.connect() as con:
      results = con.execute(statement).as_pandas()
   results

From Strings
~~~~~~~~~~~~
You `can` execute unaltered SQL strings directly, but remember to always used parametrized code for shared/production projects.

.. warning::

   Only use strings for rapid prototyping and in-house projects! Executing strings directly breaks backend compatibility and can potentially lead to SQL injection attacks!

Example:

.. ipython:: python

   from sqlalchemy import text
   statement = text('select person_id from person')
   with inspector.connect() as con:
      results = con.execute(statement).as_pandas()
   results

Sharing custom queries as functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Custom queries that may prove useful to the OMOP CDM community can easily be shared by wrapping them in a function and following a standard recipe.  `View the source code <https://github.com/jbadger3/inspectomop>`__ on GitHub to get a better feel of how to construct queries and contribute (via pull request or posting your function in issues).

In general, consider the following:

* appropriately named query functions should begin with the data you intend to return and end with the data/parameters you expect as input. E.g. `concepts_for_concept_ids`
* the return value for a query should `always` be a :py:class:`sqlalchemy.sql.expression.Executable`.  In most cases this will be :py:class:`sqlalchemy.sql.expression.Select`
* write a docstring following the `numpydoc docstring guide <https://numpydoc.readthedocs.io/en/latest/format.html>`__ to accompany your code.

Prototype:

.. code-block:: python

  import pandas as pd
  
  def output_for_input(inputs, inspector, return_columns=None):
      """
      Short description.

      Longer explanation.

      Parameters
      ----------
      inputs : type
          description of inputs
      inspector : inspectomop.inspector.Inspector
      return_columns : list of str, optional
          - optional subset of columns to return from the query
          - columns : ['col_name_1', 'col_name_2']

      Returns
      -------
      results : sqlalchemy.sql.expression.Executable

      Notes
      -----
      Optional

      """
      columns = [] # specify return columns

      if return_columns: # filter based on end-user selection
          columns = [col for col in columns if col.name in return_columns]

      statement = select(*columns).where(inputs == criteria)

      return statement
