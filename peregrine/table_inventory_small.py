"""
This script will collect information from a table. The purpose is to add all readable information from a table
in a flat structure to make it searchable.
"""

from Peregrine.lib import my_env
from Peregrine.lib import mssqlstore
from Peregrine.lib import sqlitestore
from Peregrine.lib.sqlitestore import *


cfg = my_env.init_env("peregrine", __file__)
logging.info("Start application")
# Init database
ms = mssqlstore.DataStore(cfg)
ds = sqlitestore.DirectConn(cfg)
sq = sqlitestore.init_session(cfg['Main']['inv_db'])

tn_res = ["DEVICEM1", "deviceparentm1", "devtypem1"]
for tn in tn_res:
    info_loop = my_env.LoopInfo(tn, 50)
    fieldnames = ms.get_fields(tn)
    fieldstr = ", ".join(fieldnames)
    query = "SELECT {fs} FROM {tn}".format(fs=fieldstr, tn=tn)
    res = ms.res_query(query)
    cnt = 0
    for rec in res:
        info_loop.info_loop()
        cnt += 1
        for field in fieldnames:
            if rec[field]:
                params = dict(
                    tablename=tn,
                    recnr=cnt,
                    fieldname=field,
                    value=rec[field]
                )
                recdata = Recdata(**params)
                sq.add(recdata)
        sq.commit()
    info_loop.end_loop()
ms.close()
logging.info("End application")
