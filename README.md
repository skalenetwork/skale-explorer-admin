# skale-explorer
Service for administrating and running skale blockscouts

### Install and run

#### Prerequisites
- Clone repo
- Install docker-compose (if not installed)
- Put skale-manager ABI for the network in `data/abi.json` file
- Create .env file (use template.env as example)

#### Run

Arguments:
- ETH_ENDPOINT - node endpoint with skale-manager _(required)_ 
- PROXY_DOMAIN - domain of the network proxy _(required)_
- SCHAIN_NAMES - list of schain names to run blockscouts for _(optional)_

```
./run.sh
```