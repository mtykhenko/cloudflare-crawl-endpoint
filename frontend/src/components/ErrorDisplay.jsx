/**
 * ErrorDisplay component - Displays error messages with retry option
 */
import './ErrorDisplay.css';

const ErrorDisplay = ({ error, onRetry, onClear }) => {
  if (!error) return null;

  const getErrorIcon = () => {
    if (error.status === 401 || error.status === 403) return '🔒';
    if (error.status === 429) return '⏱️';
    if (error.status === 404) return '🔍';
    if (error.status >= 500) return '🔧';
    return '⚠️';
  };

  const getErrorTitle = () => {
    if (error.status === 401 || error.status === 403) return 'Authentication Error';
    if (error.status === 429) return 'Rate Limit Exceeded';
    if (error.status === 404) return 'Not Found';
    if (error.status >= 500) return 'Server Error';
    return 'Error';
  };

  return (
    <div className="error-display">
      <div className="error-content">
        <span className="error-icon">{getErrorIcon()}</span>
        <div className="error-text">
          <h3 className="error-title">{getErrorTitle()}</h3>
          <p className="error-message">{error.message}</p>
          {error.code && (
            <p className="error-code">Error Code: {error.code}</p>
          )}
        </div>
      </div>
      <div className="error-actions">
        {onRetry && (
          <button onClick={onRetry} className="retry-button">
            🔄 Retry
          </button>
        )}
        {onClear && (
          <button onClick={onClear} className="clear-button">
            ✕ Dismiss
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorDisplay;
