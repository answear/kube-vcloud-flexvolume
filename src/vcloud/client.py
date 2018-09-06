import requests

from threading import local
ctx = local()

from vcloud.config import Config
config = Config.read()
ctx.config = config

from pyvcloud.vcd.client import Client, BasicLoginCredentials
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC

def login(session_id=None):
    log_requests = True if config['log'] == True else False
    log_headers = True if config['log'] == True else False
    log_bodies = True if config['log'] == True else False

    client = Client(config['host'],
                    api_version=config['api_version'],
                    verify_ssl_certs=config['verify_ssl_certs'],
                    log_file=config['log_file'],
                    log_requests=log_requests,
                    log_headers=log_headers,
                    log_bodies=log_bodies)

    if not config['verify_ssl_certs']:
        requests.packages.urllib3.disable_warnings()

    try:
        if session_id is not None:
            client.rehydrate_from_token(session_id)
        else:
            client.set_credentials(BasicLoginCredentials(
                    config['username'],
                    config['org'],
                    config['password']))

        logged_in_org = client.get_org() 
        org = Org(client, resource=logged_in_org)
        org_url = "https://%s/cloud/org/%s" % (config['host'], logged_in_org)
        the_vdc = org.get_vdc(config['vdc'])

        # Set contextual data:
        ctx.client = client
        ctx.vdc = VDC(client, href=the_vdc.get('href'))
        ctx.token = client._session.headers['x-vcloud-authorization']
    except Exception as e:
        if config['debug'] == True:
            print("Exception: {}\n".format(e))
        return False
    return True

def logout():
    try:
        client = ctx.client
        client.logout()
    except Exception as e:
        if config['debug'] == True:
            print("Exception: {}\n".format(e))
        return False
    return True
