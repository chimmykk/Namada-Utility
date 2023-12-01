from web3 import Web3
import config
import time
private_key = 'replacepvtkey'
test = private_key
eth_rpc = "https://goerli.infura.io/v3/3376a33c419a4d249d680fa54ff8b6bf"
web3 = Web3(Web3.HTTPProvider(eth_rpc))

print(web3.is_connected())
uniRouterContractAddress = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'

# Uniswap V2 router ABI
uniAbi = []

  # Add the ABI for Uniswap V2 router on Ethereum
# Existing liquidity pool contract ABI
lpAbi =[]

# WETH address on Ethereum mainnet
weth = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'

# Deployed Token ABI
abi = []
sender_address = web3.to_checksum_address('0x0d657f444BF2AA726a085067C4E26e782d837452')  # TokenAddress of the holder

# Create instance of Uniswap V2 Router Address Contract
uni_contract = web3.eth.contract(uniRouterContractAddress, abi=uniAbi)

# Create instance of deployed smart contract (your custom token)
tokenAddress =web3.to_checksum_address('0x082C85c81195614D417EaC10dbE767F0eBB3d53a')  # Contract address
token = web3.eth.contract(tokenAddress, abi=abi)

# Create instance of existing liquidity pool contract
lpContractAddress =web3.to_checksum_address('0x971857254d10F77878052D01063d40235a762294')
lp_contract = web3.eth.contract(lpContractAddress, abi=lpAbi)

# Approve Token before adding Liquidity
totalSupply = token.functions.totalSupply().call()
print(web3.from_wei(totalSupply, 'ether'))

approve = token.functions.approve(uniRouterContractAddress, totalSupply).build_transaction({
    'from': sender_address,
    'gasPrice': web3.to_wei('15', 'gwei'),
    'nonce': web3.eth.get_transaction_count(sender_address),
})
signed_txn = web3.eth.account.sign_transaction(approve, private_key=test)
tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("Approved: " + web3.to_hex(tx_token))
# Calculate 0.01% of the total balance of the token
token_balance = token.functions.balanceOf(sender_address).call()
# Set the desired amount of tokens and ETH for liquidity provision
amountTokenDesired = 1500000 * (10 ** 18)  # Hardcoded value for tokens with decimals
amountETHDesired = 0.015 * (10 ** 18)  # Hardcoded value for ETH

# Set minimum token and ETH amounts (adjust as needed)
amountTokenMin = 100000000  # Set to 1 wei (smallest possible value)
amountETHMin = int(0.000015 * (10 ** 18))  # Hardcoded value for ETH
#all the value are here and change here

to = sender_address
deadline = int(time.time()) + 1000000

nonce = web3.eth.get_transaction_count(sender_address)

# Check the existing liquidity
existingLiquidity = lp_contract.functions.balanceOf(sender_address).call()
print("Existing LP Tokens:", existingLiquidity)
# Add liquidity to the existing pool
add_liquidity_tx = uni_contract.functions.addLiquidityETH(
    tokenAddress,  # Address of your custom token
    amountTokenDesired,
    amountTokenMin,  
    amountETHMin, 
    to, 
    deadline,  
).build_transaction({
    'from': sender_address,
    'value': amountETHMin,  # The amount of ETH to provide as liquidity
    'gasPrice': web3.to_wei('40', 'gwei'),
    'nonce': nonce,
})

signed_txn = web3.eth.account.sign_transaction(add_liquidity_tx, private_key=test)
tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("LP Tokens added: " + web3.to_hex(tx_token))
