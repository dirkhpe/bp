"""
This script will collect all connections data from connections excel and load it in Neo4J database.
"""

import logging

from connections.lib import my_env
from connections.lib import get_servers
from connections.lib.neostore import NeoStore
from openpyxl import load_workbook

nodes = {}
rels = []
dev_not_found = []
sd = {}


def get_device_attribs(server):
    try:
        return dict(
            category=sd[server]["category"],
            subCategory=sd[server]["subCategory"],
            classification=sd[server]["classification"],
            lifeCycleState= sd[server]["lifeCycleState"]
        )
    except KeyError:
        return dict()


def get_device_info(asset, device):
    """
    This method will find a valid server name and server attributes.
    If asset name is null, then device name will be selected.
    If asset name does not return attributes, then try with device name.

    :param asset:

    :param device:

    :return: name, attributes
    """
    dev_name = asset
    if not dev_name:
        dev_name = device
    device_attribs = get_device_attribs(dev_name)
    if not device_attribs:
        if dev_name != device:
            device_attribs = get_device_attribs(device)
    if not device_attribs:
        if "PP" not in dev_name[:len("PP")]:
            # Error message only if device does not start with "PP" (Patch Panel)
            if dev_name not in dev_not_found:
                logging.error("Device {s} not in server table".format(s=dev_name))
                dev_not_found.append(dev_name)
    return dev_name, device_attribs


def handle_relation(from_node, from_key, to_node, to_key, reltype):
    """
    This method will check if a directional relation does exist already.
    If not, it will be created.

    :param from_node:

    :param from_key:

    :param to_node:

    :param to_key:

    :param reltype:

    :return:
    """
    rel_key = "{f} {t}".format(f=from_key, t=to_key)
    logging.debug("Relation key: {rk}".format(rk=rel_key))
    if rel_key not in rels:
        # Relation does not exist, create it
        ns.create_relation(from_node, reltype, to_node)
        # Remember that the relation does exist
        rels.append(rel_key)
    return


def handle_node(node_name, node_label, **attribs):
    """
    This method will handle a node. It will get a node name and label. If the node does not exist yet, it will be
    created.
    The node is returned to the calling application.
    If name is not defined, then FALSE is returned

    :param node_name:

    :param node_label:

    :return: The Neo4J node - or False if name is not defined.
    """
    if node_name:
        node_key = "{l} {n}".format(l=node_label, n=node_name)
        try:
            return nodes[node_key]
        except KeyError:
            # building node does not exist, create one
            if attribs:
                attribs["name"] = str(name)
            else:
                attribs = dict(
                    name=str(name)
                )
            nodes[node_key] = ns.create_node(label, **attribs)
        return nodes[node_key]
    else:
        return False


if __name__ == "__main__":
    cfg = my_env.init_env("connections", __file__)
    # Get Neo4J Connection and clean Database
    ns = NeoStore(cfg, refresh="Yes")
    # get device information
    sd = get_servers.get_servers(cfg['Main']['servers'])
    # Get the connections workbook
    wb = load_workbook(cfg['Main']['connections'], read_only=True)
    sheet = wb['Sheet1']
    # Get worksheet data as a list of rows
    row_list = list(sheet.rows)
    # Get title row in a named row (nr) to handle all data rows as dictionaries
    title_row = row_list.pop(0)
    nr = my_env.get_named_row("connections", title_row)
    # Then handle each record in the sheet
    loop = my_env.LoopInfo("connections", 100)
    for row in map(nr._make, row_list):
        # first get location
        label = "building"
        name = row.SOURCE_BUILDING.value
        building_node = handle_node(name, label)
        building_key = "{l} {n}".format(l=label, n=name)
        # Get rack
        label = "rack"
        name = row.SOURCE_RACK.value
        rack_node = handle_node(name, label)
        rack_key = "{l} {n}".format(l=label, n=name)
        if rack_node:
            handle_relation(rack_node, rack_key, building_node, building_key, "location")
        # Get device
        label = "device"
        name, device_attribs = get_device_info(row.SOURCE_ASSET_NUMBER.value, row.SOURCE_DEVICE_NAME.value)
        device_node = handle_node(name, label, **device_attribs)
        device_key = "{l} {n}".format(l=label, n=name)
        if rack_node:
            handle_relation(device_node, device_key, rack_node, rack_key, "in")
        else:
            handle_relation(device_node, device_key, building_node, building_key, "location")
        # Then handle port
        label = "port"
        # Port name needs to be attached to device name
        portname = row.SOURCE_PORT_LONG_NAME.value
        name = "{d} {p}".format(d=name, p=portname)
        port_attribs = dict(
            port=portname
        )
        source_port_node = handle_node(name, label, **port_attribs)
        source_port_key = "{l} {n}".format(l=label, n=name)
        handle_relation(source_port_node, source_port_key, device_node, device_key, "from")
        # Get destination rack
        label = "rack"
        name = row.DESTINATION_RACK.value
        rack_node = handle_node(name, label)
        rack_key = "{l} {n}".format(l=label, n=name)
        if rack_node:
            handle_relation(rack_node, rack_key, building_node, building_key, "location")
        # Get destination device
        label = "device"
        name, device_attribs = get_device_info(row.DESTINATION_ASSET_NUMBER.value, row.DESTINATION_DEVICE_NAME.value)
        device_node = handle_node(name, label, **device_attribs)
        device_key = "{l} {n}".format(l=label, n=name)
        if rack_node:
            handle_relation(device_node, device_key, rack_node, rack_key, "in")
        else:
            handle_relation(device_node, device_key, building_node, building_key, "location")
        # Then handle destination port
        label = "port"
        # Port name needs to be attached to device name
        # One single port has date as value, convert to string...
        portname = str(row.DESTINATION_PORT_LONG_NAME.value)
        name = "{d} {p}".format(d=name, p=portname)
        port_attribs = dict(
            port=portname
        )
        destination_port_node = handle_node(name, label, **port_attribs)
        destination_port_key = "{l} {n}".format(l=label, n=name)
        handle_relation(destination_port_node, destination_port_key, device_node, device_key, "from")
        handle_relation(source_port_node, source_port_key, destination_port_node, destination_port_key, "to")
        loop.info_loop()
    loop.end_loop()
    logging.info('End Application')
