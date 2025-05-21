from web3 import Web3

# Initialize Web3
w3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))

# Test connection
print(f"Connected to BSC: {w3.is_connected()}")
print(f"Latest block: {w3.eth.block_number}")
print(f"Chain ID: {w3.eth.chain_id}")

# Try to get token info (example with BNB token)
bnb_address = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
code = w3.eth.get_code(w3.to_checksum_address(bnb_address))
print(f"BNB contract code length: {len(code)}")
