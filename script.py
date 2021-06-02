import time
import os
import configparser
import math
from datetime import datetime
from binance.client import Client

# reads the configuration from settings file
config = configparser.ConfigParser()
config_file = os.path.join(os.path.dirname(__file__), 'config.ini') 
try:
    config.read(config_file)
except:
    print('Error! Please make sure that "config.ini" file exists and properly set.')
    exit(1)

API_KEY = config['api']['API_KEY']
API_SECRET = config['api']['API_SECRET']
TARGET_COIN = config['target']['COIN']
TARGET_DURATION = int(config['target']['DURATION'])

# MAX or number
TARGET_LOT = config['target']['LOT']

# at least buy X amount of lot in single purchase
MIN_LOT = int(config['target']['MIN_LOT'])

LOOP_SEC = int(config['general']['LOOP_SEC'])
client = Client(API_KEY, API_SECRET)

while(True):

    asset_balance = client.get_asset_balance(asset=TARGET_COIN)

    free = asset_balance.get('free', None)
    free_balance = float(free)

    if free_balance > 0:
        print(datetime.now(), '|', TARGET_COIN, free_balance)

        projects = client.get_fixed_activity_project_list(
                            type='CUSTOMIZED_FIXED',
                            status='SUBSCRIBABLE',
                            timestamp=time.time()
                            )

        for project in projects:
            status = project.get('status', None)
            asset = project.get('asset', None)
            duration = project.get('duration', None)
            lotSize = project.get('lotSize', None)

            if asset == TARGET_COIN and status == 'PURCHASING' and int(duration) == TARGET_DURATION:
                lotsPurchased = project.get('lotsPurchased', None)
                lotsUpLimit = project.get('lotsUpLimit', None)
                maxLotsPerUser = project.get('maxLotsPerUser', None)
                projectId = project.get('projectId', None)

                print(duration, lotsPurchased, lotsUpLimit, maxLotsPerUser, projectId)

                purchase_availability = lotsUpLimit - lotsPurchased
                balance_lot = free_balance / int(lotSize)
                balance_lot = math.floor(balance_lot)
                print('purchase_availability', purchase_availability, 'balance_lot', balance_lot)

                if purchase_availability > 0:

                    if balance_lot < MIN_LOT or purchase_availability < MIN_LOT:
                        continue

                    if purchase_availability > balance_lot:

                        if TARGET_LOT == 'MAX':
                            lot = balance_lot
                        else:
                            lot = int(TARGET_LOT)
                    else:
                        lot = purchase_availability

                    params = {
                        'projectId': projectId,
                        'lot': lot,
                        'timestamp': time.time()
                    }

                    print("Purchase it!")
                    purchase = client._request_margin_api('post', 'lending/customizedFixed/purchase',
                                        True, data=params)

    time.sleep(LOOP_SEC)