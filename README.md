# skale-explorer
Service for administrating and running skale blockscouts

### Install

- Clone repo
- Install docker-compose (if not installed)
- Put skale-manager ABI for the network in `data/abi.json` file
- Create .env file 

### Run

#### Default mode

Agent will generate configuration files and run blockscouts for chains that do not have blockscout yet
```
./run.sh
```

#### Update mode

Agent will update configuration files for the list of chains
```
./run.sh --update
```

#### Verify mode

Agent will run contract verification for the list of chains
```
./run.sh --verify
```

### Arguments

To run explorer-admin, `.env` file shoudl be created in the project root directory. Use `template.env` as example. 

- ETH_ENDPOINT - node endpoint with skale-manager _(required)_ 
- PROXY_DOMAIN - domain of the network proxy _(required)_
- SCHAIN_NAMES - list of schain names to run blockscouts for _(optional)_
- HOST_DOMAIN - domain of the node to run blockscouts with secured connection   _(optional)_  
- WALLET_CONNECT_PROJECT_ID - WalletConnect project ID for blockscout frontend _(optional)_
