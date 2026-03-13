/**
 * Main App component - Web Crawler Application
 */
import { useState, useEffect, useRef } from 'react';
import CrawlForm from './components/CrawlForm';
import StatusIndicator from './components/StatusIndicator';
import MarkdownViewer from './components/MarkdownViewer';
import ErrorDisplay from './components/ErrorDisplay';
import { initiateCrawl, getJobStatus } from './services/api';
import './App.css';

function App() {
  // State management
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [crawlParams, setCrawlParams] = useState(null);

  // Ref for polling interval
  const pollingIntervalRef = useRef(null);

  // Poll job status when job is running
  useEffect(() => {
    if (jobId && jobStatus?.status === 'running') {
      // Start polling every 3 seconds
      pollingIntervalRef.current = setInterval(async () => {
        try {
          const status = await getJobStatus(jobId);
          setJobStatus(status);
          setResults(status.results || []);

          // Stop polling if job is no longer running
          if (status.status !== 'running') {
            clearInterval(pollingIntervalRef.current);
            setIsLoading(false);
          }
        } catch (err) {
          console.error('Error polling job status:', err);
          setError(err);
          clearInterval(pollingIntervalRef.current);
          setIsLoading(false);
        }
      }, 3000);

      // Cleanup on unmount or when dependencies change
      return () => {
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
        }
      };
    }
  }, [jobId, jobStatus?.status]);

  const handleCrawlSubmit = async (params) => {
    setError(null);
    setIsLoading(true);
    setCrawlParams(params);
    setResults([]);
    setJobStatus(null);

    try {
      console.log('Initiating crawl with params:', params);
      const response = await initiateCrawl(params.url, params.depth);
      
      setJobId(response.job_id);
      setJobStatus({
        job_id: response.job_id,
        status: response.status,
        total: 0,
        finished: 0,
        results: []
      });

      console.log('Crawl initiated successfully:', response);
    } catch (err) {
      console.error('Error initiating crawl:', err);
      setError(err);
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    if (crawlParams) {
      handleCrawlSubmit(crawlParams);
    }
  };

  const handleClearError = () => {
    setError(null);
  };

  const handleNewCrawl = () => {
    // Clear polling interval if active
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    // Reset all state
    setJobId(null);
    setJobStatus(null);
    setResults([]);
    setError(null);
    setIsLoading(false);
    setCrawlParams(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🕷️ Web Crawler</h1>
        <p className="app-subtitle">Powered by Cloudflare Browser Rendering</p>
      </header>

      <main className="app-main">
        {error && (
          <ErrorDisplay 
            error={error} 
            onRetry={handleRetry}
            onClear={handleClearError}
          />
        )}

        {!jobId ? (
          <CrawlForm 
            onSubmit={handleCrawlSubmit}
            isLoading={isLoading}
          />
        ) : (
          <>
            <div className="crawl-info">
              <div className="crawl-info-header">
                <div>
                  <h3>Current Crawl</h3>
                  <p className="crawl-url">{crawlParams?.url}</p>
                  <p className="crawl-depth">Depth: {crawlParams?.depth}</p>
                </div>
                <button 
                  onClick={handleNewCrawl}
                  className="new-crawl-button"
                  disabled={isLoading && jobStatus?.status === 'running'}
                >
                  🆕 New Crawl
                </button>
              </div>
            </div>

            {jobStatus && (
              <StatusIndicator
                status={jobStatus.status}
                total={jobStatus.total}
                finished={jobStatus.finished}
                browserSecondsUsed={jobStatus.browser_seconds_used}
              />
            )}

            <MarkdownViewer results={results} />
          </>
        )}
      </main>

      <footer className="app-footer">
        <p>
          Built with React + FastAPI | 
          <a 
            href="https://developers.cloudflare.com/browser-rendering/" 
            target="_blank" 
            rel="noopener noreferrer"
          >
            {' '}Cloudflare Browser Rendering API
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
