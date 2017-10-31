"""
This procedure will rebuild the sqlite inventory database
"""

import logging
from Peregrine.lib import my_env
from Peregrine.lib import sqlitestore

cfg = my_env.init_env("peregrine", __file__)
logging.info("Start application")
inv = sqlitestore.DirectConn(cfg)
inv.rebuild()
logging.info("sqlite inventory rebuild")
logging.info("End application")