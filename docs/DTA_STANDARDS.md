# DTA Data Provenance Standards v1.0.0 - Complete Guide

## Overview

The Data & Trust Alliance Data Provenance Standards provide a comprehensive framework for documenting the origin, processing, and intended use of datasets. This guide explains all 22 fields with examples, common mistakes, and regulatory relevance.

**Why These Standards Matter:**
- **Regulatory Compliance**: EU AI Act, GDPR, CCPA, and other regulations require data provenance documentation
- **Trust & Transparency**: Enable data consumers to make informed decisions about data fitness for purpose
- **Reproducibility**: Support scientific reproducibility and audit trails for AI/ML models
- **Risk Management**: Help identify potential biases, privacy issues, and quality problems early

---

## Standard Structure

The DTA standards organize 22 fields into three main categories:

```
DTA Provenance Metadata
├── source (8 fields) - Where the data came from
├── provenance (6 fields) - How the data was created and processed
└── use (8 fields) - How the data should (and shouldn't) be used
```

---

## 1. SOURCE Category

Documents the origin and provider of the dataset.

### 1.1 datasetName

**Type**: String (required)
**Purpose**: Human-readable identifier for the dataset

**Example**:
```json
"datasetName": "Chest X-Ray Pneumonia Detection Dataset"
```

**Best Practices**:
- Use descriptive names that indicate content and purpose
- Include version or date if multiple releases exist
- Avoid acronyms without explanation

**Common Mistakes**:
- ❌ "dataset_v2.csv" (not descriptive)
- ❌ "training_data" (too generic)
- ✅ "Urban Air Quality Monitoring Network - San Francisco 2024"

**Regulatory Relevance**: Required for EU AI Act documentation of training data sources

---

### 1.2 datasetVersion

**Type**: String (recommended)
**Purpose**: Track changes and updates to the dataset over time

**Example**:
```json
"datasetVersion": "2.1.0"
```

**Best Practices**:
- Use semantic versioning (major.minor.patch)
- Major version: breaking changes (schema changes, data format)
- Minor version: additions (new records, new fields)
- Patch version: corrections (bug fixes, data quality improvements)

**Common Mistakes**:
- ❌ "latest" (not specific)
- ❌ "2024-01-15" (use dateDataGenerated for timestamps)
- ✅ "3.2.1" (clear versioning)

---

### 1.3 datasetURI

**Type**: String (recommended)
**Purpose**: Direct link or identifier to access the dataset

**Example**:
```json
"datasetURI": "s3://hospital-ml-datasets/chest-xray-v2"
```

**Supported URI Schemes**:
- `s3://` - AWS S3 buckets
- `gs://` - Google Cloud Storage
- `https://` - Web URLs
- `ipfs://` - IPFS content identifiers
- `doi:` - Digital Object Identifiers
- `arn:aws:` - AWS Resource Names

**Common Mistakes**:
- ❌ Including credentials in URI
- ❌ Using temporary signed URLs
- ✅ Use permanent, version-specific identifiers

---

### 1.4 providerName

**Type**: String (required)
**Purpose**: Organization or individual who created/maintains the dataset

**Example**:
```json
"providerName": "General Hospital ML Research Division"
```

**Best Practices**:
- Use full legal name for organizations
- Include department/division for large organizations
- Provide contact information in providerWebsite

**Regulatory Relevance**: GDPR Article 26 requires identification of data controllers

---

### 1.5 providerWebsite

**Type**: String (recommended)
**Purpose**: URL for more information about the provider

**Example**:
```json
"providerWebsite": "https://example-hospital.edu/ml-research"
```

**Should Include**:
- Contact information for data inquiries
- Data governance policies
- Terms of use and licensing
- Update schedule

---

### 1.6 geographicSourceOfData

**Type**: String (recommended)
**Purpose**: Geographic origin of the data subjects or collection points

**Example**:
```json
"geographicSourceOfData": "United States, Massachusetts"
```

**Granularity Guidelines**:
- Use appropriate level: country > region > city
- For privacy-sensitive data: country or region only
- For public data: can be more specific
- For global data: list major regions or "Global"

**Why It Matters**:
- Identifies potential geographic biases
- Indicates applicable regulations (GDPR for EU, CCPA for California)
- Helps assess representativeness for intended use cases

---

### 1.7 dataOriginCountry

**Type**: String (recommended)
**Purpose**: ISO country code(s) where data originated

**Example**:
```json
"dataOriginCountry": "US"
```

**Format**: Use ISO 3166-1 alpha-2 codes (US, UK, DE, etc.)

**For Multi-Country Datasets**:
```json
"dataOriginCountry": "US, CA, MX"  // North American dataset
"dataOriginCountry": "EU"  // European Union member states
"dataOriginCountry": "Global"  // Worldwide
```

**Regulatory Importance**: Critical for determining applicable data protection laws

---

### 1.8 locationDataGenerated

**Type**: String (optional)
**Purpose**: Physical location where data was created or collected

**Example**:
```json
"locationDataGenerated": "Massachusetts General Hospital, Boston, MA"
```

**Use Cases**:
- Scientific experiments (lab location)
- IoT sensors (sensor deployment locations)
- Medical data (healthcare facility)
- Surveys (where surveys were conducted)

**Privacy Consideration**: May reveal sensitive information; use appropriate granularity

---

## 2. PROVENANCE Category

Documents how the data was generated, processed, and quality-controlled.

### 2.1 dataGenerationMethod

**Type**: String (required)
**Purpose**: Detailed description of how the data was created

**Example**:
```json
"dataGenerationMethod": "DICOM medical imaging from diagnostic radiology department. Images captured using Siemens SOMATOM Definition AS+ CT scanner. Standardized acquisition protocols following ACR guidelines."
```

**Should Include**:
- Collection methodology (sensors, surveys, scraping, etc.)
- Equipment or tools used
- Protocols or standards followed
- Sampling strategy

**Examples by Data Type**:

**Survey Data**:
```json
"dataGenerationMethod": "Online survey via Qualtrics platform. Stratified random sampling of registered voters. Response rate 23.4%. Survey conducted February 1-15, 2024."
```

**Sensor Data**:
```json
"dataGenerationMethod": "IoT sensors (PurpleAir PA-II-SD) measuring PM2.5 every 60 seconds. Sensors GPS-calibrated for location accuracy ±5m. Data transmitted via 4G/LTE to MQTT broker."
```

**Scraped Data**:
```json
"dataGenerationMethod": "Web scraping of public GitHub repositories using GitHub API v3. Rate-limited to 5000 requests/hour. Only repositories with permissive licenses (MIT, Apache 2.0)."
```

---

### 2.2 dateDataGenerated

**Type**: String (ISO 8601 date/datetime) (required)
**Purpose**: When the data was created or collected

**Format**: `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ`

**Examples**:
```json
"dateDataGenerated": "2023-01-15T00:00:00Z"  // Single timestamp
"dateDataGenerated": "2023-01-15"  // Date only
```

**For Time-Series or Ongoing Collection**:
```json
"dateDataGenerated": "2024-01-01T00:00:00Z",
"_notes": "Start date of ongoing collection. Data continues to be generated in real-time."
```

**Why It Matters**:
- Establishes temporal context (social media data from 2015 vs 2024 very different)
- Helps assess data staleness
- Important for reproducibility

---

### 2.3 dataType

**Type**: String (required)
**Purpose**: High-level category of data modality

**Allowed Values**:
- `Text` - Natural language, code, documents
- `Image` - Photos, medical imaging, satellite imagery
- `Audio` - Speech, music, environmental sounds
- `Video` - Recordings, livestreams
- `Time series` - Sensor data, stock prices, metrics
- `Tabular` - CSV, databases, spreadsheets
- `Graph` - Networks, relationships
- `Geospatial` - Maps, GPS coordinates
- `Multi-modal` - Combination of above

**Examples**:
```json
"dataType": "Image"  // Medical imaging dataset
"dataType": "Text"  // Code dataset
"dataType": "Tabular"  // Financial transactions CSV
"dataType": "Time series"  // IoT sensor stream
```

---

### 2.4 dataFormat

**Type**: String (required)
**Purpose**: Technical format and schema of the data

**Examples**:

**Images**:
```json
"dataFormat": "DICOM (original), PNG (processed for ML, 512x512 pixels, 8-bit grayscale)"
```

**Text**:
```json
"dataFormat": "JSON Lines (.jsonl), schema: {code: string, repo: string, license: string}"
```

**Tabular**:
```json
"dataFormat": "CSV with 31 columns: Time, V1-V28 (PCA features), Amount, Class"
```

**Time Series**:
```json
"dataFormat": "JSON stream via MQTT, schema: {timestamp: ISO8601, sensor_id: UUID, pm25: float}"
```

**Best Practices**:
- Include file format (JPEG, CSV, Parquet, etc.)
- Document schema or structure
- Specify encoding (UTF-8, ASCII)
- Note compression (gzip, bz2)

---

### 2.5 dataSubjectivity

**Type**: String (recommended)
**Purpose**: Degree of human judgment in data creation

**Allowed Values**:
- `Objective` - Deterministic, no interpretation required
- `Subjective` - Involves human judgment or interpretation
- `Mixed` - Combination of objective and subjective elements

**Examples**:

**Objective**:
```json
"dataSubjectivity": "Objective - direct physical measurements from calibrated sensors"
```

**Subjective**:
```json
"dataSubjectivity": "Subjective - radiologist diagnoses represent expert clinical interpretation, validated by consensus of 3 board-certified radiologists"
```

**Mixed**:
```json
"dataSubjectivity": "Mixed - transaction amounts are objective, but fraud labels represent expert analyst decisions (estimated 98.5% accuracy)"
```

**Why It Matters**:
- Subjective data may have inter-annotator disagreement
- Affects reproducibility and ground truth reliability
- Important for assessing potential biases

---

### 2.6 qualityIndicators

**Type**: Object (recommended)
**Purpose**: Metrics describing data quality, completeness, and reliability

**Common Indicators**:

**Completeness**:
```json
"qualityIndicators": {
  "missingValues": "0% - all records complete",
  "completeness": "100% of images have diagnostic labels"
}
```

**Accuracy**:
```json
"qualityIndicators": {
  "labelingAccuracy": "Inter-rater agreement κ=0.89 (strong agreement)",
  "measurementAccuracy": "±10% compared to EPA reference monitors"
}
```

**Scale & Coverage**:
```json
"qualityIndicators": {
  "recordCount": "284,807 transactions",
  "timeSpan": "2 days of transactions",
  "geographicCoverage": "15 EU countries"
}
```

**Class Balance** (for ML datasets):
```json
"qualityIndicators": {
  "classImbalance": "Highly imbalanced - 99.828% legitimate vs 0.172% fraud"
}
```

**Resolution/Granularity**:
```json
"qualityIndicators": {
  "resolution": "512x512 pixels, 8-bit grayscale",
  "samplingRate": "60-second intervals per sensor"
}
```

---

## 3. USE Category

Documents legal rights, restrictions, privacy measures, and intended applications.

### 3.1 intendedUse

**Type**: String (required)
**Purpose**: Describe what the data was designed for and appropriate use cases

**Example**:
```json
"intendedUse": "Training and validation of machine learning models for automated pneumonia detection in chest X-rays. Intended for research and educational purposes to advance medical AI diagnostics."
```

**Should Include**:
- Primary use case
- Appropriate applications
- Target audience (researchers, commercial, etc.)
- Scope limitations

**Anti-Pattern Warning**: If data is later used for purposes significantly different from intended use, document this in provenance updates

---

### 3.2 restrictions

**Type**: String (recommended)
**Purpose**: Legal and practical limitations on data use

**Examples**:

**Research-Only**:
```json
"restrictions": "Research and educational use only. Not approved for clinical deployment without additional validation and FDA clearance. Commercial use requires separate licensing."
```

**License-Based**:
```json
"restrictions": "Subject to original open-source licenses (MIT, Apache 2.0, BSD). Attribution required for derived models. Commercial use allowed with proper license compliance."
```

**Geographic**:
```json
"restrictions": "Not approved for use outside EU due to GDPR transfer restrictions. Requires adequacy decision or SCCs for international transfers."
```

**Common Restrictions**:
- Non-commercial only
- Research/education only
- No production deployment
- Geographic limitations
- Attribution requirements
- No reverse engineering

---

### 3.3 legalRightsToUse

**Type**: String (required)
**Purpose**: Legal basis for data collection and use

**Examples**:

**Medical Research (IRB Approved)**:
```json
"legalRightsToUse": "Institutional Review Board (IRB) approved under protocol #2022-ML-001. Patient consent obtained for research use of de-identified medical data. HIPAA compliant under Safe Harbor de-identification method."
```

**Public Data (Fair Use)**:
```json
"legalRightsToUse": "Collected from public repositories with permissive licenses. Complies with GitHub Terms of Service for API usage. Fair use doctrine applies for ML training purposes under current US copyright law interpretations."
```

**GDPR Legitimate Interest**:
```json
"legalRightsToUse": "Data processing authorized under GDPR Article 6(1)(f) - legitimate interest for fraud prevention. Data Protection Impact Assessment (DPIA) completed. Approved by EU Data Protection Authority."
```

**Consent-Based**:
```json
"legalRightsToUse": "Explicit user consent obtained via terms of service. Users granted perpetual, worldwide license for data use in model training. CCPA opt-out mechanism provided."
```

**Key Legal Bases**:
- Consent (GDPR Art. 6(1)(a))
- Legitimate interest (GDPR Art. 6(1)(f))
- Legal obligation (GDPR Art. 6(1)(c))
- Public interest (GDPR Art. 6(1)(e))
- Fair use / Fair dealing (copyright)
- Terms of Service agreements
- Public domain

---

### 3.4 privacyMeasures

**Type**: String (required if sensitiveData=true)
**Purpose**: Detailed description of privacy protection techniques applied

**Examples**:

**De-identification (Medical Data)**:
```json
"privacyMeasures": "Full de-identification per HIPAA Safe Harbor: all 18 identifiers removed including patient names, dates (converted to year only), geographic identifiers, device IDs. Expert determination confirmed re-identification risk < 0.01%."
```

**Anonymization (Financial Data)**:
```json
"privacyMeasures": "Multi-layer anonymization: (1) PII removal, (2) PCA transformation prevents feature reversal, (3) k-anonymity (k=10), (4) differential privacy (ε=2.0) on transaction amounts, (5) geographic generalization to country level. Re-identification risk < 0.001%."
```

**Aggregation (IoT Data)**:
```json
"privacyMeasures": "Precise GPS coordinates not publicly disclosed - published maps use 100m grid aggregation. Data retention: raw data 90 days, aggregated data indefinite. No personally identifiable information collected."
```

**Common Privacy Techniques**:
- **De-identification**: Remove direct identifiers (names, IDs)
- **Pseudonymization**: Replace identifiers with pseudonyms
- **Anonymization**: Irreversibly remove identifying information
- **k-anonymity**: Ensure each record is indistinguishable from k-1 others
- **Differential privacy**: Add calibrated noise to protect individuals
- **Aggregation**: Group data to prevent individual identification
- **Generalization**: Reduce precision (zip code → state)
- **Suppression**: Remove high-risk data points

**GDPR Requirement**: Must demonstrate "appropriate technical and organizational measures" (Article 32)

---

### 3.5 sensitiveData

**Type**: Boolean (required)
**Purpose**: Flag whether dataset contains sensitive or regulated data

**Values**:
- `true` - Contains sensitive data (requires additional documentation)
- `false` - No sensitive data

**Examples**:
```json
"sensitiveData": true  // Medical records, financial data, PII
"sensitiveData": false  // Public GitHub code, weather data
```

**When to Mark as True**:
- Personal identifiable information (PII)
- Protected health information (PHI)
- Financial/payment data
- Biometric data
- Genetic data
- Location data (precise)
- Political opinions, religious beliefs
- Trade secrets, confidential business info
- Children's data (COPPA)
- Special category data (GDPR Article 9)

---

### 3.6 sensitiveDataCategories

**Type**: Array of strings (required if sensitiveData=true)
**Purpose**: Specific types of sensitive data present

**Examples**:

**Medical Data**:
```json
"sensitiveDataCategories": [
  "Protected Health Information (PHI)",
  "Medical diagnostic data"
]
```

**Financial Data**:
```json
"sensitiveDataCategories": [
  "Financial transaction data",
  "Payment card data (anonymized)",
  "Consumer spending patterns (anonymized)"
]
```

**Common Categories**:
- Personal Identifiable Information (PII)
- Protected Health Information (PHI)
- Payment Card Industry (PCI) data
- Biometric data
- Genetic information
- Precise geolocation
- Political opinions
- Religious or philosophical beliefs
- Trade union membership
- Sexual orientation or behavior
- Criminal history
- Children's data (under 13 or 16)

**Regulatory Mapping**:
- GDPR Article 9: "Special categories of personal data"
- HIPAA: Protected Health Information (PHI)
- PCI-DSS: Cardholder data, sensitive authentication data
- COPPA: Children's personal information
- CCPA: Sensitive personal information (§1798.140(ae))

---

### 3.7 dataProcessingLocation

**Type**: String (recommended)
**Purpose**: Geographic location(s) where data is processed and stored

**Examples**:

**Cloud Provider**:
```json
"dataProcessingLocation": "AWS us-west-2 (data collection and processing), HuggingFace Hub CDN (distribution)"
```

**Compliance-Focused**:
```json
"dataProcessingLocation": "EU data centers only (Frankfurt, Amsterdam). No cross-border transfers outside EU. Processing infrastructure certified under ISO 27001, PCI-DSS Level 1, and SOC 2 Type II."
```

**Multi-Region**:
```json
"dataProcessingLocation": "Data ingestion: AWS us-west-1. Real-time processing: Kafka clusters in us-west-1. Long-term storage: S3 with cross-region replication to us-east-1. All data remains within US borders."
```

**Why It Matters**:
- **GDPR**: Cross-border data transfers require adequacy decisions or safeguards
- **Data Sovereignty**: Some countries require data to stay within borders
- **Compliance**: Industry regulations may restrict processing locations
- **Performance**: Latency and data transfer costs
- **Legal Discovery**: Jurisdiction affects subpoenas and legal requests

**Should Include**:
- Cloud provider and regions
- Countries where data is processed
- Whether data crosses borders
- Compliance certifications (ISO 27001, SOC 2, etc.)

---

## Common Scenarios & Complete Examples

### Scenario 1: Internal ML Pipeline (Low Compliance Burden)

**Use Case**: Training data for internal chatbot, non-sensitive

```json
{
  "source": {
    "datasetName": "Customer Support Chat Logs 2024-Q1",
    "datasetVersion": "1.0.0",
    "providerName": "Acme Corp Customer Success Team"
  },
  "provenance": {
    "dataGenerationMethod": "Exported from Zendesk Support. Filtered for resolved tickets with CSAT > 4.",
    "dateDataGenerated": "2024-01-01T00:00:00Z",
    "dataType": "Text",
    "dataFormat": "JSON Lines, schema: {ticket_id, messages[], resolution_time, csat_score}",
    "dataSubjectivity": "Objective conversation logs"
  },
  "use": {
    "intendedUse": "Fine-tuning internal customer support chatbot",
    "restrictions": "Internal use only, not for public model training",
    "legalRightsToUse": "Company-owned data from business operations",
    "privacyMeasures": "Customer names and emails removed, replaced with pseudonyms",
    "sensitiveData": false,
    "sensitiveDataCategories": [],
    "dataProcessingLocation": "AWS us-east-1"
  }
}
```

**Minimal but Compliant**: Focuses on essential fields, lightweight privacy measures

---

### Scenario 2: High-Compliance Medical AI (Maximum Documentation)

**Use Case**: FDA submission for medical device using AI

```json
{
  "source": {
    "datasetName": "Multi-Center Diabetic Retinopathy Screening Dataset",
    "datasetVersion": "3.0.1",
    "datasetURI": "s3://fda-submission-2024/dr-screening-v3",
    "providerName": "Medical AI Consortium - Stanford, Mayo Clinic, Johns Hopkins",
    "providerWebsite": "https://medical-ai-consortium.org/dr-dataset",
    "geographicSourceOfData": "United States - California, Minnesota, Maryland",
    "dataOriginCountry": "US",
    "locationDataGenerated": "Stanford University Hospital, Mayo Clinic Rochester, Johns Hopkins Hospital"
  },
  "provenance": {
    "dataGenerationMethod": "Fundus photography using Topcon TRC-50DX and Zeiss Visucam 500. Images captured by certified ophthalmic photographers following AAO imaging protocols. Each image graded by 3 board-certified ophthalmologists using ETDRS severity scale.",
    "dateDataGenerated": "2022-06-01T00:00:00Z",
    "dataType": "Image",
    "dataFormat": "DICOM (original), JPEG 2000 (processed, 2048x2048 pixels, 24-bit color). Metadata includes: acquisition device, image quality score, laterality (OD/OS), pupil dilation status.",
    "dataSubjectivity": "Subjective - diabetic retinopathy grading involves expert clinical judgment. Inter-rater agreement: quadratic weighted kappa = 0.92 (excellent agreement). Adjudication by senior retina specialist for discordant cases.",
    "qualityIndicators": {
      "recordCount": "150,000 images from 30,000 patients",
      "interRaterAgreement": "κ=0.92 (quadratic weighted)",
      "imageQuality": "98.7% images rated 'adequate' or 'good' quality",
      "prevalence": "No DR: 60%, Mild: 15%, Moderate: 15%, Severe: 7%, PDR: 3%",
      "demographicCoverage": "Age 18-90 (median 58), 52% female, 48% male, ethnicity: 40% White, 25% Hispanic, 20% Black, 15% Asian/Other",
      "missingData": "0.2% images excluded due to insufficient quality"
    },
    "dataProcessingSteps": [
      "DICOM to JPEG 2000 conversion with lossless compression",
      "Image quality assessment using automated algorithms + manual review",
      "De-identification: removal of all PHI from DICOM headers per HIPAA Safe Harbor",
      "Color normalization using Reinhard method to account for device variations",
      "Train/validation/test split: 70/15/15, stratified by severity grade and imaging center",
      "External test set: 10,000 images from separate sites for generalizability testing"
    ]
  },
  "use": {
    "intendedUse": "Training and validation of AI/ML algorithms for automated diabetic retinopathy screening. Intended for FDA Class II medical device submission. Clinical use case: point-of-care screening in primary care and endocrinology clinics.",
    "restrictions": "Research and development use under medical AI consortium agreement. Clinical deployment requires FDA 510(k) clearance. No commercial use outside consortium members without licensing. External researchers may request access via data use agreement with IRB approval.",
    "legalRightsToUse": "Multi-site IRB approved under 45 CFR 46.111 (federated IRB agreement). Patient informed consent obtained with specific authorization for AI research. HIPAA-compliant data use agreement executed between participating institutions. FDA pre-submission meeting completed (Q-Submission Q234567).",
    "privacyMeasures": "HIPAA Safe Harbor de-identification: removal of all 18 identifiers. Expert determination conducted by certified privacy expert per §164.514(b)(1). Re-identification risk analysis: risk < 0.01% (very small risk as defined by HIPAA). Date shifting: all dates shifted by random offset per patient while preserving intervals. Image metadata scrubbed of device serial numbers and technician IDs. Statistical disclosure control applied to demographic data to prevent attribute disclosure.",
    "sensitiveData": true,
    "sensitiveDataCategories": [
      "Protected Health Information (PHI) - de-identified",
      "Medical diagnostic images",
      "Health condition (diabetes)",
      "Demographic data"
    ],
    "dataProcessingLocation": "HIPAA-compliant AWS GovCloud (US) infrastructure. Processing restricted to us-gov-west-1 region. Encrypted at rest (FIPS 140-2 validated AES-256) and in transit (TLS 1.3). BAA executed with AWS. SOC 2 Type II and HITRUST certified. No international data transfers."
  },
  "_fdaSubmissionNotes": {
    "regulatoryContext": "FDA Software as Medical Device (SaMD) - Moderate Level of Concern per FDA guidance on Clinical Decision Support Software",
    "validationStrategy": "Standalone performance testing on external test set. Primary endpoint: sensitivity/specificity for referable DR (moderate or worse). Non-inferiority comparison to human graders.",
    "biasAnalysis": "Subgroup analysis by age, sex, ethnicity, and imaging site to demonstrate equitable performance per FDA guidance on algorithmic bias"
  }
}
```

**Maximum Documentation**: Suitable for FDA submission, IRB review, or publication in medical journals

---

## Regulatory Compliance Mapping

### EU AI Act (High-Risk AI Systems)

**Required DTA Fields**:
- `datasetName`, `datasetVersion` - Article 10(3): Datasets properly identified
- `dataGenerationMethod` - Article 10(2): Data collection process documented
- `geographicSourceOfData`, `dataOriginCountry` - Article 10(2)(g): Geographic origin
- `intendedUse` - Article 10(2)(a): Relevant design choices
- `privacyMeasures` - Article 10(5): Privacy measures
- `sensitiveData`, `sensitiveDataCategories` - Article 10(5): Sensitive data identification

### GDPR (General Data Protection Regulation)

**Article 30 (Records of Processing Activities)**:
- All DTA fields contribute to GDPR compliance documentation

**Article 32 (Security of Processing)**:
- `privacyMeasures`, `dataProcessingLocation`

**Article 35 (Data Protection Impact Assessment)**:
- Complete DTA record serves as input to DPIA

### HIPAA (Health Insurance Portability and Accountability Act)

**Privacy Rule §164.514 (De-identification)**:
- `privacyMeasures` must document Safe Harbor or Expert Determination method
- `sensitiveDataCategories` must identify PHI elements

**Security Rule §164.308 (Administrative Safeguards)**:
- `dataProcessingLocation` documents where PHI is processed

### FDA (Medical Device Regulations)

**Software as Medical Device (SaMD) Guidance**:
- Complete DTA record supports premarket submissions (510(k), PMA)
- `qualityIndicators` documents dataset quality for validation studies

---

## Common Mistakes & How to Fix Them

### Mistake 1: Vague dataGenerationMethod

❌ **Bad**:
```json
"dataGenerationMethod": "Collected from users"
```

✅ **Good**:
```json
"dataGenerationMethod": "Collected via mobile app survey presented to users upon login. Stratified sampling by age group and geographic region. Response rate 34.2%. Survey conducted March 1-31, 2024 using validated questionnaire from Smith et al. 2023."
```

---

### Mistake 2: Insufficient privacyMeasures

❌ **Bad**:
```json
"privacyMeasures": "PII removed"
```

✅ **Good**:
```json
"privacyMeasures": "Direct identifiers removed (names, email addresses, phone numbers). Quasi-identifiers generalized: age → age bins (18-25, 26-35, etc.), zip code → state level. K-anonymity enforced with k=5. Expert review confirmed re-identification risk < 0.1%."
```

---

### Mistake 3: Missing Legal Basis

❌ **Bad**:
```json
"legalRightsToUse": "We can use this data"
```

✅ **Good**:
```json
"legalRightsToUse": "User consent obtained via terms of service (v2.3, accepted 2024-01-15). Users granted perpetual, worldwide license for data use in model training. GDPR Article 6(1)(a) consent basis. CCPA opt-out mechanism provided at privacy.example.com/ccpa."
```

---

## Tools & Validation

### JSON Schema Validation

**Note:** As of February 2024, the official DTA JSON Schema file from the Data & Trust Alliance
GitHub repository contains invalid JSON and cannot be used for validation. We recommend using
the DTA specification documentation for manual validation instead.

Alternatively, validate using our library's built-in validator:

```python
from src.verify import validate_provenance_file

report = validate_provenance_file('my-metadata.json')
print(report)
```

### DTA Python Library

The Data & Trust Alliance provides a Python library:

```bash
pip install dta-metadata

from dta_metadata import ProvenanceMetadata, validate

metadata = ProvenanceMetadata(...)
validate(metadata)  # Checks compliance with standards
```

---

## Further Resources

- **Official Specification**: https://github.com/Data-and-Trust-Alliance/DPS
- **JSON Schema**: https://github.com/Data-and-Trust-Alliance/json-metadata
- **DTA Website**: https://www.dtaalliance.org/
- **Python Library**: https://github.com/Data-and-Trust-Alliance/python-metadata
- **EU AI Act Text**: https://artificialintelligenceact.eu/
- **GDPR Full Text**: https://gdpr-info.eu/
- **FDA SaMD Guidance**: https://www.fda.gov/medical-devices/software-medical-device-samd

---

## Summary

The DTA Data Provenance Standards provide a comprehensive, industry-backed framework for documenting datasets. By following these 22 fields, you can:

✅ Meet regulatory requirements (EU AI Act, GDPR, FDA)
✅ Build trust with data consumers
✅ Enable reproducible research
✅ Identify and mitigate risks early
✅ Facilitate data sharing and collaboration

**Start Simple**: Focus on required fields first, then add recommended fields as needed
**Be Specific**: Vague documentation defeats the purpose
**Update Regularly**: Provenance should evolve as data is processed
**Validate**: Use JSON schema and DTA tools to ensure compliance

For implementation examples, see our Git-native and blockchain demonstrations in this repository.
