/**
 * Pure validation logic for DTA v1.0.0 provenance metadata.
 *
 * This module mirrors the Python validation from src/verify.py
 * but is independent of VS Code APIs for testability.
 */

export interface ValidationError {
  severity: 'error' | 'warning' | 'info';
  message: string;
  field?: string;
}

export interface ValidationReport {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
  missingOptionalFields: string[];
  score: number; // 0.0 to 1.0
}

export interface ProvenanceMetadata {
  source?: {
    datasetName?: string;
    datasetVersion?: string;
    datasetURI?: string;
    providerName?: string;
    providerWebsite?: string;
    dateAcquired?: string;
    geographicSourceOfData?: string;
    contactInformation?: string;
  };
  provenance?: {
    dataGenerationMethod?: string;
    dateDataGenerated?: string;
    dataType?: string;
    dataFormat?: string;
    processingSteps?: string[];
    qualityIndicators?: Record<string, unknown>;
  };
  use?: {
    intendedUse?: string;
    legalRightsToUse?: string;
    restrictions?: string[];
    sensitiveData?: boolean;
    sensitiveDataCategories?: string[];
    privacyMeasures?: string[];
    retentionPolicy?: string;
    attribution?: string;
  };
  [key: string]: unknown;
}

const VALID_DATA_TYPES = [
  'Text',
  'Image',
  'Audio',
  'Video',
  'Time series',
  'Tabular',
  'Graph',
  'Geospatial',
  'Multi-modal'
];

const REQUIRED_FIELDS = {
  source: ['datasetName', 'providerName'],
  provenance: ['dataGenerationMethod', 'dateDataGenerated', 'dataType', 'dataFormat'],
  use: ['intendedUse', 'legalRightsToUse', 'sensitiveData']
};

const RECOMMENDED_FIELDS = {
  source: ['datasetVersion', 'datasetURI', 'providerWebsite', 'geographicSourceOfData'],
  provenance: ['qualityIndicators'],
  use: ['restrictions', 'privacyMeasures']
};

/**
 * Validate DTA v1.0.0 provenance metadata compliance.
 *
 * Performs both structural and semantic validation matching
 * the Python ProvenanceVerifier.validate_dta_compliance() logic.
 */
export function validateDTACompliance(metadata: ProvenanceMetadata): ValidationReport {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];
  const missingOptional: string[] = [];

  // Validate required fields
  for (const [category, fields] of Object.entries(REQUIRED_FIELDS)) {
    if (!(category in metadata)) {
      errors.push({
        severity: 'error',
        message: `Missing required category: ${category}`,
        field: category
      });
      continue;
    }

    const categoryData = metadata[category as keyof ProvenanceMetadata] as Record<string, unknown>;
    for (const field of fields) {
      if (!categoryData || !(field in categoryData)) {
        errors.push({
          severity: 'error',
          message: `Missing required field: ${category}.${field}`,
          field: `${category}.${field}`
        });
      }
    }
  }

  // Check recommended fields
  for (const [category, fields] of Object.entries(RECOMMENDED_FIELDS)) {
    if (category in metadata) {
      const categoryData = metadata[category as keyof ProvenanceMetadata] as Record<string, unknown>;
      for (const field of fields) {
        if (!categoryData || !(field in categoryData)) {
          missingOptional.push(`${category}.${field}`);
        }
      }
    }
  }

  // Semantic validation
  if (metadata.use) {
    // If sensitiveData is true, require sensitiveDataCategories
    if (metadata.use.sensitiveData === true) {
      if (!metadata.use.sensitiveDataCategories || metadata.use.sensitiveDataCategories.length === 0) {
        errors.push({
          severity: 'error',
          message: 'sensitiveDataCategories is required when sensitiveData is true',
          field: 'use.sensitiveDataCategories'
        });
      }

      if (!metadata.use.privacyMeasures || metadata.use.privacyMeasures.length === 0) {
        warnings.push({
          severity: 'warning',
          message: 'privacyMeasures strongly recommended when sensitiveData is true',
          field: 'use.privacyMeasures'
        });
      }
    }
  }

  // Data type validation
  if (metadata.provenance?.dataType) {
    const dataType = metadata.provenance.dataType;
    if (!VALID_DATA_TYPES.includes(dataType)) {
      warnings.push({
        severity: 'warning',
        message: `dataType '${dataType}' not in standard types: ${VALID_DATA_TYPES.join(', ')}`,
        field: 'provenance.dataType'
      });
    }
  }

  // Date validation
  if (metadata.provenance?.dateDataGenerated) {
    const dateStr = metadata.provenance.dateDataGenerated;
    if (!isValidISO8601Date(dateStr)) {
      warnings.push({
        severity: 'warning',
        message: `dateDataGenerated should be in ISO 8601 format (e.g., 2024-01-15T00:00:00Z)`,
        field: 'provenance.dateDataGenerated'
      });
    }
  }

  if (metadata.source?.dateAcquired) {
    const dateStr = metadata.source.dateAcquired;
    if (!isValidISO8601Date(dateStr)) {
      warnings.push({
        severity: 'warning',
        message: `dateAcquired should be in ISO 8601 format`,
        field: 'source.dateAcquired'
      });
    }
  }

  // Calculate compliance score
  const totalRequired = Object.values(REQUIRED_FIELDS).flat().length;
  const totalRecommended = Object.values(RECOMMENDED_FIELDS).flat().length;
  const totalFields = totalRequired + totalRecommended;

  const presentFields = totalFields - errors.length - missingOptional.length;
  const score = totalFields > 0 ? presentFields / totalFields : 0.0;

  const isValid = errors.length === 0;

  return {
    isValid,
    errors,
    warnings,
    missingOptionalFields: missingOptional,
    score
  };
}

/**
 * Validate ISO 8601 date format.
 */
function isValidISO8601Date(dateStr: string): boolean {
  const iso8601Regex = /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$/;
  if (!iso8601Regex.test(dateStr)) {
    return false;
  }

  const date = new Date(dateStr);
  return !isNaN(date.getTime());
}

/**
 * Format validation report for display.
 */
export function formatValidationReport(report: ValidationReport): string {
  const status = report.isValid ? '✅ VALID' : '❌ INVALID';
  let output = `DTA Standards Validation: ${status}\n`;
  output += `Compliance Score: ${(report.score * 100).toFixed(1)}%\n\n`;

  if (report.errors.length > 0) {
    output += 'Errors:\n';
    for (const error of report.errors) {
      output += `  ❌ ${error.message}\n`;
    }
    output += '\n';
  }

  if (report.warnings.length > 0) {
    output += 'Warnings:\n';
    for (const warning of report.warnings) {
      output += `  ⚠️  ${warning.message}\n`;
    }
    output += '\n';
  }

  if (report.missingOptionalFields.length > 0) {
    output += 'Missing Optional Fields (recommended):\n';
    for (const field of report.missingOptionalFields) {
      output += `  ℹ️  ${field}\n`;
    }
  }

  return output;
}
