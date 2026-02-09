/**
 * VS Code extension for DTA provenance validation and Git integration.
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';
import { validateDTACompliance, formatValidationReport, ProvenanceMetadata } from './validator';

const execAsync = promisify(exec);

let statusBarItem: vscode.StatusBarItem;
let diagnosticCollection: vscode.DiagnosticCollection;

export function activate(context: vscode.ExtensionContext) {
  console.log('DTA Provenance Validator is now active');

  // Create diagnostic collection for inline error reporting
  diagnosticCollection = vscode.languages.createDiagnosticCollection('dta-provenance');
  context.subscriptions.push(diagnosticCollection);

  // Create status bar item
  statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBarItem.command = 'dta.validateFile';
  context.subscriptions.push(statusBarItem);

  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand('dta.validateFile', validateCurrentFile)
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('dta.showProvenance', showGitProvenance)
  );

  // Listen for document saves
  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument(onDocumentSave)
  );

  // Listen for active editor changes
  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor(updateStatusBar)
  );

  // Initial status bar update
  updateStatusBar();
}

export function deactivate() {
  if (statusBarItem) {
    statusBarItem.dispose();
  }
  if (diagnosticCollection) {
    diagnosticCollection.dispose();
  }
}

/**
 * Validate the currently active file.
 */
async function validateCurrentFile() {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showWarningMessage('No active editor');
    return;
  }

  const document = editor.document;
  if (document.languageId !== 'json') {
    vscode.window.showWarningMessage('Current file is not JSON');
    return;
  }

  await validateDocument(document);
}

/**
 * Validate a document and show results.
 */
async function validateDocument(document: vscode.TextDocument): Promise<void> {
  const fileName = path.basename(document.fileName);

  // Only validate files that look like provenance metadata
  if (!isProvenanceFile(fileName)) {
    diagnosticCollection.delete(document.uri);
    return;
  }

  try {
    const text = document.getText();
    const metadata: ProvenanceMetadata = JSON.parse(text);

    const report = validateDTACompliance(metadata);

    // Clear previous diagnostics
    diagnosticCollection.delete(document.uri);

    // Add new diagnostics
    const diagnostics: vscode.Diagnostic[] = [];

    for (const error of report.errors) {
      const range = findFieldRange(document, error.field);
      const diagnostic = new vscode.Diagnostic(
        range,
        error.message,
        vscode.DiagnosticSeverity.Error
      );
      diagnostic.source = 'DTA Provenance';
      diagnostics.push(diagnostic);
    }

    for (const warning of report.warnings) {
      const range = findFieldRange(document, warning.field);
      const diagnostic = new vscode.Diagnostic(
        range,
        warning.message,
        vscode.DiagnosticSeverity.Warning
      );
      diagnostic.source = 'DTA Provenance';
      diagnostics.push(diagnostic);
    }

    diagnosticCollection.set(document.uri, diagnostics);

    // Update status bar
    updateStatusBarForDocument(document, report.isValid, report.score);

    // Show output
    const outputChannel = vscode.window.createOutputChannel('DTA Provenance');
    outputChannel.clear();
    outputChannel.appendLine(formatValidationReport(report));
    outputChannel.show(true);

    // Show notification
    if (report.isValid) {
      vscode.window.showInformationMessage(
        `✅ DTA compliance: ${(report.score * 100).toFixed(1)}%`
      );
    } else {
      vscode.window.showErrorMessage(
        `❌ DTA validation failed: ${report.errors.length} error(s)`
      );
    }
  } catch (error) {
    if (error instanceof SyntaxError) {
      vscode.window.showErrorMessage(`JSON parse error: ${error.message}`);
    } else {
      vscode.window.showErrorMessage(`Validation error: ${error}`);
    }
  }
}

/**
 * Show Git provenance metadata for current file.
 */
async function showGitProvenance() {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showWarningMessage('No active editor');
    return;
  }

  const filePath = editor.document.fileName;
  const workspaceFolder = vscode.workspace.getWorkspaceFolder(editor.document.uri);

  if (!workspaceFolder) {
    vscode.window.showWarningMessage('File is not in a workspace');
    return;
  }

  try {
    // Get Git commits for this file
    const { stdout } = await execAsync(
      `git log --follow --pretty=format:"%H|%an|%ad|%s" --date=iso -- "${filePath}"`,
      { cwd: workspaceFolder.uri.fsPath }
    );

    if (!stdout) {
      vscode.window.showInformationMessage('No Git history found for this file');
      return;
    }

    const commits = stdout.split('\n').map(line => {
      const [hash, author, date, message] = line.split('|');
      return { hash, author, date, message };
    });

    // Check for DTA provenance in commits
    const provenanceCommits = [];
    for (const commit of commits) {
      const { stdout: commitMessage } = await execAsync(
        `git show --format=%B --no-patch ${commit.hash}`,
        { cwd: workspaceFolder.uri.fsPath }
      );

      if (commitMessage.includes('DTA-Provenance-Metadata:')) {
        const metadataLine = commitMessage
          .split('\n')
          .find(line => line.startsWith('DTA-Provenance-Metadata:'));

        if (metadataLine) {
          const jsonStr = metadataLine.substring('DTA-Provenance-Metadata:'.length).trim();
          try {
            const metadata = JSON.parse(jsonStr);
            provenanceCommits.push({
              ...commit,
              metadata
            });
          } catch {
            // Skip invalid JSON
          }
        }
      }
    }

    // Display results
    const panel = vscode.window.createWebviewPanel(
      'dtaProvenance',
      'DTA Provenance History',
      vscode.ViewColumn.Two,
      {}
    );

    panel.webview.html = generateProvenanceHTML(filePath, commits, provenanceCommits);

  } catch (error) {
    vscode.window.showErrorMessage(`Git error: ${error}`);
  }
}

/**
 * Handle document save events.
 */
async function onDocumentSave(document: vscode.TextDocument) {
  const config = vscode.workspace.getConfiguration('dta');
  const validateOnSave = config.get<boolean>('validateOnSave', true);

  if (!validateOnSave || document.languageId !== 'json') {
    return;
  }

  const fileName = path.basename(document.fileName);
  if (isProvenanceFile(fileName)) {
    await validateDocument(document);
  }
}

/**
 * Update status bar based on active editor.
 */
function updateStatusBar() {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    statusBarItem.hide();
    return;
  }

  const config = vscode.workspace.getConfiguration('dta');
  const showStatusBar = config.get<boolean>('showStatusBar', true);

  if (!showStatusBar) {
    statusBarItem.hide();
    return;
  }

  const fileName = path.basename(editor.document.fileName);
  if (isProvenanceFile(fileName) && editor.document.languageId === 'json') {
    statusBarItem.text = '$(checklist) DTA';
    statusBarItem.tooltip = 'Click to validate DTA provenance metadata';
    statusBarItem.show();
  } else {
    statusBarItem.hide();
  }
}

/**
 * Update status bar with validation results.
 */
function updateStatusBarForDocument(
  document: vscode.TextDocument,
  isValid: boolean,
  score: number
) {
  if (vscode.window.activeTextEditor?.document === document) {
    const icon = isValid ? '$(check)' : '$(error)';
    const scorePercent = (score * 100).toFixed(0);
    statusBarItem.text = `${icon} DTA ${scorePercent}%`;
    statusBarItem.tooltip = isValid
      ? `DTA compliant (${scorePercent}%)`
      : `DTA validation failed (${scorePercent}%)`;
    statusBarItem.show();
  }
}

/**
 * Check if filename suggests it's a provenance file.
 */
function isProvenanceFile(fileName: string): boolean {
  const lowerName = fileName.toLowerCase();
  return (
    lowerName.includes('provenance') ||
    lowerName.includes('dta-metadata') ||
    lowerName.includes('metadata')
  );
}

/**
 * Find the range of a field in the document for diagnostics.
 */
function findFieldRange(document: vscode.TextDocument, field?: string): vscode.Range {
  if (!field) {
    return new vscode.Range(0, 0, 0, 0);
  }

  const text = document.getText();
  const fieldPattern = new RegExp(`"${field.split('.').pop()}"\\s*:`, 'g');
  const match = fieldPattern.exec(text);

  if (match) {
    const pos = document.positionAt(match.index);
    return new vscode.Range(pos, pos.translate(0, match[0].length));
  }

  return new vscode.Range(0, 0, 0, 0);
}

/**
 * Generate HTML for provenance history webview.
 */
function generateProvenanceHTML(
  filePath: string,
  commits: any[],
  provenanceCommits: any[]
): string {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DTA Provenance History</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      color: var(--vscode-foreground);
      padding: 20px;
    }
    h1 { font-size: 1.5em; margin-bottom: 10px; }
    h2 { font-size: 1.2em; margin-top: 20px; }
    .file-path {
      color: var(--vscode-descriptionForeground);
      font-size: 0.9em;
      margin-bottom: 20px;
    }
    .commit {
      border: 1px solid var(--vscode-panel-border);
      border-radius: 4px;
      padding: 15px;
      margin-bottom: 15px;
      background: var(--vscode-editor-background);
    }
    .commit-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 10px;
    }
    .commit-hash {
      font-family: monospace;
      font-size: 0.9em;
    }
    .commit-date {
      color: var(--vscode-descriptionForeground);
      font-size: 0.9em;
    }
    .provenance-badge {
      display: inline-block;
      background: var(--vscode-badge-background);
      color: var(--vscode-badge-foreground);
      padding: 2px 8px;
      border-radius: 3px;
      font-size: 0.85em;
      margin-left: 10px;
    }
    pre {
      background: var(--vscode-textCodeBlock-background);
      padding: 10px;
      border-radius: 4px;
      overflow-x: auto;
      font-size: 0.9em;
    }
    .no-provenance {
      color: var(--vscode-descriptionForeground);
      font-style: italic;
    }
  </style>
</head>
<body>
  <h1>DTA Provenance History</h1>
  <div class="file-path">${filePath}</div>

  ${provenanceCommits.length > 0 ? `
    <h2>Commits with DTA Provenance (${provenanceCommits.length})</h2>
    ${provenanceCommits.map(commit => `
      <div class="commit">
        <div class="commit-header">
          <span class="commit-hash">${commit.hash.substring(0, 8)}</span>
          <span class="commit-date">${commit.date}</span>
        </div>
        <div><strong>${commit.author}</strong>: ${commit.message}</div>
        <div><span class="provenance-badge">DTA Provenance</span></div>
        <pre>${JSON.stringify(commit.metadata, null, 2)}</pre>
      </div>
    `).join('')}
  ` : `
    <div class="no-provenance">No commits with DTA provenance metadata found.</div>
  `}

  <h2>All Commits (${commits.length})</h2>
  ${commits.slice(0, 10).map(commit => `
    <div class="commit">
      <div class="commit-header">
        <span class="commit-hash">${commit.hash.substring(0, 8)}</span>
        <span class="commit-date">${commit.date}</span>
      </div>
      <div><strong>${commit.author}</strong>: ${commit.message}</div>
    </div>
  `).join('')}
  ${commits.length > 10 ? `<div class="no-provenance">Showing 10 of ${commits.length} commits</div>` : ''}
</body>
</html>
  `;
}
