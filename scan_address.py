import json
from web3 import Web3

# 1. Connexion à un RPC endpoint de Gnosis
gnosis_rpc = "https://rpc.gnosischain.com"
web3 = Web3(Web3.HTTPProvider(gnosis_rpc))

# Vérifier la connexion
if not web3.is_connected():
    raise Exception("Impossible de se connecter au noeud RPC Gnosis")

# Charger les uuids depuis le JSON
with open('listof_reevaluation.json', 'r', encoding='utf-8') as json_file:
    reevaluation_data = json.load(json_file)

# Extraire les UUID depuis le JSON
# On suppose que les UUID sont des adresses Ethereum valides sur Gnosis.
additional_addresses = [item['uuid'] for item in reevaluation_data if 'uuid' in item]

# Liste initiale de tokens ERC-20 connus
erc20_token_addresses = [
    "0x9c58bacc331c9aa871afd802db6379a98e80cedb",  # GNO token sur Gnosis
    "0xddafbb505ad214d7b80b1f830fccc89b60fb7a83",  # USDC sur Gnosis
    "0xaA2C0cf54cB418eB24E7e09053B82C875C68bb88",  # SOON address
    "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d",  # WXDAI
    "0x0AA1e96D2a46Ec6beB2923dE1E61Addf5F5f1dce",  # REG
    "0x0675e8F4A52eA6c845CB6427Af03616a2af42170",  # RWA
    # Autres adresses connues...
]

# Ajouter les UUID extraits du JSON à la liste des adresses ERC-20
erc20_token_addresses.extend(additional_addresses)

# Adresse de l'utilisateur que l'on veut scanner
user_address = web3.to_checksum_address("0xc3210d7491E290405A533C8f923BC8A0FEe273AD")

# ABI minimal pour ERC-20 : balanceOf, decimals et symbol
erc20_abi = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "type": "function"
    }
]

balances = {}

for token_addr in erc20_token_addresses:
    # S'assurer que l'adresse est valide avant de l'utiliser
    try:
        checksummed_addr = web3.to_checksum_address(token_addr)
    except ValueError:
        # Si l'UUID n'est pas une adresse valide, on l'ignore
        continue
    
    token_contract = web3.eth.contract(address=checksummed_addr, abi=erc20_abi)
    try:
        balance = token_contract.functions.balanceOf(user_address).call()
    except:
        # Si l'appel échoue (pas un contrat ERC-20 valide, par ex.), on ignore
        continue

    if balance > 0:
        decimals = token_contract.functions.decimals().call()
        symbol = token_contract.functions.symbol().call()
        normalized_balance = balance / (10 ** decimals)
        balances[symbol] = normalized_balance

# Afficher les tokens détenus
if balances:
    print("L'adresse détient les tokens suivants :")
    for sym, amt in balances.items():
        print(f"- {sym}: {amt}")
else:
    print("Aucun token ERC-20 trouvé avec un solde supérieur à zéro.")
