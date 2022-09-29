
import psycopg2
import logging
from datetime import datetime

# DB tables names

class Tables:
    LOCATION = 'hkdb_locations'
    INSTANCE = 'hkdb_instances'
    PRODUCT = 'hkdb_products'
    CONTAINER = 'hkdb_containers'
    LIMIT = 'hkdb_limits'
    TG_USERS = 'hkdb_tg_users'
    TG_ADMINS = 'hkdb_tg_admins'
    TG_REQUESTS = 'hkdb_tg_requests'

import os
DATABASE_URL = os.environ["DATABASE_URL"]

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


def update_value(table_name, data: dict, criteria: dict):
    conn, cur = _query("MODIFY %s SET %s WHERE %s;" %
                       (table_name, _join_dict(data), _join_dict(criteria)))
    conn.commit()


def delete_value(table_name, criteria: dict):
    conn, cur = _query("DELETE FROM %s WHERE %s;" %
                       (table_name, _join_dict(criteria)))
    conn.commit()


def insert_value(table_name, data: dict):
    columns = []
    values = []
    for key in data:
        columns.append(key)
        values.append("'%s'" % data[key])

    conn, cur = _query("INSERT INTO %s (%s) VALUES (%s);" %
                       (table_name, ", ".join(columns), ", ".join(values)))
    conn.commit()

# some more logic over


def update_limit(product_id, amount, container_id):
    limits = get_table(LIMIT)
    limit = next((x for x in limits if x[0] == product_id), None)

    if not amount:
        delete_value(
            LIMIT, {'product': user_data[UserDataKey.CURRENT_ID]})
    elif limit:
        update_value(LIMIT,
                     {
                         'amount': amount,
                         "container_id": container_id,
                         "product_id": product_id
                     },
                     {'id': limit[0]}
                     )
    else:
        insert_value(LIMIT, {
            'amount': amount,
            "container_id": container_id,
            "product_id": product_id
        },)


def update_instance(id, user_name, data):
    instances = get_table(Tables.INSTANCE)
    instance = next((x for x in instances if x[0] == id), None)

    data["date"] = "'%s'" % datetime.now()
    data["editor"] = "'%s'" % user_name

    if not amount:
        delete_value(Table.INSTANCE, {'id': user_data[UserDataKey.CURRENT_ID]})
    elif instance:
        update_value(Table.INSTANCE, data, {'id': id})
    else:
        insert_value(INSTANCE, data)

# def


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    insert_value('hkdb_product', {"name": "Булгур"})
