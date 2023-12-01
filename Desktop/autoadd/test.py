from web3 import Web3
import config
import time

bsc = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc))

print(web3.isConnected())


#pancakeswap router
panRouterContractAddress = '0x10ED43C718714eb63d5aA57B78B54704E256024E'

#pancakeswap router abi 
panabi =[]
#Deployed Token ABI
abi = []

sender_address = web3.toChecksumAddress('') #TokenAddress of holder
wbnb = web3.toChecksumAddress("0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c")  #WBNB Address

#Create Instance of Pancakerouter Address Contract
contract = web3.eth.contract(panRouterContractAddress, abi=panabi)


#Create instance of deployed smart contract
tokenAddress = web3.toChecksumAddress('')  #Contract address
token = web3.eth.contract(tokenAddress, abi=abi)


 #Approve Token before adding Liquidity

totalSupply = token.functions.totalSupply().call()
print(web3.fromWei(totalSupply, 'ether'))


#start = time.time()
approve = token.functions.approve(panRouterContractAddress, totalSupply).buildTransaction({
           'from': sender_address,
          'gasPrice': web3.toWei('5','gwei'),
          'nonce': web3.eth.get_transaction_count(sender_address),
          })

signed_txn = web3.eth.account.sign_transaction(approve, private_key=config.private)
tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("Approved: " + web3.toHex(tx_token))

time.sleep(10)


#Creating Liquidity pair

amountTokenDesired = web3.toWei('90000000', 'ether')
amountTokenMin = web3.toWei('90000000', 'ether')
amountETHMin = 19000000000000000
to = sender_address
deadline = int(time.time()) + 1000000

nonce = web3.eth.get_transaction_count(sender_address)

addliq = contract.functions.addLiquidityETH(
    tokenAddress,amountTokenDesired, amountTokenMin, amountETHMin, to, deadline
).buildTransaction({
            'from': sender_address,
            'value': web3.toWei('0.01', 'ether'),
            'gasPrice': web3.toWei('5','gwei'),
            'nonce': nonce,
            })

signed_txn = web3.eth.account.sign_transaction(addliq, private_key=config.private)
tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("LP created: " + web3.toHex(tx_token))


