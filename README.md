# ergo-offchain-execution

## Requirements

Running the ergo off chain execution setup requires: [Docker](https://docs.docker.com/get-started/) and [Docker compose v2](https://docs.docker.com/compose/compose-file/compose-file-v2/).

## Installation
Make a copy of `.env.example` and name it `.env`

Edit `.env` so the reward address is set to an address you own. This address will get lots of small utxos; do not use your main address.

Clone the repo
```sh
git clone https://github.com/ergo-pad/ergo-offchain-execution
```

Run/build the services using the following command:
```sh
cd ergo-offchain-execution
sudo docker-compose up -d --build
```

Once all containers are built, ensure they are running properly.

These services are now be ready to work together with project specific code such as ergopad-offchain.

## Validation
Once all services are running correctly, check the `tx_submitter` logs, and look for:
```
Submitted tx: f359ebc33e9573bf6eb1c40507cc4e02c9a30c9dc65131777e4097727210b854
```
You can look this transaction id up in the Ergo Explorer to see if you were successful in obtaining a reward.  If it does not show up, it indicates that another bot recieved the reward.