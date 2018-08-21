import pytest
from inspectomop.inspector import Inspector

@pytest.fixture(scope="module")

def inspector():
    connection_url = 'sqlite:///test/test_omop.sqlite3'
    return Inspector(connection_url)


def test_attach_sqlite_db():
    """TODO"""
def test_clinical_data_tables():
   """TODO"""
def test_derived_element_tables():
    """TODO"""
def test_health_economic_data_tables():
    """TODO"""
def test_health_system_data_tables():
    """TODO"""
def test_metadata_tables():
    """TODO"""
def test_vocabulary_tables():
    """TODO"""
def test_table_info():
    """TODO"""
def test_execute():
    """TODO"""

