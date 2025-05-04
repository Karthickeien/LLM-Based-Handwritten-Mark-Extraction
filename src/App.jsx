import React, { useState } from 'react';
import Header from './components/Header';
import ImageUploader from './components/ImageUploader';
import ResultsDisplay from './components/ResultsDisplay';
import ExportOptions from './components/ExportOptions';
import './styles/App.css';

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const handleImageSubmit = async (imageFile) => {
    setLoading(true);
    setError(null);
    setResults(null);
    setUploadSuccess(false);

    try {
      const formData = new FormData();
      formData.append('image', imageFile);

      const response = await fetch('http://localhost:5000/api/process-image', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to process image');
      }

      const data = await response.json();
      setResults(data);
      setUploadSuccess(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    if (!results) return;

    try {
      setLoading(true);
      
      const endpoint = format === 'csv' 
        ? 'http://localhost:5000/api/export-csv'
        : 'http://localhost:5000/api/export-excel';

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(results),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Failed to export as ${format.toUpperCase()}`);
      }

      // Handle file download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = format === 'csv' ? 'marksheet_results.csv' : 'marksheet_results.xlsx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Header />
      <main className="main-content">
        <ImageUploader onSubmit={handleImageSubmit} loading={loading} />
        
        {error && (
          <div className="error-message">
            Error: {error}
          </div>
        )}
        
        {results && (
          <>
            <ResultsDisplay results={results} />
            <ExportOptions onExport={handleExport} loading={loading} />
          </>
        )}
      </main>
    </div>
  );
}

export default App;