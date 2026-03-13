/**
 * StatusIndicator component - Displays crawl job status and progress
 */
import './StatusIndicator.css';

const StatusIndicator = ({ status, total, finished, browserSecondsUsed }) => {
  const getStatusInfo = () => {
    switch (status) {
      case 'running':
        return {
          icon: '⏳',
          label: 'Crawling in Progress',
          color: '#3498db',
          description: 'Discovering and processing pages...'
        };
      case 'completed':
        return {
          icon: '✅',
          label: 'Crawl Completed',
          color: '#27ae60',
          description: 'All pages have been processed successfully'
        };
      case 'errored':
        return {
          icon: '❌',
          label: 'Crawl Failed',
          color: '#e74c3c',
          description: 'An error occurred during crawling'
        };
      case 'cancelled_by_user':
        return {
          icon: '🛑',
          label: 'Cancelled by User',
          color: '#95a5a6',
          description: 'Crawl was cancelled'
        };
      case 'cancelled_due_to_timeout':
        return {
          icon: '⏰',
          label: 'Timeout',
          color: '#e67e22',
          description: 'Crawl exceeded maximum runtime (7 days)'
        };
      case 'cancelled_due_to_limits':
        return {
          icon: '⚠️',
          label: 'Limit Reached',
          color: '#e67e22',
          description: 'Account limits were exceeded'
        };
      default:
        return {
          icon: '❓',
          label: 'Unknown Status',
          color: '#95a5a6',
          description: 'Status information unavailable'
        };
    }
  };

  const statusInfo = getStatusInfo();
  const progress = total > 0 ? (finished / total) * 100 : 0;

  return (
    <div className="status-indicator">
      <div className="status-header">
        <span className="status-icon" style={{ color: statusInfo.color }}>
          {statusInfo.icon}
        </span>
        <div className="status-text">
          <h3 style={{ color: statusInfo.color }}>{statusInfo.label}</h3>
          <p className="status-description">{statusInfo.description}</p>
        </div>
      </div>

      {total > 0 && (
        <div className="progress-section">
          <div className="progress-info">
            <span className="progress-label">Progress</span>
            <span className="progress-numbers">
              {finished} / {total} pages
            </span>
          </div>
          
          <div className="progress-bar-container">
            <div 
              className="progress-bar"
              style={{ 
                width: `${progress}%`,
                backgroundColor: statusInfo.color
              }}
            />
          </div>
          
          <div className="progress-percentage">
            {progress.toFixed(1)}%
          </div>
        </div>
      )}

      {browserSecondsUsed !== null && browserSecondsUsed !== undefined && (
        <div className="browser-time">
          <span className="browser-time-label">Browser Time Used:</span>
          <span className="browser-time-value">
            {browserSecondsUsed.toFixed(2)}s
          </span>
        </div>
      )}
    </div>
  );
};

export default StatusIndicator;
