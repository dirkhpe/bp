"""
This script will collect information from a table. The purpose is to add all readable information from a table
in a flat structure to make it searchable.
"""

from Peregrine.lib import my_env
from Peregrine.lib import mssqlstore
from Peregrine.lib import sqlitestore
from Peregrine.lib.sqlitestore import *
from sqlalchemy.orm.exc import NoResultFound


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
query = """
SELECT name
FROM table_inv
WHERE name like 'bpg%'
  AND (rows < 200000)
  AND not (name like 'bpgact%')
  AND not (name like 'bpgapproval%')
"""
tn_res = ds.res_query(query)
for tn_rec in tn_res:
    tn = tn_rec['name']
    print("Tablename: {tn}".format(tn=tn))
    # Check TableName not in table_names
    dummyres = sq.query(TableName).filter_by(name=tn).first()
    if not dummyres:
        # OK, table not processed.
        # Add table to table_names, Get table_id
        table_name = TableName(
            name=tn
        )
        sq.add(table_name)
        sq.commit()
        sq.refresh(table_name)
        table_id = table_name.id

        info_loop = my_env.LoopInfo(tn, 50)
        fieldids = {}
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
                    # First get Field ID
                    if field not in fieldids:
                        # New field, add to table field_names
                        field_data = FieldName(
                            table_id=table_id,
                            fieldname=field
                        )
                        sq.add(field_data)
                        sq.commit()
                        sq.refresh(field_data)
                        fieldids[field] = field_data.id
                    params = dict(
                        recnr=cnt,
                        field_id=fieldids[field],
                        value=rec[field]
                    )
                    recdata = Recdata(**params)
                    sq.add(recdata)
            sq.commit()
        info_loop.end_loop()
ms.close()
logging.info("End application")
