// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ProvenanceRegistry
 * @dev Smart contract for registering DTA-compliant data provenance records
 * @notice This is a demonstration contract for educational purposes
 *
 * Design decisions:
 * - Stores metadata hash on-chain for immutability
 * - Full metadata stored off-chain (IPFS/Arweave) for cost optimization
 * - Simple access control (anyone can register, optional verification)
 * - Events for indexing and monitoring
 */
contract ProvenanceRegistry {
    // Provenance record structure
    struct ProvenanceRecord {
        string datasetName;         // Human-readable dataset name
        string metadataURI;        // IPFS/Arweave URI for full DTA metadata
        bytes32 metadataHash;      // SHA-256 hash of DTA metadata JSON
        address provider;          // Address of data provider
        uint256 timestamp;         // Block timestamp when registered
        bool verified;             // Optional verification flag
        bool exists;               // Check if record exists
    }

    // Mapping from recordId to ProvenanceRecord
    mapping(bytes32 => ProvenanceRecord) public records;

    // Mapping from provider address to array of their record IDs
    mapping(address => bytes32[]) public providerRecords;

    // Total number of records registered
    uint256 public totalRecords;

    // Events
    event RecordCreated(
        bytes32 indexed recordId,
        address indexed provider,
        string datasetName,
        bytes32 metadataHash,
        uint256 timestamp
    );

    event RecordVerified(
        bytes32 indexed recordId,
        address indexed verifier,
        uint256 timestamp
    );

    event MetadataUpdated(
        bytes32 indexed recordId,
        string newMetadataURI,
        bytes32 newMetadataHash,
        uint256 timestamp
    );

    /**
     * @dev Register a new provenance record
     * @param _datasetName Human-readable name of the dataset
     * @param _metadataURI URI pointing to full DTA metadata (IPFS, Arweave, etc.)
     * @param _metadataHash SHA-256 hash of the DTA metadata JSON
     * @return recordId Unique identifier for this provenance record
     */
    function registerProvenance(
        string memory _datasetName,
        string memory _metadataURI,
        bytes32 _metadataHash
    ) public returns (bytes32) {
        require(bytes(_datasetName).length > 0, "Dataset name cannot be empty");
        require(bytes(_metadataURI).length > 0, "Metadata URI cannot be empty");
        require(_metadataHash != bytes32(0), "Metadata hash cannot be zero");

        // Generate unique record ID from hash of key components
        bytes32 recordId = keccak256(
            abi.encodePacked(
                msg.sender,
                _datasetName,
                _metadataHash,
                block.timestamp
            )
        );

        require(!records[recordId].exists, "Record already exists");

        // Create and store record
        records[recordId] = ProvenanceRecord({
            datasetName: _datasetName,
            metadataURI: _metadataURI,
            metadataHash: _metadataHash,
            provider: msg.sender,
            timestamp: block.timestamp,
            verified: false,
            exists: true
        });

        // Add to provider's records
        providerRecords[msg.sender].push(recordId);

        // Increment counter
        totalRecords++;

        emit RecordCreated(
            recordId,
            msg.sender,
            _datasetName,
            _metadataHash,
            block.timestamp
        );

        return recordId;
    }

    /**
     * @dev Verify a provenance record
     * @param _recordId The record ID to verify
     * @notice In production, this should have access control (e.g., only trusted verifiers)
     */
    function verifyRecord(bytes32 _recordId) public {
        require(records[_recordId].exists, "Record does not exist");
        require(!records[_recordId].verified, "Record already verified");

        records[_recordId].verified = true;

        emit RecordVerified(_recordId, msg.sender, block.timestamp);
    }

    /**
     * @dev Get a provenance record by ID
     * @param _recordId The record ID to retrieve
     * @return The complete provenance record
     */
    function getProvenance(bytes32 _recordId)
        public
        view
        returns (ProvenanceRecord memory)
    {
        require(records[_recordId].exists, "Record does not exist");
        return records[_recordId];
    }

    /**
     * @dev Validate that provided metadata matches stored hash
     * @param _recordId The record ID to validate
     * @param _metadata The metadata JSON string to validate
     * @return True if metadata hash matches, false otherwise
     */
    function validateMetadata(bytes32 _recordId, string memory _metadata)
        public
        view
        returns (bool)
    {
        require(records[_recordId].exists, "Record does not exist");

        bytes32 computedHash = sha256(bytes(_metadata));
        return computedHash == records[_recordId].metadataHash;
    }

    /**
     * @dev Get all record IDs for a provider
     * @param _provider Address of the data provider
     * @return Array of record IDs
     */
    function getProviderRecords(address _provider)
        public
        view
        returns (bytes32[] memory)
    {
        return providerRecords[_provider];
    }

    /**
     * @dev Get total number of records by a provider
     * @param _provider Address of the data provider
     * @return Number of records
     */
    function getProviderRecordCount(address _provider)
        public
        view
        returns (uint256)
    {
        return providerRecords[_provider].length;
    }

    /**
     * @dev Update metadata URI and hash for an existing record
     * @param _recordId The record ID to update
     * @param _newMetadataURI New metadata URI
     * @param _newMetadataHash New metadata hash
     * @notice Only the original provider can update their records
     */
    function updateMetadata(
        bytes32 _recordId,
        string memory _newMetadataURI,
        bytes32 _newMetadataHash
    ) public {
        require(records[_recordId].exists, "Record does not exist");
        require(
            records[_recordId].provider == msg.sender,
            "Only provider can update record"
        );
        require(bytes(_newMetadataURI).length > 0, "Metadata URI cannot be empty");
        require(_newMetadataHash != bytes32(0), "Metadata hash cannot be zero");

        records[_recordId].metadataURI = _newMetadataURI;
        records[_recordId].metadataHash = _newMetadataHash;

        emit MetadataUpdated(
            _recordId,
            _newMetadataURI,
            _newMetadataHash,
            block.timestamp
        );
    }

    /**
     * @dev Check if a record exists
     * @param _recordId The record ID to check
     * @return True if record exists, false otherwise
     */
    function recordExists(bytes32 _recordId) public view returns (bool) {
        return records[_recordId].exists;
    }
}
