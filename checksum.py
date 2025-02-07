from web3 import Web3
from ethers import ethers
#const ethers = require('ethers');

address = '0x58FAd51245861798c33E5b214551878D020B8922'

checksum = ethers.util.getAddress(address)
console.log("Checksum address:", checksum)


