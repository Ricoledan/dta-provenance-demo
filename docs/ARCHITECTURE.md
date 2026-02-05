# Architecture Documentation

Technical architecture diagrams for both Git-native and blockchain implementations.

---

## Table of Contents

1. [Git-Native Architecture](#git-native-architecture)
2. [Blockchain Architecture](#blockchain-architecture)
3. [Data Flow Diagrams](#data-flow-diagrams)
4. [Provenance Graph Structure](#provenance-graph-structure)
5. [Integration Patterns](#integration-patterns)

---

## Git-Native Architecture

### System Overview

```mermaid
%%{init: {"theme":"dark","themeVariables":{"darkMode":true,"background":"#0d1117","primaryColor":"#2d333b","primaryTextColor":"#e6edf3","primaryBorderColor":"#444c56","lineColor":"#768390","secondaryColor":"#1c2128","tertiaryColor":"#22272e","clusterBkg":"#2d333b","clusterBorder":"#444c56","nodeTextColor":"#e6edf3","mainBkg":"#2d333b","secondBkg":"#22272e","edgeLabelBackground":"#2d333b","nodeBorder":"#444c56"}}}%%
graph TB
    subgraph User["User Interface"]
        CLI["CLI Tool<br/>(dta-provenance)"]
        Code["Python Code<br/>(import library)"]
    end

    subgraph Core["Core Library"]
        Tracker["ProvenanceTracker<br/>• commit_with_provenance()<br/>• read_provenance()<br/>• verify_integrity()"]
        Verifier["ProvenanceVerifier<br/>• validate_dta_compliance()<br/>• trace_lineage()"]
        Meta["ProvenanceMetadata<br/>• DTA v1.0.0 fields<br/>• compute_hash()"]
    end

    subgraph Git["Git Repository"]
        Commits["Git Commits<br/>• Commit message<br/>• DTA metadata trailers<br/>• SHA-256 hash"]
        History["Git History<br/>• Full audit trail<br/>• Signed commits<br/>• Cryptographic chain"]
    end

    User --> Core
    Core --> Git

```

### Commit Structure

```mermaid
%%{init: {"theme":"dark","themeVariables":{"darkMode":true,"background":"#0d1117","primaryColor":"#2d333b","primaryTextColor":"#e6edf3","primaryBorderColor":"#444c56","lineColor":"#768390","secondaryColor":"#1c2128","tertiaryColor":"#22272e","clusterBkg":"#2d333b","clusterBorder":"#444c56","nodeTextColor":"#e6edf3","mainBkg":"#2d333b","secondBkg":"#22272e","edgeLabelBackground":"#2d333b","nodeBorder":"#444c56"}}}%%
graph LR
    subgraph Commit["Git Commit"]
        Message["Commit Message"]
        Trailers["Git Trailers"]
        Tree["Tree Object<br/>(files)"]
        Parent["Parent Commit"]
    end

    subgraph Trailers["DTA Trailers"]
        Version["DTA-Provenance-Version: 1.0.0"]
        Hash["DTA-Provenance-Hash: sha256..."]
        Name["DTA-Dataset-Name: ..."]
        JSON["DTA-Provenance-Metadata: {...}"]
    end

    Message --> Trailers
    Commit --> Tree
    Commit --> Parent

```

---

## Blockchain Architecture

### System Overview

```mermaid
%%{init: {"theme":"dark","themeVariables":{"darkMode":true,"background":"#0d1117","primaryColor":"#2d333b","primaryTextColor":"#e6edf3","primaryBorderColor":"#444c56","lineColor":"#768390","secondaryColor":"#1c2128","tertiaryColor":"#22272e","clusterBkg":"#2d333b","clusterBorder":"#444c56","nodeTextColor":"#e6edf3","mainBkg":"#2d333b","secondBkg":"#22272e","edgeLabelBackground":"#2d333b","nodeBorder":"#444c56"}}}%%
graph TB
    subgraph User["User Interface"]
        Web3["Web3 DApp"]
        Script["Node.js Script"]
    end

    subgraph Contract["Smart Contract (On-Chain)"]
        Registry["ProvenanceRegistry.sol<br/>• registerProvenance()<br/>• verifyRecord()<br/>• validateMetadata()"]
        Events["Events<br/>• RecordCreated<br/>• RecordVerified<br/>• MetadataUpdated"]
    end

    subgraph Blockchain["Blockchain Network"]
        ETH["Ethereum Mainnet"]
        L2["Layer 2<br/>(Polygon, Arbitrum)"]
    end

    subgraph Storage["Off-Chain Storage"]
        IPFS["IPFS<br/>(Full DTA metadata)"]
        Indexer["The Graph<br/>(Query indexing)"]
    end

    User --> Contract
    Contract --> Blockchain
    Contract -.-> Events
    Events -.-> Indexer
    User -.-> IPFS
    Contract -.-> IPFS

```

### Smart Contract Data Structure

```mermaid
%%{init: {"theme":"dark","themeVariables":{"darkMode":true,"background":"#0d1117","primaryColor":"#2d333b","primaryTextColor":"#e6edf3","primaryBorderColor":"#444c56","lineColor":"#768390","secondaryColor":"#1c2128","tertiaryColor":"#22272e","clusterBkg":"#2d333b","clusterBorder":"#444c56","nodeTextColor":"#e6edf3","mainBkg":"#2d333b","secondBkg":"#22272e","edgeLabelBackground":"#2d333b","nodeBorder":"#444c56"}}}%%
graph TB
    subgraph Contract["ProvenanceRegistry Contract"]
        Mapping["records mapping<br/>(bytes32 => ProvenanceRecord)"]
        Provider["providerRecords mapping<br/>(address => bytes32[])"]
        Counter["totalRecords counter"]
    end

    subgraph Record["ProvenanceRecord Struct"]
        Name["datasetName: string"]
        URI["metadataURI: string"]
        Hash["metadataHash: bytes32"]
        Addr["provider: address"]
        Time["timestamp: uint256"]
        Verified["verified: bool"]
    end

    Contract --> Record

```

---

## Data Flow Diagrams

### Git-Native: Commit with Provenance

```mermaid
%%{init: {"theme":"dark","themeVariables":{"darkMode":true,"background":"#0d1117","primaryColor":"#2d333b","primaryTextColor":"#e6edf3","primaryBorderColor":"#444c56","lineColor":"#768390","secondaryColor":"#1c2128","tertiaryColor":"#22272e","clusterBkg":"#2d333b","clusterBorder":"#444c56","nodeTextColor":"#e6edf3","mainBkg":"#2d333b","secondBkg":"#22272e","edgeLabelBackground":"#2d333b","nodeBorder":"#444c56"}}}%%
sequenceDiagram
    participant User
    participant CLI
    participant Tracker
    participant Metadata
    participant Git

    User->>CLI: dta-provenance commit file.csv
    CLI->>Metadata: Load JSON file
    Metadata->>Metadata: Validate DTA fields
    Metadata->>Metadata: Compute SHA-256 hash
    CLI->>Tracker: commit_with_provenance()
    Tracker->>Git: Stage files
    Tracker->>Git: Create commit with trailers
    Git->>Tracker: Return commit hash
    Tracker->>CLI: Commit successful
    CLI->>User: Display commit hash

    Note over Metadata,Git: Cryptographic integrity<br/>via hash + signatures
```

### Git-Native: Verify Integrity

```mermaid
%%{init: {"theme":"dark","themeVariables":{"darkMode":true,"background":"#0d1117","primaryColor":"#2d333b","primaryTextColor":"#e6edf3","primaryBorderColor":"#444c56","lineColor":"#768390","secondaryColor":"#1c2128","tertiaryColor":"#22272e","clusterBkg":"#2d333b","clusterBorder":"#444c56","nodeTextColor":"#e6edf3","mainBkg":"#2d333b","secondBkg":"#22272e","edgeLabelBackground":"#2d333b","nodeBorder":"#444c56"}}}%%
sequenceDiagram
    participant User
    participant CLI
    participant Tracker
    participant Verifier
    participant Git

    User->>CLI: dta-provenance verify HEAD
    CLI->>Tracker: verify_integrity(HEAD)
    Tracker->>Git: Read commit
    Git->>Tracker: Commit object
    Tracker->>Tracker: Extract metadata
    Tracker->>Tracker: Extract stored hash
    Tracker->>Tracker: Compute current hash
    Tracker->>Git: Verify GPG signature
    Git->>Tracker: Signature valid
    Tracker->>CLI: Verification result
    CLI->>User: ✅ Integrity verified

    Note over Tracker,Git: Tamper detection via<br/>hash comparison
```

### Blockchain: Register Provenance

```mermaid
%%{init: {"theme":"dark","themeVariables":{"darkMode":true,"background":"#0d1117","primaryColor":"#2d333b","primaryTextColor":"#e6edf3","primaryBorderColor":"#444c56","lineColor":"#768390","secondaryColor":"#1c2128","tertiaryColor":"#22272e","clusterBkg":"#2d333b","clusterBorder":"#444c56","nodeTextColor":"#e6edf3","mainBkg":"#2d333b","secondBkg":"#22272e","edgeLabelBackground":"#2d333b","nodeBorder":"#444c56"}}}%%
sequenceDiagram
    participant User
    participant Script
    participant IPFS
    participant Contract
    participant Blockchain

    User->>Script: Register dataset
    Script->>Script: Create DTA metadata JSON
    Script->>IPFS: Upload metadata
    IPFS->>Script: Return IPFS URI
    Script->>Script: Compute SHA-256 hash
    Script->>Contract: registerProvenance(name, URI, hash)
    Contract->>Contract: Generate recordId
    Contract->>Contract: Store record
    Contract->>Contract: Emit RecordCreated event
    Contract->>Blockchain: Transaction submitted
    Blockchain->>Blockchain: Mine block
    Blockchain->>Script: Transaction receipt
    Script->>User: ✅ Record registered

    Note over Script,Blockchain: Gas costs apply<br/>for each transaction
```

---

## Provenance Graph Structure

### Data Lineage DAG (Directed Acyclic Graph)

```mermaid
%%{init: {"theme":"dark","themeVariables":{"darkMode":true,"background":"#0d1117","primaryColor":"#2d333b","primaryTextColor":"#e6edf3","primaryBorderColor":"#444c56","lineColor":"#768390","secondaryColor":"#1c2128","tertiaryColor":"#22272e","clusterBkg":"#2d333b","clusterBorder":"#444c56","nodeTextColor":"#e6edf3","mainBkg":"#2d333b","secondBkg":"#22272e","edgeLabelBackground":"#2d333b","nodeBorder":"#444c56"}}}%%
graph LR
    A["Raw Data<br/>v1.0"]
    B["Cleaned Data<br/>v1.1"]
    C["Processed Data<br/>v1.2"]
    D["Training Set<br/>v2.0"]
    E["Test Set<br/>v2.0"]
    F["Model v1<br/>trained"]
    G["Model v2<br/>retrained"]

    A --> B
    B --> C
    C --> D
    C --> E
    D --> F
    D --> G
    E --> F
    E --> G

```

### Provenance Chain (Git Commits)

```mermaid
%%{init: {"theme":"dark","themeVariables":{"darkMode":true,"background":"#0d1117","primaryColor":"#2d333b","primaryTextColor":"#e6edf3","primaryBorderColor":"#444c56","lineColor":"#768390","secondaryColor":"#1c2128","tertiaryColor":"#22272e","clusterBkg":"#2d333b","clusterBorder":"#444c56","nodeTextColor":"#e6edf3","mainBkg":"#2d333b","secondBkg":"#22272e","edgeLabelBackground":"#2d333b","nodeBorder":"#444c56"}}}%%
graph LR
    subgraph History["Git History (Newest to Oldest)"]
        C3["Commit 3<br/>Update dataset<br/>DTA metadata"]
        C2["Commit 2<br/>Add features<br/>DTA metadata"]
        C1["Commit 1<br/>Initial data<br/>DTA metadata"]
        C0["Commit 0<br/>Repository init"]
    end

    C3 --> C2
    C2 --> C1
    C1 --> C0

```

---

## Integration Patterns

### MLflow Integration

```mermaid
%%{init: {"theme":"dark","themeVariables":{"darkMode":true,"background":"#0d1117","primaryColor":"#2d333b","primaryTextColor":"#e6edf3","primaryBorderColor":"#444c56","lineColor":"#768390","secondaryColor":"#1c2128","tertiaryColor":"#22272e","clusterBkg":"#2d333b","clusterBorder":"#444c56","nodeTextColor":"#e6edf3","mainBkg":"#2d333b","secondBkg":"#22272e","edgeLabelBackground":"#2d333b","nodeBorder":"#444c56"}}}%%
graph TB
    subgraph ML["ML Training Pipeline"]
        Data["Training Data"]
        Train["Model Training"]
        Log["MLflow Logging"]
    end

    subgraph Prov["Provenance Tracking"]
        Tracker["ProvenanceTracker"]
        Commit["Git Commit"]
    end

    subgraph MLflow["MLflow Registry"]
        Experiment["Experiment"]
        Run["Run"]
        Artifacts["Artifacts"]
    end

    Data --> Tracker
    Tracker --> Commit
    Data --> Train
    Train --> Log
    Log --> Run
    Run --> Experiment
    Run --> Artifacts
    Commit -.-> Run

    Note["Commit hash stored<br/>as MLflow parameter"]
    Commit -.-> Note
    Note -.-> Run

```

### DVC Integration

```mermaid
%%{init: {"theme":"dark","themeVariables":{"darkMode":true,"background":"#0d1117","primaryColor":"#2d333b","primaryTextColor":"#e6edf3","primaryBorderColor":"#444c56","lineColor":"#768390","secondaryColor":"#1c2128","tertiaryColor":"#22272e","clusterBkg":"#2d333b","clusterBorder":"#444c56","nodeTextColor":"#e6edf3","mainBkg":"#2d333b","secondBkg":"#22272e","edgeLabelBackground":"#2d333b","nodeBorder":"#444c56"}}}%%
graph TB
    subgraph Files["Data Files"]
        Large["large_dataset.parquet<br/>(10 GB)"]
        DVC["large_dataset.parquet.dvc<br/>(metadata file)"]
    end

    subgraph Storage["Remote Storage"]
        S3["AWS S3<br/>(actual data)"]
    end

    subgraph Prov["Git Provenance"]
        Git["Git Repository"]
        Meta["DTA Metadata"]
    end

    Large -.-> S3
    Large --> DVC
    DVC --> Git
    Meta --> Git

    Note["DVC handles large files<br/>Git tracks provenance"]
    DVC -.-> Note

```

### CI/CD Pipeline Integration

```mermaid
%%{init: {"theme":"dark","themeVariables":{"darkMode":true,"background":"#0d1117","primaryColor":"#2d333b","primaryTextColor":"#e6edf3","primaryBorderColor":"#444c56","lineColor":"#768390","secondaryColor":"#1c2128","tertiaryColor":"#22272e","clusterBkg":"#2d333b","clusterBorder":"#444c56","nodeTextColor":"#e6edf3","mainBkg":"#2d333b","secondBkg":"#22272e","edgeLabelBackground":"#2d333b","nodeBorder":"#444c56"}}}%%
graph LR
    subgraph Pipeline["CI/CD Pipeline"]
        Push["Git Push"]
        Validate["Validate<br/>Provenance"]
        Test["Run Tests"]
        Deploy["Deploy"]
    end

    subgraph Actions["GitHub Actions"]
        Checkout["Checkout Code"]
        Install["Install dta-provenance"]
        Check["dta-provenance validate"]
        Verify["dta-provenance verify HEAD"]
    end

    Push --> Checkout
    Checkout --> Install
    Install --> Check
    Check --> Verify
    Verify --> Test
    Test --> Deploy

```

---

## DTA Metadata Structure

### Complete Field Hierarchy

```mermaid
%%{init: {"theme":"dark","themeVariables":{"darkMode":true,"background":"#0d1117","primaryColor":"#2d333b","primaryTextColor":"#e6edf3","primaryBorderColor":"#444c56","lineColor":"#768390","secondaryColor":"#1c2128","tertiaryColor":"#22272e","clusterBkg":"#2d333b","clusterBorder":"#444c56","nodeTextColor":"#e6edf3","mainBkg":"#2d333b","secondBkg":"#22272e","edgeLabelBackground":"#2d333b","nodeBorder":"#444c56"}}}%%
graph TB
    Root["DTA Provenance<br/>Metadata v1.0.0"]

    subgraph Source["source (8 fields)"]
        S1["datasetName"]
        S2["datasetVersion"]
        S3["datasetURI"]
        S4["providerName"]
        S5["providerWebsite"]
        S6["geographicSourceOfData"]
        S7["dataOriginCountry"]
        S8["locationDataGenerated"]
    end

    subgraph Provenance["provenance (6 fields)"]
        P1["dataGenerationMethod"]
        P2["dateDataGenerated"]
        P3["dataType"]
        P4["dataFormat"]
        P5["dataSubjectivity"]
        P6["qualityIndicators"]
    end

    subgraph Use["use (8 fields)"]
        U1["intendedUse"]
        U2["restrictions"]
        U3["legalRightsToUse"]
        U4["privacyMeasures"]
        U5["sensitiveData"]
        U6["sensitiveDataCategories"]
        U7["dataProcessingLocation"]
    end

    Root --> Source
    Root --> Provenance
    Root --> Use

```

---

## Security Model

### Git-Native Security Layers

```mermaid
%%{init: {"theme":"dark","themeVariables":{"darkMode":true,"background":"#0d1117","primaryColor":"#2d333b","primaryTextColor":"#e6edf3","primaryBorderColor":"#444c56","lineColor":"#768390","secondaryColor":"#1c2128","tertiaryColor":"#22272e","clusterBkg":"#2d333b","clusterBorder":"#444c56","nodeTextColor":"#e6edf3","mainBkg":"#2d333b","secondBkg":"#22272e","edgeLabelBackground":"#2d333b","nodeBorder":"#444c56"}}}%%
graph TB
    subgraph Security["Security Layers"]
        L1["Layer 1: Git SHA-1 Hashing<br/>Every commit cryptographically hashed"]
        L2["Layer 2: GPG/SSH Signatures<br/>Commit authenticity verification"]
        L3["Layer 3: Metadata SHA-256<br/>DTA metadata integrity check"]
        L4["Layer 4: Access Control<br/>Git hosting permissions"]
    end

    L1 --> L2
    L2 --> L3
    L3 --> L4

    Trust["Trust Model:<br/>Federated (Git host)"]
    L4 --> Trust

```

### Blockchain Security Layers

```mermaid
%%{init: {"theme":"dark","themeVariables":{"darkMode":true,"background":"#0d1117","primaryColor":"#2d333b","primaryTextColor":"#e6edf3","primaryBorderColor":"#444c56","lineColor":"#768390","secondaryColor":"#1c2128","tertiaryColor":"#22272e","clusterBkg":"#2d333b","clusterBorder":"#444c56","nodeTextColor":"#e6edf3","mainBkg":"#2d333b","secondBkg":"#22272e","edgeLabelBackground":"#2d333b","nodeBorder":"#444c56"}}}%%
graph TB
    subgraph Security["Security Layers"]
        L1["Layer 1: Blockchain Consensus<br/>Network-wide agreement"]
        L2["Layer 2: Smart Contract<br/>Immutable code execution"]
        L3["Layer 3: Metadata SHA-256<br/>Tamper detection"]
        L4["Layer 4: Wallet Signatures<br/>Transaction authenticity"]
    end

    L1 --> L2
    L2 --> L3
    L3 --> L4

    Trust["Trust Model:<br/>Trustless (no central authority)"]
    L4 --> Trust

```

---

## Performance Characteristics

### Git-Native Performance Profile

```mermaid
%%{init: {"theme":"dark","themeVariables":{"darkMode":true,"background":"#0d1117","primaryColor":"#2d333b","primaryTextColor":"#e6edf3","primaryBorderColor":"#444c56","lineColor":"#768390","secondaryColor":"#1c2128","tertiaryColor":"#22272e","clusterBkg":"#2d333b","clusterBorder":"#444c56","nodeTextColor":"#e6edf3","mainBkg":"#2d333b","secondBkg":"#22272e","edgeLabelBackground":"#2d333b","nodeBorder":"#444c56"}}}%%
graph LR
    Operation["Operation Type"]

    Write["Write<br/>~45ms"]
    Read["Read<br/>~10ms"]
    Verify["Verify<br/>~50ms"]
    Trace["Trace<br/>~150ms"]

    Operation --> Write
    Operation --> Read
    Operation --> Verify
    Operation --> Trace

    Note["All operations<br/>complete instantly"]
    Trace -.-> Note

```

### Blockchain Performance Profile

```mermaid
%%{init: {"theme":"dark","themeVariables":{"darkMode":true,"background":"#0d1117","primaryColor":"#2d333b","primaryTextColor":"#e6edf3","primaryBorderColor":"#444c56","lineColor":"#768390","secondaryColor":"#1c2128","tertiaryColor":"#22272e","clusterBkg":"#2d333b","clusterBorder":"#444c56","nodeTextColor":"#e6edf3","mainBkg":"#2d333b","secondBkg":"#22272e","edgeLabelBackground":"#2d333b","nodeBorder":"#444c56"}}}%%
graph LR
    Operation["Operation Type"]

    Write["Write<br/>~3-10 seconds<br/>(+ block time)"]
    Read["Read<br/>~100ms"]
    Verify["Verify<br/>~200ms"]
    Query["Query<br/>~5 seconds<br/>(w/o indexer)"]

    Operation --> Write
    Operation --> Read
    Operation --> Verify
    Operation --> Query

    Note["Block confirmation<br/>adds latency"]
    Write -.-> Note

```

---

## Summary

Both architectures provide cryptographic provenance tracking with different trade-offs:

**Git-Native:**
- Simple, fast, free
- Private by default
- Requires trust in Git host
- Perfect for internal use

**Blockchain:**
- Complex, slower, costs money
- Public by default
- Trustless verification
- Only needed for adversarial multi-party scenarios

Choose based on your trust model, not the hype.
