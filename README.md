# ergo-offchain-execution

## Requirements

Running the ergo off chain execution setup requires Docker and Docker compose

## Installation

1. Make a copy of .env.example and name it .env
2. Edit .env so the reward address is set to an address you own. This address will get lots of small utxo's, do dont use your main address.
3. run/build the services using the following command:
```
sudo docker-compose up -d --build
```
4. Once all containers are built ensure they are all running properly.
5. These services will now be ready to work together with project specific code such as ergopad-offchain.