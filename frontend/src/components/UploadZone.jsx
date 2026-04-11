import { useState, useRef, useCallback } from "react";

export default function UploadZone({ onFileSelect, disabled }) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  const handleFile = useCallback(
    (file) => {
      if (file && file.type.startsWith("image/")) {
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      handleFile(file);
    },
    [handleFile]
  );

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  return (
    <div>
      <div
        className={`upload-zone ${isDragging ? "upload-zone--active" : ""}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="upload-zone__icon">📋</div>
        <div className="upload-zone__text">
          Drop your prescription image here
        </div>
        <div className="upload-zone__hint">
          or click to browse &middot; JPG, PNG, WebP &middot; Max 10 MB
        </div>
        <input
          ref={fileInputRef}
          type="file"
          className="upload-zone__input"
          accept="image/*"
          onChange={(e) => handleFile(e.target.files[0])}
          disabled={disabled}
        />
      </div>

      <div className="camera-row">
        <button
          className="btn btn--primary"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
        >
          📁 Upload Image
        </button>
        <button
          className="btn btn--secondary"
          onClick={() => cameraInputRef.current?.click()}
          disabled={disabled}
        >
          📷 Take Photo
        </button>
        <input
          ref={cameraInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          style={{ display: "none" }}
          onChange={(e) => handleFile(e.target.files[0])}
          disabled={disabled}
        />
      </div>
    </div>
  );
}
