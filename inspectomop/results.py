from datetime import date as _date, datetime as _datetime

import sqlalchemy.engine.result as _result
import pandas as _pd

class Results(_result.ResultProxy):
    """
    A cursor-like object with methods such as `fetchone`, `fetchmany` etc. that can be used to retrieve rows of results from query execution.

    A subclass of sqlalchemy.engine.result.ResultProxy
    that adds additional methods for retreving query results as Pandas DataFrames.

    See Also
    --------
    Results.as_pandas, Results.as_pandas_chunks
    """
    def __init__(self, results_proxy):
        context = results_proxy.context
        super().__init__(context)

    def _convert_dates(self, df):
        if df.empty:
            return df
        first_row = df.iloc[0]
        cols_to_convert = []
        for col in df:
            item = first_row[col]
            if isinstance(item, _date) or isinstance(item, _datetime):
                df[col] = _pd.to_datetime(df[col],errors='ignore')
        return df

    def as_pandas(self):
        """
        Return all rows from a `results` object as a pandas DataFrame

        Returns
        -------
        results : Pandas.DataFrame

        See also
        --------
        as_pandas_chunks
        """
        columns = self.keys()
        rows = self.fetchall()
        df = _pd.DataFrame(data=rows, columns=columns)
        df = self._convert_dates(df)
        return df
    def as_pandas_chunks(self, chunksize):
        """
        Yields a pandas DataFrame with n_rows = chunksize

        Parameters
        ----------
        chunksize : int
            number of rows to return in each chunk

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
                df = _pd.DataFrame(data=rows, columns=columns)
                df = self._convert_dates(df)
                yield df
            if not rows:
                break
