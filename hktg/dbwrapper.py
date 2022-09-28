
import psycopg2
import os
import logging
import inspect
from datetime import datetime

DATABASE_URL = os.environ["DATABASE_URL"]

# util

LOCATION_TABLE = 'hkdb_locations'
INSTANCE_TABLE = 'hkdb_instances'
PRODUCT_TABLE = 'hkdb_products'
CONTAINER_TABLE = 'hkdb_containers'
LIMIT_TABLE = 'hkdb_limits'
TG_USERS_TABLE = 'hkdb_tg_users'
TG_ADMINS_TABLE = 'hkdb_tg_admins'
TG_REQUESTS_TABLE = 'hkdb_tg_requests'

def _join_dict(table: dict):
    result = []
    for k in table:
        result.append("%s=%s" % (k, table[k]))
    return ', '.join(result)

def _query(q: str):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    logging.info("SQL: %s" % q)
    cur.execute(q)
    # logging.info(cur.statusmessage)
    return conn, cur

# simple queries

def get_table(name):
    conn, cur = _query("SELECT * FROM %s;" % name)
    return cur.fetchall()

def update_value(table_name, data: dict, criteria:dict ):
    conn, cur = _query("UPDATE %s SET %s WHERE %s;" % (table_name, _join_dict(data), _join_dict(criteria)))
    conn.commit()

def delete_value(table_name, criteria:dict ):
    conn, cur = _query("DELETE FROM %s WHERE %s;" % (table_name, _join_dict(criteria)))
    conn.commit()

def insert_value(table_name, data: dict):
    columns = []
    values = []
    for key in data:
        columns.append(key)
        values.append("'%s'" % data[key])

    conn, cur = _query("INSERT INTO %s (%s) VALUES (%s);" % (table_name, ", ".join(columns), ", ".join(values)))
    conn.commit()

# some more logic over

def update_limit(product_id, amount, container_id):
    limits = get_table(LIMIT_TABLE)
    limit = next((x for x in limits if x[0] == product_id), None)

    if not amount:
        delete_value(LIMIT_TABLE, {'product': user_data[UserDataKey.CURRENT_ID]})
    elif limit:
        update_value(LIMIT_TABLE,
            {
                'amount': amount,
                "container_id": container_id,
                "product_id": product_id
            },
            {'id': limit[0]}
        )
    else:
        insert_value(LIMIT_TABLE, {
            'amount': amount,
            "container_id": container_id,
            "product_id": product_id
        },)

def update_instance(id, user_name, data):
    instances = get_table(INSTANCE_TABLE)
    instance = next((x for x in instances if x[0] == id), None)

    data["date"] =  "'%s'" % datetime.now()
    data["editor"] = "'%s'" % user_name

    if not amount:
        delete_value(INSTANCE_TABLE, {'id': user_data[UserDataKey.CURRENT_ID]})
    elif instance:
        update_value(INSTANCE_TABLE, data, {'id': id} )
    else:
        insert_value(INSTANCE_TABLE, data)

# def 

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    insert_value('hkdb_product', {"name": "Булгур"})
