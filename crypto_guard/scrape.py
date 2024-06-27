import requests
import pandas as pd

def fetch_bitcoin_transaction(txid):
    url = f"https://blockchain.info/rawtx/{txid}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        transaction = response.json()
        return transaction
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def fetch_block(height):
    url = f"https://blockchain.info/block-height/{height}?format=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        block_data = response.json()
        return block_data['blocks'][0]
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def fetch_transactions_after_block(start_height, end_height=None):
    current_height = start_height
    transactions = []
    
    while True:
        block = fetch_block(current_height)
        if block:
            transactions.extend(block['tx'])
            current_height += 1
        else:
            break

        if end_height and current_height > end_height:
            break

    return transactions

def fetch_transactions_after_transaction(txid, n=10):
    current_txid = txid
    transactions = []
    
    while True:
        transaction = fetch_bitcoin_transaction(current_txid)
        if transaction:
            transactions.append(transaction)
            bh = transaction['block_height']
            block = fetch_block(bh)
            if not block:
                break
            # find this transaction in block 
            for tx in block['tx']:
                if tx['hash'] == current_txid:
                    idx = block['tx'].index(tx)
                    if idx < len(block['tx']) - 1:
                        current_txid = block['tx'][idx + 1]['hash']
                    else:
                        current_txid = None
                    break
            # get next block if this is last transaction in block 
            if not current_txid:
                current_height = block['height']
                block = fetch_block(current_height + 1)
                if block:
                    current_txid = block['tx'][0]['hash']
                else:
                    break
        else:
            break

        if len(transactions) >= n:
            break

    return transactions

def read_malicious_transactions_from_csv(file_path):
    result = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            progress = (i+1)/len(lines)*100
            print(f"Reading transaction {i+1}/{len(lines)} ({progress:.2f}%)", end='\r')
            txid = line.strip()
            transaction = fetch_bitcoin_transaction(txid)
            if transaction:
                result.append(transaction)
    return result
            
def scrape(output: str, malicious_transactions_csv: str, n: int):
    malicious_transactions = read_malicious_transactions_from_csv(malicious_transactions_csv)
    transactions = []
    for i, tx in enumerate(malicious_transactions):
        progress = (i + 1) / len(malicious_transactions) * 100
        print(f"Scraping transaction {i + 1}/{len(malicious_transactions)} ({progress:.2f}%)", end='\r')
        transactions.extend(fetch_transactions_after_transaction(tx['hash'], n))
    data = [] 
    # create pandas dataframe and save it to CSV 
    for i, tx in enumerate(transactions):
        progress = (i + 1) / len(transactions) * 100
        print(f"Processing transaction {i + 1}/{len(transactions)} ({progress:.2f}%)", end='\r')
        inputs = tx['inputs']
        outputs = tx['out']
        for inp in inputs:
            for out in outputs:
                data.append({
                    'output_addr': out['addr'] if 'addr' in out else "",
                    'value': out['value'] if 'value' in out else 0,
                    'time': tx['time'] if 'time' in tx else 0,
                    'block_height': tx['block_height'] if 'block_height' in tx else 0,
                    'txid': tx['hash'] if 'hash' in tx else "",
                    'is_scam': 1 if tx in malicious_transactions else 0,
                    'spent': inp['prev_out']['spent'] if "prev_out" in inp and "spent" in inp['prev_out'] else False,
                    'type': inp['prev_out']['type'] if "prev_out" in inp and "type" in inp['prev_out'] else "",
                    'sequence': inp['sequence'] if 'sequence' in inp else 0,
                    'script': inp['script'] if 'script' in inp else "",
                    'witness': inp['witness'] if 'witness' in inp else "",
                    'ver': tx['ver'] if 'ver' in tx else 0,
                    'vin_sz': tx['vin_sz'] if 'vin_sz' in tx else 0,
                    'vout_sz': tx['vout_sz'] if 'vout_sz' in tx else 0,
                    'size': tx['size'] if 'size' in tx else 0,
                    'weight': tx['weight'] if 'weight' in tx else 0,
                    'fee': tx['fee'] if 'fee' in tx else 0,
                    'relayed_by': tx['relayed_by'] if 'relayed_by' in tx else "",
                    'lock_time': tx['lock_time'] if 'lock_time' in tx else 0,
                    'tx_index': tx['tx_index'] if 'tx_index' in tx else 0,
                    'double_spend': tx['double_spend'] if 'double_spend' in tx else False,
                    'block_index': tx['block_index'] if 'block_index' in tx else 0,
                })
    df = pd.DataFrame(data)
    df.to_csv(output, index=False)
