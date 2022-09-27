
import psycopg2
import os
import logging
import inspect

DATABASE_URL = os.environ["DATABASE_URL"]

# util

LOCATION_TABLE = 'hkdb_locations'
INSTANCE_TABLE = 'hkdb_instances'
PRODUCT_TABLE = 'hkdb_products'
CONTAINER_TABLE = 'hkdb_containers'
LIMIT_TABLE = 'hkdb_limits'

def _query(q: str):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    logging.info("SQL: %s" % q)
    cur.execute(q)
    # logging.info(cur.statusmessage)
    return conn, cur

def get_table(name):
    conn, cur = _query("SELECT * FROM %s;" % name)
    return cur.fetchall()

def update_value(table_name, data: dict, criteria:dict ):
    def join_dict(table: dict):
        result = []
        for k in table:
            result.append("%s=%s" % (k, table[k]))
        return ', '.join(result)

    conn, cur = _query("UPDATE %s SET %s WHERE %s;" % (table_name, join_dict(data), join_dict(criteria)))
    conn.commit()

def insert_value(table_name, data: dict):
    columns = []
    values = []
    for key in data:
        columns.append(key)
        values.append("'%s'" % data[key])

    conn, cur = _query("INSERT INTO %s (%s) VALUES (%s);" % (table_name, ", ".join(columns), ", ".join(values)))
    conn.commit()

# def 

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    insert_value('hkdb_product', {"name": "Булгур"})
