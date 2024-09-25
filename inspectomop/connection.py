from sqlalchemy.engine import Connection as _AlchemyConnection

from .results import Results

class Connection(_AlchemyConnection):
    """
    A subclass of sqlalchemy.engine.Connection.
    
    The execute method returns an inspectomop.Results object
    that adds additional methods for retrieving query results as Pandas DataFrames.

    See Also
    --------
    inspectomop.results.Results
    """


    def execute(self, statement, parameters = None, execution_options = None):
        """
        Executes an SQL query on the OMOP CDM.

        Parameters
        ----------
        statement : sqlalchemy object or string
            sqlalchemy objects - statements can be created using sqlalchemy objects such as select, insert, etc. and the underlying table structures from Inspector.tables
                e.g. select([concept]).where(concept.concept_id==0)
            strings - can be a string containing an SQL statement such as
                e.g. 'SELECT concept_name from concept where concept_id = 0'

        Returns
        -------
        results : inspectomop.Results
            The results object is a subclass of sqlalchemy.engine.CursorResult with extra methods for retrieving the results as
            pandas DataFrames.  Traditional methods conforming to the python DB connection spec work as well e.g. fetchone, fetchmany, fetchall

        Notes
        -----
            *** Use of raw SQL strings is not recommended as they bypass the dialect translation and security
            provided by using SQLAlchemy ***

        See Also
        --------
        inpsectomop.Results, inspectomop.queries
        """
        return Results(super().execute(statement, parameters=parameters, execution_options=execution_options)) 