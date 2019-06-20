import asana

import os
import json

def create_task():
    if 'ASANA_ACCESS_TOKEN' in os.environ:
        client = asana.Client.access_token(os.environ['ASANA_ACCESS_TOKEN'])
