from sqlalchemy.engine.result import ResultProxy
import pandas as pd

class Results(ResultProxy):
    """
    Subclass of sqlalchemy.engine.result.ResultProxy
    Adds additional methods as_pandas and as_pandas_chunks
    """
    def __init__(self, results_proxy):
        context = results_proxy.context
        super().__init__(context)


    def as_pandas(self):
        """
        Return all rows as a pandas DataFrame

        See also
        --------
        pandas_chunks
        """
        columns = self.keys()
        rows = self.fetchall()
        return pd.DataFrame(data=rows, columns=columns)

    def pandas_chunks(self, chunksize):
        """
        Yields a pandas DataFrame with n_rows = chunksize
        """
        columns = self.keys()
        while True:
            rows = self.fetchmany(chunksize)
            if not rows:
                rows = self.fetchall()
            if rows:
                yield pd.DataFrame(data=rows, columns=columns)
            if not rows:
                break
