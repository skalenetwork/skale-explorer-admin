# skale-explorer
Service for administrating and running skale blockscouts

### Install

- Clone repo
- Install docker-compose (if not installed)
- Put skale-manager ABI for the network in `data/abi.json` file
- Create .env file 

### Run

#### Default mode

Agent will generate configuration files and run explorers for chains
```
./run.sh
```

#### Update mode

Agent will update configuration files
```
./run.sh --update
```

#### Verify mode

Agent will run contract verification
```
./run.sh --verify
```

#### Stop mode

Agent will stop explorers, all data from explorers will be saved
```
./run.sh --down
```

### Arguments

To run explorer-admin, `.env` file shoudl be created in the project root directory. Use `template.env` as example. 

- ETH_ENDPOINT - node endpoint with skale-manager _(required)_ 
- PROXY_DOMAIN - domain of the network proxy _(required)_
- SCHAIN_NAMES - list of schain names to operate _(optional)_
- SSL_ENABLED - set https connection for explorers _(optional)_
- INTERNAL_DOMAIN_NAME - domain of the node, to run explorers with https  _(optional)_  
- WALLET_CONNECT_PROJECT_ID - WalletConnect project ID for blockscout frontend _(optional)_
- IS_TESTNET - whether network is testnet _(optional)_
- BLOCKSCOUT_TAG - version of skalenetwork/blockscout container to use _(optional)_
