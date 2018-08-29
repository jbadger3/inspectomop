from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy import select
from sqlalchemy.engine import reflection

import pandas as _pd

from .results import Results

class Inspector():
    """
    Creates an Inspector object which can be used to run OMOP data queries

    Parameters
    ----------
    connection_url : string
        A connection url of form 'dialect+driver://username:password@host:port/database'.
        The driver can be any currently supported by sqlalchemy (sqlite, mysql, postgresql, etc.).

    Returns
    -------
    out : Inspector
        An Inspetor object

    Notes
    -----
        SQLite DBs require an additional '/' as in 'sqlite:///foo.db' for a relative path and
         'sqlite:////abs/path/to/foo.db' for an absolute path.

        See http://docs.sqlalchemy.org/en/latest/core/engines.html for more information about
        connection URLs and supported dialects.

    Examples
    --------
    >>> import inspectomop as iomop
    >>> connection_url = 'sqlite:///:memory:'
    >>> iomop.Inspector(connection_url)
    """

    def __init__(self,connection_url):
        self.connection_url = connection_url
        self.__engine = create_engine(self.connection_url)
        self.__tables = None
        self._sqlite_attach_list = None

    def _tables_summary_df(self):
        column_names = ['clinical','vocabulary','derived_element','health_system','health_economic'\
            ,'metadata']
        clinical = list(self.clinical_data_tables.keys())
        clinical.sort()
        vocab = list(self.vocabulary_tables.keys())
        vocab.sort()
        derived = list(self.derived_element_tables.keys())
        derived.sort()
        health_system = list(self.health_system_data_tables.keys())
        health_system.sort()
        health_economic = list(self.health_economic_data_tables.keys())
        health_economic.sort()
        metadata = list(self.metadata_tables.keys())
        metadata.sort()
        all_categories = [clinical,vocab,derived,health_system,health_economic,metadata]
        max_length = len(max(all_categories,key=len))
        for cat in all_categories:
            while True:
                if len(cat) != max_length:
                    cat.append('')
                else:
                    break
        data_dict = {col_name:table_names for col_name,table_names in zip(column_names,all_categories)}
        return _pd.DataFrame(data_dict)

    def __str__(self):
        tables_df = self._tables_summary_df()
        return 'connection_url : {}\n\ntables:\n{}'.format(self.connection_url,tables_df)

    def __repr__(self):
        return 'Inspector(\'{}\')'.format(self.connection_url)

    @property
    def engine(self):
        """
        A convenience hook to the underlying sqlalchemy engine.

        Use .execute() for submitting queries.
        """
        return self.__engine

    def _extract_table_classes(self):
        def add_tables(metadata):
            for table_name,table in metadata.tables.items():
                #sqlalchemy requires a primary key in each table for automatic mapping to work.
                #If no primary key is found, set the default primary key to be the first column in each table.
                if len(table.primary_key) == 0:
                    table.primary_key._reload([table.c[table.c.keys()[0]]])
            Base = automap_base(metadata=metadata)
            Base.prepare(engine=self.engine,reflect=True)
            for table_name, table in Base.classes.items():
                assert table_name not in tables.keys(), 'A table named {} was found more than once!'.format(table_name)
                tables[table_name] = table


        inspector = reflection.Inspector.from_engine(self.engine)
        tables = {}

        if self.engine.dialect.name == 'sqlite':
            schema_names = inspector.get_schema_names() #return [] for sqlalchemy versions < 1.2
            for schema in schema_names:
                metadata = MetaData(schema=schema)
                metadata.reflect(bind=self.engine)
                add_tables(metadata)
        else:
            metadata = MetaData()
            metadata.reflect(bind=self.engine)
            add_tables(metadata)

        self.__tables = tables

    @property
    def tables(self):
        if not self.__tables:
            self._extract_table_classes()
        return self.__tables

    @property
    def vocabulary_tables(self):
        table_names = ['concept','vocabulary','domain','concept_class','concept_relationship','relationship','concept_synonym','concept_ancestor','source_to_concept_map','drug_strength','cohort_definition','attribute_definition']
        return {table_name:table for table_name,table in self.tables.items() if table_name in table_names}

    @property
    def metadata_tables(self):
        table_names = ['cdm_source','metadata']
        return {table_name:table for table_name,table in self.tables.items() if table_name in table_names}

    @property
    def clinical_data_tables(self):
        table_names = ['person','observation_period','specimen','death','visit_occurrence','visit_detail','procedure_occurrence','drug_exposure','device_exposure','condition_occurrence','measurement','note','note_nlp','observation','fact_relationship']
        return {table_name:table for table_name,table in self.tables.items() if table_name in table_names}

    @property
    def health_system_data_tables(self):
        table_names = ['location','care_site','provider']
        return {table_name:table for table_name,table in self.tables.items() if table_name in table_names}

    @property
    def health_economic_data_tables(self):
        table_names = ['payer_plan_period','cost']
        return {table_name:table for table_name,table in self.tables.items() if table_name in table_names}

    @property
    def derived_element_tables(self):
        table_names = ['cohort','cohort_attribute','drug_era','dose_era','condition_era']
        return {table_name:table for table_name,table in self.tables.items() if table_name in table_names}



    def attach_sqlite_db(self,db_file, schema_name):
        """
        For SQLite backends, attaches an additional sqlite database file using
        'ATTACH DATABSE db_file AS schema_name'.

        ***This method can only be called if the dialect specified in connection_url is sqlite***

        Parameters
        ----------
        db_file : String
            A string giving a path to a database file.  Ex. 'databases/my_db_to_attach.db'

        schema_name : String
           The name to associate with the attached schema
        """
        def connect():
            import sqlite3
            connect_url = self.connection_url.replace('sqlite:///','')
            connection = sqlite3.connect(connect_url)
            cursor = connection.cursor()
            for db_file, schema_name in self._sqlite_attach_list:
                cursor.execute('attach database "{}" as {}'.format(db_file, schema_name))
            return connection

        assert self.__engine.dialect.name == 'sqlite', 'The dialect {} cannot be used with this method. Only "sqlite" dialect is supported'.format(dialect)

        if not self._sqlite_attach_list:
            self._sqlite_attach_list = [(db_file, schema_name)]
        else:
            self._sqlite_attach_list.append((db_file, schema_name))
        self.__tables = None #attaching a new database should force the tables to reload
        self.__engine = create_engine(self.connection_url, creator=connect)



    def table_info(self,table_name):
        """
        Return a Pandas DataFrame describing the fields of a table.

        Parameters
        ----------
        table_name : String

        """
        if table_name not in self.tables.keys():
            raise KeyError('`{}` not found in tables.'.format(table_name))
        table = self.tables[table_name]
        data = [[col.name, col.type, col.nullable, col.primary_key] for col in table.__table__.columns.values()]
        return _pd.DataFrame(data, columns=['column','type','nullable','primary_key'])



    def execute(self, statement):
        """
        Executes an SQL query on the OMOP CDM.

        Parameters
        ----------
        statement : sqlalchemy object or string
            sqlalchemy objects - statements can be created using sqlalchemy objects such as select, insert, etc. and the underlying table structures from Inspector.tables
                e.g. select([concept]).where(concept.concept_id==0)

            strings - can be a string containing an SQL statemment such as
                e.g. \'SELECT concept_name from concept where concept_id = 0\'

        Returns
        -------
            out : Results object

            The results object is a subclass of SQLAlchemy results_proxy with extra methods for retrieving the results as
            pandas DataFrames.  Traditional methods conforming to the python DB connection spec work as well e.g. fetchone, fetchmany, fetchall

        Notes
        -----
            *** Use of raw SQL strings is not recommended as they bypass the dialect translation and security
            provided by using SQLAlchemy ***

        See Also
        --------
        inpsectomop.Results, inspectomop.queries
        """
        results_proxy = self.engine.execute(statement)
        return Results(results_proxy)
