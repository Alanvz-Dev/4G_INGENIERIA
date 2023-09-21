import random

from xmlrpc import client as xmlrpc_client


from .timeout_transport import TimeoutTransport
username = ODOO_USERNAME = 'admin'  
password = PASSWORD = 'Gacl751001E85+'
url = ODOO_URL = 'http://odoo.4gingenieria.com/' 
timeout_transport = TimeoutTransport()
timeout_transport.set_timeout(20.0)



def get_models(url):
    return xmlrpc_client.ServerProxy('{}xmlrpc/2/object'.format(url),transport=timeout_transport)

def get_common(url):
    return xmlrpc_client.ServerProxy('{}xmlrpc/2/common'.format(url),transport=timeout_transport)


def get_uid(db,url):
    return get_common(url).authenticate(db, username, password, {})



def generate_barcode(db,url,contract_id):
    get_models(url).execute_kw(db, get_uid(db,url), password, 'hr.contract', 'write', [[contract_id], {'dinning_service_barcode': str(random.randint(111111111111, 999999999999))}])

def get_contract_name(db,url):
    lst = list()
    contract_ids = get_models(url).execute_kw(db, get_uid(db,url), password,'hr.contract','search_read',[[('state', 'in', ['open']),('employee_id', '!=',False)]],{'fields': ['name','dinning_service_barcode'],'order': 'name asc'})
    for contract in contract_ids:
        if contract['dinning_service_barcode'] == '' or contract['dinning_service_barcode'] == False:
            generate_barcode(db,url,contract['id'])
        lst.append((contract['id'], str(contract['name']+'/'+db)))
    return lst



