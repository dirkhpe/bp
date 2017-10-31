"""
The purpose of this file is to read the servers information and remember fields required for Neo4J property in a hash.
"""
import logging
from connections.lib import my_env
from openpyxl import load_workbook


def handle_servers(worksheet):
    """
    This function will handle the worksheet

    :param worksheet: worksheet object.

    :return: Dictionary with servernames as key and attributes is dictionary with server properties.
    """
    logging.info("Collect servers information")
    # Convert worksheet info to the list of rows
    row_list = list(worksheet.rows)
    # Get name tuple from title row
    title_row = row_list.pop(0)
    nr = my_env.get_named_row("Serversheet", title_row)
    loop = my_env.LoopInfo("servers", 1000)
    server = {}
    for row in map(nr._make, row_list):
        attribs = dict(
            classification=row.classification.value,
            category=row.category.value,
            subCategory=row.subCategory.value,
            lifeCycleState=row.lifeCycleState.value
        )
        server[row.serverId.value] = attribs
        loop.info_loop()
    loop.end_loop()
    return server


def get_servers(serverpath):
    wb = load_workbook(serverpath, read_only=True)
    server = handle_servers(worksheet=wb['servers'])
    return server


if __name__ == "__main__":
    server_dict = get_servers("c:\\development\\python\\bpost\\connections\\data\\servers.xlsx")
    for k in server_dict:
        for p in server_dict[k]:
            # print("Server: {s} Attribute {p} has value {v}".format(s=k, p=p, v=server[k][p]))
            pass
