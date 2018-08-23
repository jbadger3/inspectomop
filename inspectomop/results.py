import sqlalchemy.engine.result as _result
import pandas as _pd

class Results(_result.ResultProxy):
    """
    An interally used subclass of sqlalchemy.engine.result.ResultProxy
    that adds additional methods for retreving query results as Pandas DataFrames.

    See Results.as_pandas() and Results.as_pandas_chunks().
    """
    def __init__(self, results_proxy):
        context = results_proxy.context
        super().__init__(context)


    def as_pandas(self):
        """
        Return all rows as a pandas DataFrame

        See also
        --------
        as_pandas_chunks
        """
        columns = self.keys()
        rows = self.fetchall()
        return _pd.DataFrame(data=rows, columns=columns)

    def as_pandas_chunks(self, chunksize):
        """
        Yields a pandas DataFrame with n_rows = chunksize

        See also
        --------
        as_pandas
        """
        columns = self.keys()
        while True:
            rows = self.fetchmany(chunksize)
            if not rows:
                rows = self.fetchall()
            if rows:
                yield _pd.DataFrame(data=rows, columns=columns)
            if not rows:
                break
