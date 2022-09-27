
import psycopg2
import os
import logging
import inspect

# DATABASE_URL = os.environ["DATABASE_URL"]
DATABASE_URL = 'postgres://wprlgaxw:QoFbjtHSP05i9YUKOrVVX0W4K5wp8zBb@rogue.db.elephantsql.com/wprlgaxw'
# util

LOCATION_TABLE = 'hkdb_location'
INSTANCE_TABLE = 'hkdb_instance'
PRODUCT_TABLE = 'hkdb_product'

def _query(q: str):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    logging.info("SQL: %s" % q)
    cur.execute(q)
    # logging.info(cur.statusmessage)
    return conn, cur

def _get_table(name):
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

# get

def get_location_list():
    return _get_table('hkdb_location')

def get_instance_list():
    return _get_table('hkdb_instance')

def get_product_list():
    return _get_table('hkdb_product')

# add

def add_instance(location, product, amount):
    logging.info(inspect.stack()[0][0].f_code.co_name)
    pass

def add_product(product):
    logging.info(inspect.stack()[0][0].f_code.co_name)
    pass

def add_location(location):
    logging.info(inspect.stack()[0][0].f_code.co_name)
    pass

# remove

def remove_instance(location, product, amount):
    logging.info(inspect.stack()[0][0].f_code.co_name)
    pass

def remove_product(product):
    logging.info(inspect.stack()[0][0].f_code.co_name)
    pass

def remove_location(location):
    logging.info(inspect.stack()[0][0].f_code.co_name)
    pass

# update

def update_instance(location, product, amount):
    logging.info(inspect.stack()[0][0].f_code.co_name)
    pass

def update_product(product_id, new_name):
    logging.info(inspect.stack()[0][0].f_code.co_name)
    pass

def update_location(location):
    logging.info(inspect.stack()[0][0].f_code.co_name)
    pass



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    insert_value('hkdb_product', {"name": "Булгур"})
