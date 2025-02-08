# Incredible Squaring AVS in Python

<b> Do not use it in Production, testnet only. </b>

A Python implementation of the EigenLayer [Incredible Squaring AVS](https://github.com/Layr-Labs/incredible-squaring-avs) 

## Dependencies

1. Install [foundry](https://book.getfoundry.sh/getting-started/installation)
```
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

2. Install [docker](https://docs.docker.com/get-docker/)

3. Build the contracts:
```
make build-contracts
```

4. Install [MCL](https://github.com/herumi/mcl) (it is included in the repo, so you can start with the unzip command)
```
sudo apt install libgmp3-dev
wget https://github.com/herumi/mcl/archive/refs/tags/v1.93.zip
unzip v1.93.zip
cd mcl-1.93
mkdir build
cd build
cmake ..
make
make install
```

5. Python3
6. Create a virtual environment (use the appropriate python command for your environment) and nnstall required modules. Downgrade web3 and re-install eth-account to avoid bugs (TODO: Fix said bugs 🪲):
```
python3 -m venv .venv 
pip install -r requirements.txt
pip install --force web3==6.19.0
pip install --force eth-account==0.13.5
```

> [!TIP]
> This AVS employs the [eigensdk-python](https://github.com/abramsymons/eigensdk-python) to facilitate interaction with EigenLayer contracts and to aggregate BLS signatures.

## Running

This simple session illustrates the basic flow of the AVS. The makefile commands are hardcoded for a single operator, but it's however easy to create new operator config files, and start more operators manually (see the actual commands that the makefile calls).

Start anvil in a separate terminal:

```bash
make start-anvil-chain-with-el-and-avs-deployed
```

The above command starts a local anvil chain from a [saved state](./tests/anvil/avs-and-eigenlayer-deployed-anvil-state.json) with eigenlayer and incredible-squaring contracts already deployed (but no operator registered).

Start the aggregator in a separate terminal:

```bash
make start-aggregator
```

Set your OpenAI API Key in another terminal:

```bash
export OPENAI_API_KEY=sk-mysecretapikey
```

Register the operator with eigenlayer and incredible-squaring, and then start the process:

```bash
make start-operator
```
