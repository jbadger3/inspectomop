from datetime import date as _date, datetime as _datetime
 
from sqlalchemy.engine.cursor import CursorResult as _CursorResult
import pandas as _pd

class Results(_CursorResult):
    """
    A cursor-like object with methods such as `fetchone`, `fetchmany` etc. that can be 
    used to retrieve rows of results from query execution.

    A subclass of sqlalchemy.engine.CursorResult
    that adds additional methods for retrieving query results as Pandas DataFrames.

    See Also
    --------
    Results.as_pandas, Results.as_pandas_chunks
    """
    def __init__(self, cursor_result):
        self.__cursor_result = cursor_result

    def __getattribute__(self,name):
        if name == '__cursor_result':
            return self.__cursor_result
        else:
            return super().__getattribute__(name)

    #CursorResult methods
    def all(self):
        return self.__cursor_result.all()
    
    def close(self):
        return self.__cursor_result.close()
    
    def columns(self, *col_expressions):
        return self.__cursor_result.columns(*col_expressions)
    
    def fetchall(self):
        return self.__cursor_result.fetchall()
    
    def fetchmany(self, size=None):
        return self.__cursor_result.fetchmany(size)

    def fetchone(self):
        return self.__cursor_result.fetchone()
    
    def first(self):
        return self.__cursor_result.first()
    
    def freeze(self):
        return self.__cursor_result.freeze()
    
    def keys(self):
        return self.__cursor_result.keys()
    
    def last_inserted_params(self):
        return self.__cursor_result.last_inserted_params()

    def last_updated_params(self):
        return self.__cursor_result.last_updated_params()
     
    def mappings(self):
        return self.__cursor_result.mappings()
        
    def merge(self, *others):
        return self.__cursor_result.merge(*others)
    
    def one(self):
        return self.__cursor_result.one()
    
    def one_or_non(self):
        return self.__cursor_result.one_or_none()
    
    def partitions(self, size = None):
        return self.__cursor_result.partitions(size)
    
    def postfetch_cols(self):
        return self.__cursor_result.postfetch_cols()
    
    def prefetch_cols(self):
        return self.__cursor_result.prefetch_cols()
        
    def scalar(self):
        return self.__cursor_result.scalar()
    
    def scalar_one(self):
        return self.__cursor_result.scalar_one()
    
    def scalar_one_or_none(self):
        return self.__cursor_result.scalar_one_or_none()
    
    def scalars(self):
        return self.__cursor_result.scalars()
    
    def splice_horizontally(self, other):
        return self.__cursor_result.splice_horizontally(other)
    
    def splice_vertically(self, other):
        return self.__cursor_result.splice_vertically(other)
    
    def supports_sane_multi_rowcount(self):
        return self.__cursor_result.supports_sane_multi_rowcount()
    
    def supports_sane_rowcount(self):
        return self.__cursor_result.supports_sane_rowcount()
    
    def tuples(self):
        return self.__cursor_result.tuples()
        
    def unique(self, strategy = None):
        return self.__cursor_result.unique(strategy)
    
    def yield_per(self, num):
        return self.__cursor_result.yield_per(num)

    #subclass methods
    def _convert_dates(self, df):
        if df.empty:
            return df
        first_row = df.iloc[0]
        cols_to_convert = []
        for col in df:
            item = first_row[col]
            if isinstance(item, _date) or isinstance(item, _datetime):
                df[col] = _pd.to_datetime(df[col])
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
        for rows in self.partitions(chunksize):
            df = _pd.DataFrame(data=rows, columns=columns)
            df = self._convert_dates(df)
            yield df

