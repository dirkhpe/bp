"""
This script will collect inventory information from Peregrine.
"""

from Peregrine.lib import my_env
from Peregrine.lib import mssqlstore
from Peregrine.lib import sqlitestore
from Peregrine.lib.sqlitestore import *


cfg = my_env.init_env("peregrine", __file__)
logging.info("Start application")
# Init database
ms = mssqlstore.DataStore(cfg)
sq = sqlitestore.init_session(cfg['Main']['inv_db'])

# Get inventory of the table names in schema dbo
query = "select table_name from INFORMATION_SCHEMA.TABLES where TABLE_TYPE = 'BASE TABLE' and TABLE_SCHEMA = 'dbo'" \
        "order by table_name"
res = ms.res_query(query)
inv_loop = my_env.LoopInfo("Table Inventory", 20)
for rec in res:
    # query = "select count(*) as cnt from {t}".format(t=rec['table_name'])
    query = "sp_spaceused '{t}'".format(t=rec['table_name'])
    table_rec = ms.res_query(query)[0]
    # cnt_rec = cnt_res[0]['cnt']
    params = dict(
        name=table_rec['name'],
        rows=table_rec['rows'],
        reserved=table_rec['reserved'][:-3],
        data=table_rec['data'][:-3],
        index_size=table_rec['index_size'][:-3],
        unused=table_rec['unused'][:-3]
    )
    table_inv = Table(**params)
    sq.add(table_inv)
    inv_loop.info_loop()
inv_loop.end_loop()
sq.commit()

ms.close()
logging.info("End application")
