import os
from datetime import datetime
import requests
import json
from web3 import Web3
import shutil
import glob
import pandas as pd
import subprocess
import time
import re
import eth_abi
import psutil
import ast
import sys

import platform
if platform.system() == 'Windows':
    import wexpect as uniexpect
else:
    import pexpect as uniexpect


from fastlane_bot.data.abi import CARBON_CONTROLLER_ABI, UNISWAP_V3_POOL_ABI, UNISWAP_V2_POOL_ABI, PANCAKESWAP_V3_POOL_ABI, PANCAKESWAP_V2_POOL_ABI

from dotenv import load_dotenv
load_dotenv()

binance14 = "0x28C6c06298d514Db089934071355E5743bf21d60"

def create_new_testnet(blockchain):

    # Replace these variables with your actual data
    ACCOUNT_SLUG = os.environ['TENDERLY_USER'] 
    PROJECT_SLUG = os.environ['TENDERLY_PROJECT'] 
    ACCESS_KEY = os.environ['TENDERLY_ACCESS_KEY']

    url = f'https://api.tenderly.co/api/v1/account/{ACCOUNT_SLUG}/project/{PROJECT_SLUG}/testnet/container'

    headers = {
        'Content-Type': 'application/json',
        'X-Access-Key': ACCESS_KEY
    }

    if blockchain=='ethereum':
        networkId = 1
        chainId = 1
    elif blockchain == 'coinbase_base':
        networkId = 8453
        chainId = 8453
    else:
        raise ValueError("Blockchain not supported")

    data = {
        "slug": f"testing-api-endpoint-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "displayName": "Automated Test Env",
        "description": "",
        "visibility": "TEAM",
        "tags": {
            "purpose": "development"
        },
        "networkConfig": {
            "networkId": f"{networkId}",
            "blockNumber": "latest",
            "baseFeePerGas": "1",
            "chainConfig": {
                "chainId": f"{chainId}"
            }
        },
        "private": True,
        "syncState": False,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(response.text)

    uri = f"{response.json()['container']['connectivityConfig']['endpoints'][0]['uri']}"
    fromBlock = int(response.json()['container']['networkConfig']['blockNumber'])

    return uri

def get_GenericEvents(w3, ContractObject, EventName, fromBlock):
    logList = getattr(ContractObject.events, EventName).get_logs(fromBlock=fromBlock)
    data = []
    for log in logList:
        log_data = {
            'blockNumber': log['blockNumber'],
            'transactionHash': w3.to_hex(log['transactionHash']),
            **log['args']
        }
        if "order0" in log['args'].keys():
            order0_dict = dict()
            for key, value in log['args']["order0"].items():
                order0_dict[key + '0'] = value
            log_data.update(order0_dict)
            del log_data["order0"]
        if "order1" in log['args'].keys():
            order1_dict = dict()
            for key, value in log['args']["order1"].items():
                order1_dict[key + '1'] = value
            log_data.update(order1_dict)
            del log_data["order1"]
        data.append(log_data)

    mdf = pd.DataFrame(data)
    if 'blockNumber' in mdf.columns:
        mdf.sort_values(by='blockNumber', inplace=True)
    mdf.reset_index(inplace=True, drop=True)
    return(mdf)
    
def createStrategy_fromTestDict(w3, CarbonController, test_strategy):
    (token0, token1, y0, z0, A0, B0, y1, z1, A1, B1, wallet) = (
        test_strategy['token0'],
        test_strategy['token1'],
        test_strategy['y0'],
        test_strategy['z0'],
        test_strategy['A0'],
        test_strategy['B0'],
        test_strategy['y1'],
        test_strategy['z1'],
        test_strategy['A1'],
        test_strategy['B1'],
        test_strategy['wallet']
        )
    print("Funding Wallet....")
    setBalance_via_faucet(w3, token0, int(y0*2), wallet)
    setBalance_via_faucet(w3, token1, int(y1*2), wallet)

    print("Creating Strategy...")
    nonce = w3.eth.get_transaction_count(wallet)
    if token0 == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
        value = y0
        function_call = CarbonController.functions.createStrategy(token0, token1, ([y0, z0, A0, B0], [y1, z1, A1, B1])).transact({
            "gasPrice": 0,
            "gas": 2000000,
            "from": wallet,
            "nonce": nonce,
            "value": value
        })
    elif token1 == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
        value = y1
        function_call = CarbonController.functions.createStrategy(token0, token1,([y0, z0, A0, B0], [y1, z1, A1, B1])).transact({
            "gasPrice": 0,
            "gas": 2000000,
            "from": wallet,
            "nonce": nonce,
            "value": value
        })
    else:
        function_call = CarbonController.functions.createStrategy(token0, token1, ([y0, z0, A0, B0], [y1, z1, A1, B1])).transact({
            "gasPrice": 0,
            "gas": 2000000,
            "from": wallet,
            "nonce": nonce,
        })
    
    tx_reciept = w3.eth.wait_for_transaction_receipt(function_call)    
    tx_hash = w3.to_hex(dict(tx_reciept)['transactionHash'])
    
    if dict(tx_reciept)['status'] != 1:
        print('Creation Failed')
        # print(f'tx_hash = {tx_hash}')
        return(None)
    else:
        print(f'Successfully Created Strategy')
        # print(f'tx_hash = {tx_hash}')
        return(tx_hash)

def deleteStrategy(w3, CarbonController, id, owner):
    print("Deleting Strategy...")
    nonce = w3.eth.get_transaction_count(owner)
    function_call = CarbonController.functions.deleteStrategy(id).transact({
        "gasPrice": 0,
        "gas": 2000000,
        "from": owner,
        "nonce": nonce,
    })
    
    tx_reciept = w3.eth.wait_for_transaction_receipt(function_call)    
    if dict(tx_reciept)['status'] != 1:
        return(dict(tx_reciept)['status'])
    else:
        return(dict(tx_reciept)['status'])
    
def get_state_of_carbon_strategies(w3, CarbonController, fromBlock):
    strategy_created_df = get_GenericEvents(w3=w3, ContractObject=CarbonController, EventName="StrategyCreated", fromBlock=fromBlock)
    if len(strategy_created_df) > 0:
        all_carbon_strategies = [(strategy_created_df["id"][i],strategy_created_df["owner"][i]) for i in strategy_created_df.index]
    else:
        all_carbon_strategies = []
    print(f"{len(all_carbon_strategies)} Carbon strategies have been created")

    strategy_deleted_df = get_GenericEvents(w3=w3, ContractObject=CarbonController, EventName="StrategyDeleted", fromBlock=fromBlock)
    if len(strategy_deleted_df) > 0:
        deleted_strategies = strategy_deleted_df["id"].to_list()
    else:
        deleted_strategies = []
    print(f"{len(deleted_strategies)} Carbon strategies have been deleted")

    if all_carbon_strategies != []:
        remaining_carbon_strategies = [x for x in all_carbon_strategies if x[0] not in deleted_strategies]
    else:
        remaining_carbon_strategies = []
    print(f"{len(remaining_carbon_strategies)} Carbon strategies remain")

    return strategy_created_df, strategy_deleted_df, remaining_carbon_strategies

def delete_all_carbon_strategies(w3, CarbonController, blockchain, carbon_strategy_id_owner_list):
    print("Deleting strategies...")
    if blockchain == 'ethereum':
        modify_tokens_for_deletion(w3, CarbonController)
    undeleted_strategies = []
    for id,owner in carbon_strategy_id_owner_list:
        print("Attempt 1")
        status = deleteStrategy(w3, CarbonController, id, owner)
        if status == 0:
            try:
                strat_info = CarbonController.functions.strategy(id).call()
                current_owner = strat_info[1]
                try:
                    print("Attempt 2")
                    status = deleteStrategy(w3, CarbonController, id, current_owner)
                    if status == 0:
                        print(f"Unable to delete strategy {id}")
                        undeleted_strategies += [id]
                except:
                    print(f"Strategy {id} not found - already deleted")
            except:
                print(f"Strategy {id} not found - already deleted")
                pass
        elif status==1:
            print(f"Strategy {id} successfully deleted")
        else:
            print("Possible error")
    return undeleted_strategies

# Set the eth or token balance of any address (TestNet feature)
def setBalance_via_faucet(w3, tokenAddress, amountWei, wallet):
    wallet = w3.to_checksum_address(wallet)
    if tokenAddress in ['0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE']:
        params = [[wallet], w3.to_hex(amountWei)]
        w3.provider.make_request(method='tenderly_setBalance', params=params)
    else:
        params = [tokenAddress, wallet, w3.to_hex(amountWei)]
        w3.provider.make_request(method='tenderly_setErc20Balance', params=params)
    print(f"Reset Balance to {amountWei}")

def get_token_approval(w3, tokenAddress, approval_address, my_address):
    if tokenAddress in ["0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"]:
        return None
    my_address = w3.to_checksum_address(my_address)
    approval_address = w3.to_checksum_address(approval_address)
    tokenAddress = w3.to_checksum_address(tokenAddress)
    token_contract = w3.eth.contract(address = tokenAddress, abi = erc20_abi)
    if tokenAddress in ['0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C','0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48','0xdAC17F958D2ee523a2206206994597C13D831ec7']: # first approve BNT with 0
        nonce = w3.eth.get_transaction_count(my_address)

        function_call = token_contract.functions.approve(approval_address, 0).transact({ 
            "gasPrice": 0,
            "gas": 2000000,
            "from": my_address,
            "nonce": nonce,
        })
        tx_reciept = w3.eth.wait_for_transaction_receipt(function_call)    
        tx_hash = w3.to_hex(dict(tx_reciept)['transactionHash'])

        if dict(tx_reciept)['status'] != 1:
            print('Approval Failed')
            print(f'tx_hash = {tx_hash}')
        else:
            print(f'Successfully Approved for 0')
            print(f'tx_hash = {tx_hash}')    
    else:
        pass
    nonce = w3.eth.get_transaction_count(my_address)
    function_call = token_contract.functions.approve(approval_address, 115792089237316195423570985008687907853269984665640564039457584007913129639935).transact({ 
        "gasPrice": 0,
        "gas": 2000000,
        "from": my_address,
        "nonce": nonce,
    })
    tx_reciept = w3.eth.wait_for_transaction_receipt(function_call)    
    tx_hash = w3.to_hex(dict(tx_reciept)['transactionHash'])

    if dict(tx_reciept)['status'] != 1:
        print('Approval Failed')
        print(f'tx_hash = {tx_hash}')
    else:
        print(f'Successfully Approved Token for Unlimited')
        print(f'tx_hash = {tx_hash}')    
    
    return()

def get_tx_data(strategy_id, txt_all_successful_txs):
    '''this only handles one tx found'''
    for tx in txt_all_successful_txs:
        if str(strategy_id) in tx:
            tx_data = json.loads(tx.split("\n\n")[-1])
            return tx_data
        
# clean cid0 out since this is unique and depends on the history of the carbon deployment
def clean_tx_data(tx_data):
    for trade in tx_data['trades']:
        if trade['exchange'] == 'carbon_v1' and 'cid0' in trade:
            del trade['cid0']
    return tx_data

def appendZeros(value, type_a):
    if (type_a == 'bool') and (value == 'True'):
        return '0001'
    elif (type_a == 'bool') and (value == 'False'):
        return '0000'
    elif type_a == 'int24':
        long_hex = eth_abi.encode(['int24'], [value]).hex()
        return long_hex[-6:]
    else:
        try:
            hex_value = hex(value)[2:]
            length = int(re.search(r'\d+', type_a).group()) // 4
            result = '0' * (length - len(hex_value)) + hex_value
        except Exception as e:
            print(f'Error building appendZeros {str(e)}')
        return result

def build_type_val_dict(w3, test_pools_row, param_list_single):
    type_val_dict = {}
    for param in param_list_single:
        # will pick up the correct type for given param
        if param in ["blockTimestampLast"]:
            try:
                type_val_dict[param] = {
                    'type': test_pools_row[f'param_{param}_type'], 
                    'value': int(w3.eth.get_block('latest')['timestamp'])
                }
            except:
                print(f"Error building type_val_dict, type: {test_pools_row[f'param_{param}_type']}, value: fetching timestamp")
        elif param in ["unlocked"]:
            try:
                type_val_dict[param] = {
                    'type': test_pools_row[f'param_{param}_type'], 
                    'value': test_pools_row[f'param_{param}']
                }
            except:
                print(f"Error building type_val_dict, type: {test_pools_row[f'param_{param}_type']}, value: {test_pools_row[f'param_{param}']}")
        else:
            try:
                type_val_dict[param] = {
                    'type': test_pools_row[f'param_{param}_type'], 
                    'value': int(test_pools_row[f'param_{param}'])
                }
            except:
                print(f"Error building type_val_dict, type: {test_pools_row[f'param_{param}_type']}, value: {test_pools_row[f'param_{param}']}")
    
    # encode params
    try:
        result = ''.join(appendZeros(type_val_dict[arg]['value'], type_val_dict[arg]['type']) for arg in param_list_single)
        encoded_params = '0x' + '0'*(64-len(result)) + result
    except:
        print(f"Error encoding params: {type_val_dict}")
    return type_val_dict, encoded_params

def get_update_params_dict(w3, test_pools_row, slots, param_lists):
    params_dict = {}
    for i in range(len(slots)):
        params_dict[slots[i]] = {}
        params_dict[slots[i]]['slot'] = '0x'+appendZeros(int(slots[i]), 'uint256')

        type_val_dict, encoded_params = build_type_val_dict(w3, test_pools_row, param_list_single=param_lists[i])
        
        params_dict[slots[i]]['type_val_dict'] = type_val_dict
        params_dict[slots[i]]['encoded_params'] = encoded_params
        print(params_dict)
    return params_dict

def setStorageAt(w3, pool_address, update_params_dict_single):
    params = [
    pool_address,
    update_params_dict_single['slot'],
    update_params_dict_single['encoded_params']
    ]
    w3.provider.make_request(method='tenderly_setStorageAt', params=params)
    print(f"setStorageAt {pool_address}, {update_params_dict_single['slot']}")

def initialize_bot(blockchain, arb_mode, static_pool_data_FORTESTING, python_instance='python', rpc=None, terminate_other_bots=False):

    # Check to see if unexpected instances of the bot are running
    bot_counts = count_process_instances('main.py')

    # If unexpected bots are running terminate them
    if bot_counts != 0:
        print('Other Bot Instances Found - ensure they are not on the same testnet')
        if terminate_other_bots:
            print("Terminating other bot instances")
            terminate_process_instances('main.py')
            print('Bots terminated')

    # set defaults
    if blockchain is None:
        blockchain = 'ethereum'
    if arb_mode is None:
        arb_mode ='multi'
    if static_pool_data_FORTESTING is None:
        static_pool_data_FORTESTING = 'static_pool_data_testing'

    # build command
    cmd = [
    f"{python_instance}",
    "main.py",
    "--loglevel=DEBUG",
    f"--arb_mode={arb_mode}",
    "--default_min_profit_gas_token=0.002",
    "--alchemy_max_block_fetch=10",
    f"--blockchain={blockchain}",
    "--randomizer=1",
    "--backdate_pools=True",
    f"--static_pool_data_filename={static_pool_data_FORTESTING}",
    "--reorg_delay=0",
    "--polling_interval=0",
    f"--rpc_url={rpc}",
    "--read_only=False",
    ]
    

    # Join the command list into a single string
    command_string = ' '.join(cmd)

    # Execute the command in the background
    child = uniexpect.spawn(command_string)

    # ALTERNATIVELY to Execute the command in a new command prompt window
    # subprocess.Popen(f"start cmd /k \"{command_string}\"", shell=True)
    # result = subprocess.run(cmd, text=True, capture_output=True, check=True, timeout=180)

    print("Arb Bot Initialized")
    return child

def initialize_bot_new(click_options, terminate_other_bots=False):

    # Check to see if unexpected instances of the bot are running
    bot_counts = count_process_instances('main.py')

    # If unexpected bots are running terminate them
    if bot_counts != 0:
        print('Other Bot Instances Found - ensure they are not on the same testnet')
        if terminate_other_bots:
            print("Terminating other bot instances")
            terminate_process_instances('main.py')
            print('Bots terminated')

    # Execute the command in the background
    child = uniexpect.spawn(click_options)

    print("Arb Bot Initialized")
    return child

def count_process_instances(process_name):
    count = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if cmdline is not None and process_name is in cmdline
            if proc.info['cmdline'] and process_name in proc.info['cmdline']:
                count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return count

def terminate_process_instances(process_name):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if process_name is in cmdline
            if proc.info['cmdline'] and process_name in proc.info['cmdline']:
                print(f"Terminating process {proc.pid}...")
                proc.terminate()  # Terminate the process

                # Optionally, wait for the process to ensure it's killed
                proc.wait(timeout=3)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def await_first_iteration():

    time.sleep(5)
    # Set the path to the logs directory relative to your notebook's location
    path_to_logs = "./logs/*"

    # Use glob to list all directories
    log_directories = [f for f in glob.glob(path_to_logs) if os.path.isdir(f)]

    most_recent_log_folder = log_directories[-1]
    print(f"Accessing log folder {most_recent_log_folder}")
    print("Looking for pool data file...")
    most_recent_pooldata = os.path.join(most_recent_log_folder, "latest_pool_data.json")

    while True:
        if os.path.exists(most_recent_pooldata):
            print("File found.")
            break
        else:
            print("File not found, waiting 10 seconds.")
            time.sleep(10)

    with open(most_recent_pooldata) as f:
        poolData = json.load(f)
    print("len(poolData)", len(poolData))

    return most_recent_log_folder

def handle_exchange_parameters(w3, test_pools_row):
    if test_pools_row['exchange_type'] in ["uniswap_v2",'uniswap_v3',"pancakeswap_v2",'pancakeswap_v3']:
        pool_address = test_pools_row['pool_address']
        slots = ast.literal_eval(test_pools_row['slots'])
        param_lists = ast.literal_eval(test_pools_row['param_lists'])
        
        # Set balances on pool
        setBalance_via_faucet(w3, tokenAddress=test_pools_row['tkn0_address'], amountWei=int(test_pools_row['tkn0_setBalance']), wallet=test_pools_row['pool_address'])
        setBalance_via_faucet(w3, tokenAddress=test_pools_row['tkn1_address'], amountWei=int(test_pools_row['tkn1_setBalance']), wallet=test_pools_row['pool_address'])

        # Set storage parameters
        update_params_dict = get_update_params_dict(w3, test_pools_row, slots, param_lists)
        for k,update_params_dict_single in update_params_dict.items():
            setStorageAt(w3, pool_address, update_params_dict_single)

    else:
        Exception, "exchange_type not recognized"

def modify_tokens_for_deletion(w3, CarbonController):
    '''Custom modifications to tokens to allow their deletion from Carbon'''
    #### 0x0 ####
    # modify the tax parameters of 0x0 token
    params = [
    "0x5a3e6A77ba2f983eC0d371ea3B475F8Bc0811AD5",
    "0x0000000000000000000000000000000000000000000000000000000000000006",
    '0x0000000000000000000000000000000000000000000000000000000000000001']
    w3.provider.make_request(method='tenderly_setStorageAt', params=params)
    params = [
    "0x5a3e6A77ba2f983eC0d371ea3B475F8Bc0811AD5",
    "0x0000000000000000000000000000000000000000000000000000000000000007",
    '0x0000000000000000000000000000000000000000000000000000000000000001']
    w3.provider.make_request(method='tenderly_setStorageAt', params=params)
    params = [
    "0x5a3e6A77ba2f983eC0d371ea3B475F8Bc0811AD5",
    "0x000000000000000000000000000000000000000000000000000000000000000d",
    '0x0000000000000000000000000000000000000000000000000000000000000001']
    w3.provider.make_request(method='tenderly_setStorageAt', params=params)
    # make sure there is sufficient funds for withdrawal
    setBalance_via_faucet(w3, "0x5a3e6A77ba2f983eC0d371ea3B475F8Bc0811AD5", 288551667147, CarbonController.address)
    deleteStrategy(w3, CarbonController, 9868188640707215440437863615521278132277, '0xe3d51681Dc2ceF9d7373c71D9b02c5308D852dDe')
    # modify the tax parameters of 0x0 token back to their original state
    params = [
    "0x5a3e6A77ba2f983eC0d371ea3B475F8Bc0811AD5",
    "0x0000000000000000000000000000000000000000000000000000000000000006",
    '0x0000000000000000000000000000000000000000000000000000000000000019']
    w3.provider.make_request(method='tenderly_setStorageAt', params=params)
    params = [
    "0x5a3e6A77ba2f983eC0d371ea3B475F8Bc0811AD5",
    "0x0000000000000000000000000000000000000000000000000000000000000007",
    '0x0000000000000000000000000000000000000000000000000000000000000005']
    w3.provider.make_request(method='tenderly_setStorageAt', params=params)
    params = [
    "0x5a3e6A77ba2f983eC0d371ea3B475F8Bc0811AD5",
    "0x000000000000000000000000000000000000000000000000000000000000000d",
    '0x0000000000000000000000000000000000000000000000000002386f26fc10000']
    w3.provider.make_request(method='tenderly_setStorageAt', params=params)    
    # empty out this token from Carboncontroler
    setBalance_via_faucet(w3, "0x5a3e6A77ba2f983eC0d371ea3B475F8Bc0811AD5", 0, CarbonController.address)

    #### PAXG ####
    # modify the tax parameters of PAXG token
    params = [
    "0x45804880De22913dAFE09f4980848ECE6EcbAf78",
    "0x000000000000000000000000000000000000000000000000000000000000000d",
    '0x0000000000000000000000000000000000000000000000000000000000000000']
    w3.provider.make_request(method='tenderly_setStorageAt', params=params)
    # # make sure there is sufficient funds for withdrawal
    setBalance_via_faucet(w3, "0x45804880De22913dAFE09f4980848ECE6EcbAf78", 395803389286127, CarbonController.address)
    deleteStrategy(w3, CarbonController, 15312706511442230855851857334429569515620, '0xFf365375777069eBd8Fa575635EB31a0787Afa6c')
    params = [
    "0x45804880De22913dAFE09f4980848ECE6EcbAf78",
    "0x000000000000000000000000000000000000000000000000000000000000000d",
    '0x00000000000000000000000000000000000000000000000000000000000000c8']
    w3.provider.make_request(method='tenderly_setStorageAt', params=params)
    # empty out this token from Carboncontroler
    setBalance_via_faucet(w3, "0x45804880De22913dAFE09f4980848ECE6EcbAf78", 0, CarbonController.address)


def get_balance_raw(w3, tokenAddress, address, blockNumber = None):
    if tokenAddress in ['0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee']:
        if blockNumber == None:
            return w3.eth.get_balance(address)
        else:
            return w3.eth.get_balance(address, blockNumber)
    tokenContract = w3.eth.contract(address=tokenAddress, abi=erc20_abi)
    if blockNumber == None:
        balance = tokenContract.functions.balanceOf(address).call()
    else:
        balance = tokenContract.functions.balanceOf(address).call(block_identifier = blockNumber)
    return(balance)

def run_slot_update_tests(w3, test_pools):
    global PANCAKESWAP_V2_POOL_ABI
    global PANCAKESWAP_V3_POOL_ABI
    global UNISWAP_V2_POOL_ABI
    global UNISWAP_V3_POOL_ABI
    for i in test_pools.index:
        if test_pools["exchange"][i] == 'pancakeswap_v2':
            print(f"Testing {i}")
            pool_contract = w3.eth.contract(address=test_pools["pool_address"][i], abi=PANCAKESWAP_V2_POOL_ABI)
            reserve0, reserve1, ts = [str(x) for x in pool_contract.functions.getReserves().call()]
            assert reserve0 == test_pools["param_reserve0"][i], f"Line {i} reserve0 not updated. Should be {test_pools['param_reserve0'][i]} got {reserve0}"
            assert reserve1 == test_pools["param_reserve1"][i], f"Line {i} reserve1 not updated. Should be {test_pools['param_reserve1'][i]} got {reserve1}"
            print('Test Passed')
        elif test_pools["exchange"][i] in ['uniswap_v2', 'baseswap_v2']:
            print(f"Testing {i}")
            pool_contract = w3.eth.contract(address=test_pools["pool_address"][i], abi=UNISWAP_V2_POOL_ABI)
            reserve0, reserve1, ts = [str(x) for x in pool_contract.functions.getReserves().call()]
            assert reserve0 == test_pools["param_reserve0"][i], f"Line {i} reserve0 not updated. Should be {test_pools['param_reserve0'][i]} got {reserve0}"
            assert reserve1 == test_pools["param_reserve1"][i], f"Line {i} reserve1 not updated. Should be {test_pools['param_reserve1'][i]} got {reserve1}"
            print('Test Passed')
        elif (test_pools["exchange"][i] == 'uniswap_v3'):
            print(f"Testing {i}")
            pool_contract = w3.eth.contract(address=test_pools["pool_address"][i], abi=UNISWAP_V3_POOL_ABI)
            liquidity= str(pool_contract.functions.liquidity().call())
            slot0 = pool_contract.functions.slot0().call()
            sqrtPriceX96, tick, observationIndex, observationCardinality, observationCardinalityNext, feeProtocol, unlocked = [str(x) for x in slot0]
            assert liquidity == test_pools["param_liquidity"][i], f"Line {i} liquidity not updated. Should be {test_pools['param_liquidity'][i]} got {liquidity}"
            assert sqrtPriceX96 == test_pools["param_sqrtPriceX96"][i], f"Line {i} sqrtPriceX96 not updated. Should be {test_pools['param_sqrtPriceX96'][i]} got {sqrtPriceX96}"
            assert tick == test_pools["param_tick"][i], f"Line {i} tick not updated. Should be {test_pools['param_tick'][i]} got {tick}"
            assert observationIndex == test_pools["param_observationIndex"][i], f"Line {i} observationIndex not updated. Should be {test_pools['param_observationIndex'][i]} got {observationIndex}"
            assert observationCardinality == test_pools["param_observationCardinality"][i], f"Line {i} observationCardinality not updated. Should be {test_pools['param_observationCardinality'][i]} got {observationCardinality}"
            assert observationCardinalityNext == test_pools["param_observationCardinalityNext"][i], f"Line {i} observationCardinalityNext not updated. Should be {test_pools['param_observationCardinalityNext'][i]} got {observationCardinalityNext}"
            assert feeProtocol == test_pools["param_feeProtocol"][i], f"Line {i} feeProtocol not updated. Should be {test_pools['param_feeProtocol'][i]} got {feeProtocol}"
            assert unlocked == test_pools["param_unlocked"][i], f"Line {i} feeProtocol not updated. Should be {test_pools['param_unlocked'][i]} got {unlocked}"
            print('Test Passed')
        elif (test_pools["exchange"][i] == 'pancakeswap_v3'):
            print(f"Testing {i}")
            pool_contract = w3.eth.contract(address=test_pools["pool_address"][i], abi=PANCAKESWAP_V3_POOL_ABI)
            liquidity= str(pool_contract.functions.liquidity().call())
            slot0 = pool_contract.functions.slot0().call()
            sqrtPriceX96, tick, observationIndex, observationCardinality, observationCardinalityNext, feeProtocol, unlocked = [str(x) for x in slot0]
            assert liquidity == test_pools["param_liquidity"][i], f"Line {i} liquidity not updated. Should be {test_pools['param_liquidity'][i]} got {liquidity}"
            assert sqrtPriceX96 == test_pools["param_sqrtPriceX96"][i], f"Line {i} sqrtPriceX96 not updated. Should be {test_pools['param_sqrtPriceX96'][i]} got {sqrtPriceX96}"
            assert tick == test_pools["param_tick"][i], f"Line {i} tick not updated. Should be {test_pools['param_tick'][i]} got {tick}"
            assert observationIndex == test_pools["param_observationIndex"][i], f"Line {i} observationIndex not updated. Should be {test_pools['param_observationIndex'][i]} got {observationIndex}"
            assert observationCardinality == test_pools["param_observationCardinality"][i], f"Line {i} observationCardinality not updated. Should be {test_pools['param_observationCardinality'][i]} got {observationCardinality}"
            assert observationCardinalityNext == test_pools["param_observationCardinalityNext"][i], f"Line {i} observationCardinalityNext not updated. Should be {test_pools['param_observationCardinalityNext'][i]} got {observationCardinalityNext}"
            assert feeProtocol == test_pools["param_feeProtocol"][i], f"Line {i} feeProtocol not updated. Should be {test_pools['param_feeProtocol'][i]} got {feeProtocol}"
            assert unlocked == test_pools["param_unlocked"][i], f"Line {i} feeProtocol not updated. Should be {test_pools['param_unlocked'][i]} got {unlocked}"
            print('Test Passed')

# ALTERNATIVE methods for transaction success query the txhash to see if the signature field `r` was populated indicating success
# actually_txt_all_successful_txs = []
# for tx in txt_all_successful_txs:
#     this_txhash = "0x"+ast.literal_eval(tx.split("\n\n")[1]).hex()
#     if w3.eth.get_transaction(this_txhash)['r'].hex() != "0x00":
#         actually_txt_all_successful_txs += [tx]

erc20_abi = '[{"inputs":[{"internalType":"uint256","name":"chainId_","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"src","type":"address"},{"indexed":true,"internalType":"address","name":"guy","type":"address"},{"indexed":false,"internalType":"uint256","name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":true,"inputs":[{"indexed":true,"internalType":"bytes4","name":"sig","type":"bytes4"},{"indexed":true,"internalType":"address","name":"usr","type":"address"},{"indexed":true,"internalType":"bytes32","name":"arg1","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"arg2","type":"bytes32"},{"indexed":false,"internalType":"bytes","name":"data","type":"bytes"}],"name":"LogNote","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"src","type":"address"},{"indexed":true,"internalType":"address","name":"dst","type":"address"},{"indexed":false,"internalType":"uint256","name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":true,"inputs":[],"name":"DOMAIN_SEPARATOR","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"usr","type":"address"},{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"usr","type":"address"},{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"burn","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"guy","type":"address"}],"name":"deny","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"usr","type":"address"},{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"mint","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"src","type":"address"},{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"move","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"holder","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"expiry","type":"uint256"},{"internalType":"bool","name":"allowed","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"usr","type":"address"},{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"pull","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"usr","type":"address"},{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"push","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"guy","type":"address"}],"name":"rely","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"src","type":"address"},{"internalType":"address","name":"dst","type":"address"},{"internalType":"uint256","name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"version","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"wards","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]'