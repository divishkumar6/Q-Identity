// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract IdentityRegistry {
    struct Identity {
        string did;
        bytes32 publicKeyHash;
        bytes32 identityHash;
        string algorithm;
        uint8 status; // 0: active, 1: revoked, 2: migrated
        uint256 version;
        uint256 createdAt;
        uint256 updatedAt;
    }

    struct MigrationRecord {
        string oldAlgorithm;
        string newAlgorithm;
        bytes32 oldKeyRef;
        bytes32 newKeyRef;
        uint256 timestamp;
    }

    mapping(string => Identity) private identities;
    mapping(string => MigrationRecord[]) private migrationHistory;
    mapping(string => uint256) private identityVersions;

    event IdentityRegistered(string did, string algorithm, bytes32 publicKeyHash);
    event PublicKeyUpdated(string did, string newAlgorithm, bytes32 newPublicKeyHash);
    event MigrationRecorded(string did, string oldAlgorithm, string newAlgorithm);
    event IdentityRevoked(string did);

    modifier identityExists(string memory did) {
        require(bytes(identities[did].did).length > 0, "Identity does not exist");
        _;
;
    }

    function registerIdentity(
        string memory did,
        bytes32 publicKeyHash,
        bytes32 identityHash,
        string memory algorithm
    ) external returns (bool) {
        require(bytes(identities[did].did).length == 0, "Identity already registered");

        identities[did] = Identity({
            did: did,
            publicKeyHash: publicKeyHash,
            identityHash: identityHash,
            algorithm: algorithm,
            status: 0,
            version: 1,
            createdAt: block.timestamp,
            updatedAt: block.timestamp
        });

        identityVersions[did] = 1;

        emit IdentityRegistered(did, algorithm, publicKeyHash);
        return true;
    }

    function updatePublicKey(
        string memory did,
        bytes32 newPublicKeyHash,
        string memory newAlgorithm
    ) external identityExists(did) returns (bool) {
        Identity storage identity = identities[did];
        require(identity.status == 0, "Identity is not active");

        identity.publicKeyHash = newPublicKeyHash;
        identity.algorithm = newAlgorithm;
        identity.version += 1;
        identity.updatedAt = block.timestamp;

        emit PublicKeyUpdated(did, newAlgorithm, newPublicKeyHash);
        return true;
    }

    function recordMigration(
        string memory did,
        string memory oldAlgorithm,
        string memory newAlgorithm,
        bytes32 oldKeyRef,
        bytes32 newKeyRef
    ) external identityExists(did) returns (bool) {
        Identity storage identity = identities[did];
        require(identity.status == 0, "Identity is not active");

        migrationHistory[did].push(MigrationRecord({
            oldAlgorithm: oldAlgorithm,
            newAlgorithm: newAlgorithm,
            oldKeyRef: oldKeyRef,
            newKeyRef: newKeyRef,
            timestamp: block.timestamp
        }));

        identity.algorithm = newAlgorithm;
        identity.version += 1;
        identity.updatedAt = block.timestamp;

        emit MigrationRecorded(did, oldAlgorithm, newAlgorithm);
        return true;
    }

    function revokeIdentity(string memory did) external identityExists(did) returns (bool) {
        Identity storage identity = identities[did];
        require(identity.status == 0, "Identity already revoked");

        identity.status = 1;
        identity.updatedAt = block.timestamp;

        emit IdentityRevoked(did);
        return true;
    }

    function getIdentity(string memory did) external view identityExists(did) returns (Identity memory) {
        return identities[did];
    }

    function verifyIdentityStatus(string memory did) external view returns (uint8) {
        require(bytes(identities[did].did).length > 0, "Identity does not exist");
        return identities[did].status;
    }

    function getMigrationCount(string memory did) external view returns (uint256) {
        return migrationHistory[did].length;
    }

    function getMigration(string memory did, uint256 index) external view returns (MigrationRecord memory) {
        require(index < migrationHistory[did].length, "Index out of bounds");
        return migrationHistory[did][index];
    }
}
