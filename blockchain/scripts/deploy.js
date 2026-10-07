const hre = require("hardhat");

async function main() {
  const IdentityRegistry = await hre.ethers.getContractFactory("IdentityRegistry");
  const contract = await IdentityRegistry.deploy();
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log(`IdentityRegistry deployed to: ${address}`);
  console.log(`Update CONTRACT_ADDRESS in backend/.env to: ${address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
