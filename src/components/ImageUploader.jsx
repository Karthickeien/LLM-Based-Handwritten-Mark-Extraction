import React, { useState, useRef } from 'react';
import '../styles/components.css';

function ImageUploader({ onSubmit, loading }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      
      // Create image preview
      const reader = new FileReader();
      reader.onload = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
      
      // Create image preview
      const reader = new FileReader();
      reader.onload = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedFile) {
      onSubmit(selectedFile);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="uploader-container">
      <h2>Upload Marksheet Image</h2>
      <div 
        className="drop-area"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={triggerFileInput}
      >
        {preview ? (
          <div className="preview-container">
            <img src={preview} alt="Preview" className="image-preview" />
            <p>{selectedFile.name}</p>
          </div>
        ) : (
          <div className="upload-prompt">
            <i className="upload-icon">📁</i>
            <p>Drag and drop a marksheet image here or click to select</p>
          </div>
        )}
        <input 
          type="file" 
          ref={fileInputRef}
          onChange={handleFileChange} 
          accept="image/*" 
          className="file-input"
        />
      </div>
      
      <button 
        className="submit-button" 
        onClick={handleSubmit} 
        disabled={!selectedFile || loading}
      >
        {loading ? 'Processing...' : 'Extract Marks'}
      </button>
      
      <p className="help-text">
        Upload a clear image of a completed marksheet to extract the marks data.
      </p>
    </div>
  );
}

export default ImageUploader;