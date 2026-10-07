const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("IdentityRegistry", function () {
  let contract, owner;

  beforeEach(async function () {
    [owner] = await ethers.getSigners();
    const IdentityRegistry = await ethers.getContractFactory("IdentityRegistry");
    contract = await IdentityRegistry.deploy();
  });

  it("Should register an identity", async function () {
    const did = "did:qidentity:test123";
    const pkHash = ethers.keccak256(ethers.toUtf8Bytes("pubkey"));
    const idHash = ethers.keccak256(ethers.toUtf8Bytes("identity"));

    await contract.registerIdentity(did, pkHash, idHash, "ECDSA");
    const identity = await contract.getIdentity(did);

    expect(identity.did).to.equal(did);
    expect(identity.algorithm).to.equal("ECDSA");
    expect(identity.status).to.equal(0);
  });

  it("Should revoke an identity", async function () {
    const did = "did:qidentity:revoke1";
    const pkHash = ethers.keccak256(ethers.toUtf8Bytes("pubkey"));
    const idHash = ethers.keccak256(ethers.toUtf8Bytes("identity"));

    await contract.registerIdentity(did, pkHash, idHash, "ECDSA");
    await contract.revokeIdentity(did);

    const status = await contract.verifyIdentityStatus(did);
    expect(status).to.equal(1);
  });

  it("Should record migration", async function () {
    const did = "did:qidentity:migrate1";
    const pkHash = ethers.keccak256(ethers.toUtf8Bytes("pubkey"));
    const idHash = ethers.keccak256(ethers.toUtf8Bytes("identity"));

    await contract.registerIdentity(did, pkHash, idHash, "ECDSA");
    await contract.recordMigration(did, "ECDSA", "ML-DSA", pkHash, pkHash);

    const identity = await contract.getIdentity(did);
    expect(identity.algorithm).to.equal("ML-DSA");
    expect(identity.version).to.equal(2);
  });
});
