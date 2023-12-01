from web3 import Web3
import time
# FINAL qoeking
import config
goerli_rpc = "https://goerli.infura.io/v3/3376a33c419a4d249d680fa54ff8b6bf"
web3 = Web3(Web3.HTTPProvider(goerli_rpc))
private_key = 'replacepvtkey'
test = private_key
print(web3.is_connected())

# Uniswap Router V2
uniRouterContractAddress = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
uniAbi = []
sender_address = web3.to_checksum_address('0x0d657f444BF2AA726a085067C4E26e782d837452')  # TokenAddress of holder
weth = web3.to_checksum_address("0xB4FBF271143F4FBf7B91A5ded31805e42b2208d6")  # WETH Address on Goerli

contract = web3.eth.contract(uniRouterContractAddress, abi=uniAbi)

tokenAddress = web3.to_checksum_address('0x082C85c81195614D417EaC10dbE767F0eBB3d53a')  # Deployed ERC20 Token Contract on Goerli

# get LP info
contractA = web3.to_checksum_address("0x971857254d10F77878052D01063d40235a762294")  # LP Contract on Goerli
lpabi = []
lpcontract = web3.eth.contract(address=contractA, abi=lpabi)

lptotalSupply = lpcontract.functions.totalSupply().call()
print("LP Total Supply:", lptotalSupply)

balanceLp = lpcontract.functions.balanceOf(sender_address).call()
print("LP Balance of Sender:", balanceLp)

time.sleep(5)

tokenA = weth
tokenB = tokenAddress
liquidity = balanceLp
amountAmin = 1399
amountBmin = 64
to = sender_address
deadline = int(time.time()) + 1000000
slippage = 5  # 5% slippage
amountBmin = int(amountBmin * (1 - slippage / 100))

# Approve LP token before removing
nonce = web3.eth.get_transaction_count(sender_address)
approve = lpcontract.functions.approve(uniRouterContractAddress, balanceLp).build_transaction({
    'from': sender_address,
    'gasPrice': web3.to_wei('10', 'gwei'),
    'nonce': nonce,
})
signed_txn = web3.eth.account.sign_transaction(approve, private_key=test)  # Replace with your private key
tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("LP token Approved: " + web3.to_hex(tx_token))

time.sleep(10)

# Removing LP token from Uniswap V2 on Goerli
nonce = web3.eth.get_transaction_count(sender_address)

remove = contract.functions.removeLiquidityETH(
    tokenAddress, liquidity, amountAmin, amountBmin, to, deadline
).build_transaction({
    'from': sender_address,
    'gasPrice': web3.to_wei('10', 'gwei'),
    'nonce': nonce,
})

signed_txn = web3.eth.account.sign_transaction(remove, private_key=test)  # Replace with your private key
tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("Liquidity removed: " + web3.to_hex(tx_token))
