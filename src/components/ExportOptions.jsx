import React from 'react';
import '../styles/components.css';

function ExportOptions({ onExport, loading }) {
  return (
    <div className="export-container">
      <h3>Export Options</h3>
      <div className="export-buttons">
        <button 
          className="export-button csv" 
          onClick={() => onExport('csv')}
          disabled={loading}
        >
          {loading ? 'Exporting...' : 'Export as CSV'}
        </button>
        
        <button 
          className="export-button excel" 
          onClick={() => onExport('excel')}
          disabled={loading}
        >
          {loading ? 'Exporting...' : 'Export as Excel'}
        </button>
      </div>
      <p className="export-help">
        Download the extracted data in your preferred format
      </p>
    </div>
  );
}

export default ExportOptions;