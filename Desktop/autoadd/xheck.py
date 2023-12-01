from web3 import Web3
from web3.middleware import geth_poa_middleware

# Uniswap Router V2 ABI (you need to provide the correct ABI)
uniswap_router_abi = [];

# Connect to a Goerli testnet node
w3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/3376a33c419a4d249d680fa54ff8b6bf'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)


assert w3.is_connected()
# Replace 'YOUR_ACCOUNT_ADDRESS' with your wallet address
my_address = w3.to_checksum_address('0x0d657f444BF2AA726a085067C4E26e782d837452')

# Replace 'YOUR_PRIVATE_KEY' with your private key
private_key = 'replacepvtkey'

# Uniswap Router V2 address (this is constant)
uniswap_router_address = w3.to_checksum_address('0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D')
uniswap_pair_address = '0x971857254d10F77878052D01063d40235a762294'  # Uniswap V2 pair address

router_contract = w3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)

# Define the amount of ETH and ERC20 tokens you want to supply
eth_to_add = w3.to_wei(0.01, 'ether')  # Send 0.01 ETH
token_to_add = 2900000  # Send 10,000 tokens

nonce = w3.eth.get_transaction_count(my_address)
slippage = 2  # 5% slippage

# Additional parameters for addLiquidityETH function
min_token_amount = int(token_to_add - (token_to_add * slippage / 100))
min_eth_amount = int(eth_to_add - (eth_to_add * slippage / 100))
recipient_address ="0x9260cA8E5c75693121E6cbD5a33b4497cF73f81f" # Recipient address for LP tokens
deadline = int(w3.eth.get_block('latest')['timestamp'] + 120)  # Deadline in unix timestamp (+120 seconds from now)

add_liquidity_txn = router_contract.functions.addLiquidityETH(
    '0x082C85c81195614D417EaC10dbE767F0eBB3d53a',  # Token address
    token_to_add,
    min_token_amount,
    min_eth_amount,
    recipient_address,
    deadline,
).build_transaction({
    'from': my_address,
    'value': eth_to_add,
    'gas': 250000,
    'gasPrice': w3.to_wei('30', 'gwei'),
    'nonce': nonce,
})

signed_txn = w3.eth.account.sign_transaction(add_liquidity_txn, private_key)

tx_token = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

print(f"Added Liquidity! Transaction hash: {w3.to_hex(tx_token)}")