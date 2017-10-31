"""
This script will search for specific strings in the database.
"""

from Peregrine.lib import my_env
from Peregrine.lib import mssqlstore
from Peregrine.lib import sqlitestore
from Peregrine.lib.sqlitestore import *
# from sqlalchemy.orm.exc import NoResultFound


cfg = my_env.init_env("peregrine", __file__)
logging.info("Start application")
# Init database
ms = mssqlstore.DataStore(cfg)
ds = sqlitestore.DirectConn(cfg)
sq = sqlitestore.init_session(cfg['Main']['inv_db'])

"""
query = 
SELECT name 
FROM table_inv 
WHERE ((name like 'dev%') or (name like 'ci%') or (name like 'bpgci%')) 
  AND (rows > 1)
"""
"""
query = 
SELECT name
FROM table_inv
WHERE name like 'bpg%'
  AND (rows < 200000)
  AND not (name like 'bpgact%')
  AND not (name like 'bpgapproval%')
"""
query = """
SELECT name 
FROM table_inv
where (rows > 1) AND (rows < 1000000)
AND name > 'probsummarym1'
order by name
"""
tn_res = ds.res_query(query)
strfound = []
searcharray = ["Twinax", "FR144142"]
for tn_rec in tn_res:
    tn = tn_rec['name']
    print("Tablename: {tn}".format(tn=tn))
    # Check TableName not in table_names
    dummyres = sq.query(TableName).filter_by(name=tn).first()
    if not dummyres:
        # OK, table not processed.
        info_loop = my_env.LoopInfo(tn, 50)
        fieldnames = ms.get_fields(tn)
        if len(fieldnames) > 0:
            fieldstr = ", ".join(fieldnames)
            query = "SELECT {fs} FROM {tn}".format(fs=fieldstr, tn=tn)
            res = ms.res_query(query)
            cnt = 0
            for rec in res:
                info_loop.info_loop()
                cnt += 1
                for field in fieldnames:
                    if rec[field]:
                        for searchstr in searcharray:
                            searchres = "{t}-{f}-{s}".format(t=tn, f=field, s=searchstr)
                            if searchres not in strfound:
                                if searchstr in rec[field]:
                                    msg = "Found {s} in Table {t} on Field {f}".format(s=searchstr, t=tn, f=field)
                                    logging.info(msg)
                                    print(msg)
                                    strfound.append(searchres)
        info_loop.end_loop()
ms.close()
logging.info("End application")
