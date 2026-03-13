/**
 * MarkdownViewer component - Displays crawl results in markdown format
 */
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './MarkdownViewer.css';

const MarkdownViewer = ({ results }) => {
  const [expandedPages, setExpandedPages] = useState(new Set([0])); // First page expanded by default
  const [copiedUrl, setCopiedUrl] = useState(null);

  const togglePage = (index) => {
    const newExpanded = new Set(expandedPages);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedPages(newExpanded);
  };

  const expandAll = () => {
    setExpandedPages(new Set(results.map((_, i) => i)));
  };

  const collapseAll = () => {
    setExpandedPages(new Set());
  };

  const copyToClipboard = async (text, url) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedUrl(url);
      setTimeout(() => setCopiedUrl(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      completed: { label: 'Completed', color: '#27ae60' },
      queued: { label: 'Queued', color: '#3498db' },
      disallowed: { label: 'Disallowed', color: '#e67e22' },
      skipped: { label: 'Skipped', color: '#95a5a6' },
      errored: { label: 'Error', color: '#e74c3c' },
      cancelled: { label: 'Cancelled', color: '#95a5a6' },
    };

    const badge = badges[status] || { label: status, color: '#95a5a6' };
    
    return (
      <span 
        className="status-badge"
        style={{ backgroundColor: badge.color }}
      >
        {badge.label}
      </span>
    );
  };

  if (!results || results.length === 0) {
    return (
      <div className="markdown-viewer empty">
        <p className="empty-message">No results yet. Start a crawl to see content here.</p>
      </div>
    );
  }

  return (
    <div className="markdown-viewer">
      <div className="viewer-header">
        <h2>📄 Crawl Results ({results.length} pages)</h2>
        <div className="viewer-actions">
          <button onClick={expandAll} className="action-button">
            Expand All
          </button>
          <button onClick={collapseAll} className="action-button">
            Collapse All
          </button>
        </div>
      </div>

      <div className="results-list">
        {results.map((result, index) => {
          const isExpanded = expandedPages.has(index);
          const hasContent = result.markdown && result.markdown.trim().length > 0;

          return (
            <div key={index} className="result-item">
              <div 
                className="result-header"
                onClick={() => togglePage(index)}
              >
                <div className="result-header-left">
                  <span className="expand-icon">
                    {isExpanded ? '▼' : '▶'}
                  </span>
                  <div className="result-info">
                    <h3 className="result-title">
                      {result.metadata?.title || 'Untitled Page'}
                    </h3>
                    <a 
                      href={result.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="result-url"
                      onClick={(e) => e.stopPropagation()}
                    >
                      {result.url}
                    </a>
                  </div>
                </div>
                <div className="result-header-right">
                  {getStatusBadge(result.status)}
                  {result.metadata?.status && (
                    <span className="http-status">
                      HTTP {result.metadata.status}
                    </span>
                  )}
                </div>
              </div>

              {isExpanded && (
                <div className="result-content">
                  {hasContent ? (
                    <>
                      <div className="content-actions">
                        <button
                          onClick={() => copyToClipboard(result.markdown, result.url)}
                          className="copy-button"
                        >
                          {copiedUrl === result.url ? '✓ Copied!' : '📋 Copy Markdown'}
                        </button>
                      </div>
                      <div className="markdown-content">
                        <ReactMarkdown>{result.markdown}</ReactMarkdown>
                      </div>
                    </>
                  ) : (
                    <div className="no-content">
                      <p>No content available for this page.</p>
                      {result.status === 'disallowed' && (
                        <p className="hint">This page was blocked by robots.txt</p>
                      )}
                      {result.status === 'errored' && (
                        <p className="hint">An error occurred while crawling this page</p>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default MarkdownViewer;
