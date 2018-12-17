"""
Payer plan related OMOP data queries.

Addapted from: https://github.com/OHDSI/OMOP-Queries
"""
from sqlalchemy import select as _select, join as _join,\
    union as _union, union_all as _union_all, \
    distinct as _distinct, between as  _between, alias as _alias, \
    and_ as _and_, or_ as _or_, literal_column as _literal_column, func as _func

import pandas as _pd, numpy as _np

def counts_by_years_of_coverage(inspector):
    """
    Returns counts of payer coverage based on continuous coverage (payer_plan_period_start_date - payer_plan_period_end_date)365.25.
    Note this method may count patients with more than one insurance plan multiple times.  Ex pt with Medicare Parts A, B, and D.

    Parameters
    ----------
    inspector : inspectomop.inspector.Inspector

    Returns
    -------
    df : pandas.DataFrame

    Notes
    -----
    Original SQL

    PP01: Continuous years with patient counts::

        SELECT
            floor((p.payer_plan_period_end_date - p.payer_plan_period_start_date)/365) AS year_int,
            count(1) AS num_patients
    	FROM
            payer_plan_period p
    	GROUP BY
            floor((p.payer_plan_period_end_date - p.payer_plan_period_start_date)/365)
    	ORDER BY 1;
    """
    p = _alias(inspector.tables['payer_plan_period'], 'p')

    columns = [p.c.payer_plan_period_end_date,p.c.payer_plan_period_start_date]
    statement = _select(columns)
    results = inspector.execute(statement).as_pandas()
    results['payer_plan_period_end_date'] = _pd.to_datetime(results['payer_plan_period_end_date'])
    results['payer_plan_period_start_date'] = _pd.to_datetime(results['payer_plan_period_start_date'])
    results['coverage_years'] = results['payer_plan_period_end_date'] - results['payer_plan_period_start_date']
    results['coverage_years'] = [_np.floor(cov.days/365.25) for cov in  results['coverage_years']]
    results = results[['coverage_years','payer_plan_period_start_date']].groupby('coverage_years', as_index=False).count()
    results.rename(mapper={'payer_plan_period_start_date':'count'},inplace=True, axis=1)

    return results


def patient_distribution_by_plan_type(inspector):
    """
    Returns counts of payer coverage by plan type.

    Parameters
    ----------
    inspector : inspectomop.inspector.Inspector

    Returns
    -------
    results : inspectomop.results.Results

    Notes
    -----
    Original SQL

    PP02: Patient distribution by plan type::

        SELECT
    	  t.plan_source_value,
    	  t.pat_cnt AS num_patients,
    	  100.00\*t.pat_cnt/ (sum(t.pat_cnt) over()) perc_of_total_count
    	FROM (
            SELECT
                p.plan_source_value,
                count(1) AS pat_cnt
            FROM
                payer_plan_period p
            GROUP BY
                p.plan_source_value
            ) t
    	ORDER BY
            t.plan_source_value;
    """
    p = _alias(inspector.tables['payer_plan_period'], 'p')
    columns = [p.c.plan_source_value, _func.count(p.c.plan_source_value).label('count')]
    statement = _select(columns).group_by(p.c.plan_source_value)
    return inspector.execute(statement)
