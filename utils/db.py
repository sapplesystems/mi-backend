from django.db import connection
from collections import namedtuple


def get_db_rows(sql, args=None):
    cursor = connection.cursor()
    cursor.execute(sql, args)
    columns = [col[0] for col in cursor.description]
    RowType = namedtuple('Row', columns)
    data = [
        RowType(*row) # Edited by John suggestion fix
        for row in cursor.fetchall()]

    cursor.close()
    return data
