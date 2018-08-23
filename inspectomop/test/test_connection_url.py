import os



def test_connection_url():
    pkg_test_path = os.path.dirname(__file__)
    connection_url = 'sqlite:///{}'.format(os.path.join(pkg_test_path,'tiny_omop_test.sqlite3'))
    return connection_url
