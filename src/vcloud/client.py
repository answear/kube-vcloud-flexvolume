from threading import local
ctx = local()

from vcloud.config import Config
config = Config.read()
ctx.config = config

from pyvcloud.vcd.client import Client, BasicLoginCredentials
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcloudair import VCA
import requests
import pprint

def login(session_id=None):
    client = Client(config['host'],
                    api_version=config['api_version'],
                    verify_ssl_certs=config['verify_ssl_certs'])

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
        ctx.vca = VCA(host=config['host'],
                      username=config['username'],
                      service_type='vcd',
                      version=config['api_version'],
                      verify=config['verify_ssl_certs'],
                      log=config['log'])
        ctx.vca.login(password=config['password'], org=config['org'], org_url=org_url)
        ctx.vca.login(token=ctx.vca.token, org=config['org'], org_url=ctx.vca.vcloud_session.org_url)
    except Exception as e:
        return False
    return True

def logout():
    try:
        client = ctx.client
        client.logout()
        vca = ctx.vca
        vca.logout()
    except Exception as e:
        return False
    return True
