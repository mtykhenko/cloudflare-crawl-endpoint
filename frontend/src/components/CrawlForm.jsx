/**
 * CrawlForm component - Form for initiating web crawls
 */
import { useState } from 'react';
import './CrawlForm.css';

const CrawlForm = ({ onSubmit, isLoading }) => {
  const [url, setUrl] = useState('');
  const [depth, setDepth] = useState(2);
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};

    // Validate URL
    if (!url.trim()) {
      newErrors.url = 'URL is required';
    } else {
      try {
        const urlObj = new URL(url);
        if (!['http:', 'https:'].includes(urlObj.protocol)) {
          newErrors.url = 'URL must use http or https protocol';
        }
      } catch (e) {
        newErrors.url = 'Please enter a valid URL';
      }
    }

    // Validate depth
    if (depth < 1 || depth > 100) {
      newErrors.depth = 'Depth must be between 1 and 100';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      onSubmit({ url: url.trim(), depth: parseInt(depth, 10) });
    }
  };

  const handleUrlChange = (e) => {
    setUrl(e.target.value);
    if (errors.url) {
      setErrors({ ...errors, url: null });
    }
  };

  const handleDepthChange = (e) => {
    setDepth(e.target.value);
    if (errors.depth) {
      setErrors({ ...errors, depth: null });
    }
  };

  return (
    <div className="crawl-form-container">
      <h2>🕷️ Web Crawler</h2>
      <p className="form-description">
        Enter a URL to crawl and specify the maximum depth of links to follow.
      </p>
      
      <form onSubmit={handleSubmit} className="crawl-form">
        <div className="form-group">
          <label htmlFor="url">
            Website URL <span className="required">*</span>
          </label>
          <input
            type="text"
            id="url"
            value={url}
            onChange={handleUrlChange}
            placeholder="https://example.com"
            disabled={isLoading}
            className={errors.url ? 'error' : ''}
          />
          {errors.url && <span className="error-message">{errors.url}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="depth">
            Crawl Depth <span className="required">*</span>
          </label>
          <input
            type="number"
            id="depth"
            value={depth}
            onChange={handleDepthChange}
            min="1"
            max="100"
            disabled={isLoading}
            className={errors.depth ? 'error' : ''}
          />
          <span className="help-text">
            Maximum number of link levels to follow (1-100)
          </span>
          {errors.depth && <span className="error-message">{errors.depth}</span>}
        </div>

        <button 
          type="submit" 
          className="submit-button"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <span className="spinner"></span>
              Crawling...
            </>
          ) : (
            <>
              <span>🚀</span>
              Start Crawl
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default CrawlForm;
