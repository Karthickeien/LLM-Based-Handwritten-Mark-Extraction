import React from 'react';
import '../styles/components.css';

function ResultsDisplay({ results }) {
  const { SI_No, Question_Nos, Subtotal } = results;
  
  // Sort question numbers numerically
  const sortedQuestions = Object.entries(Question_Nos || {}).sort((a, b) => {
    const numA = parseInt(a[0], 10);
    const numB = parseInt(b[0], 10);
    return isNaN(numA) || isNaN(numB) ? a[0].localeCompare(b[0]) : numA - numB;
  });

  return (
    <div className="results-container">
      <h2>Extracted Marksheet Data</h2>
      
      {SI_No && (
        <div className="result-item">
          <span className="label">Serial Number:</span>
          <span className="value">{SI_No}</span>
        </div>
      )}
      
      <div className="questions-container">
        <h3>Question Marks</h3>
        <div className="questions-grid">
          {sortedQuestions.map(([qNum, marks]) => (
            <div key={qNum} className="question-item">
              <span className="q-label">Q{qNum}:</span>
              <span className="q-value">{marks}</span>
            </div>
          ))}
        </div>
      </div>
      
      {Subtotal !== undefined && (
        <div className="result-item subtotal">
          <span className="label">Subtotal:</span>
          <span className="value">{Subtotal}</span>
        </div>
      )}
    </div>
  );
}

export default ResultsDisplay;