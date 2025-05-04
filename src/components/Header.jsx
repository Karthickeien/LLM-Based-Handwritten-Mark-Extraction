import React from 'react';
import '../styles/components.css';

function Header() {
  return (
    <header className="app-header">
      <h1>Marksheet Data Extractor</h1>
      <p className="header-subtitle">
        Upload images of marksheets to extract and export mark data
      </p>
    </header>
  );
}

export default Header;