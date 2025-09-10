import React, { useState } from 'react';
import './App.css';

function App() {
  const [emailText, setEmailText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('http://localhost:5000/detect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: emailText }),
      });

      const data = await response.json();
      setResult(data.result);
    } catch (error) {
      console.error('Error:', error);
      setResult('Error detecting phishing.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <h1>Email Phishing Detection</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          rows="10"
          placeholder="Paste your email content here..."
          value={emailText}
          onChange={(e) => setEmailText(e.target.value)}
        />
        <button type="submit" disabled={loading || !emailText.trim()}>
          {loading ? 'Analyzing...' : 'Check Email'}
        </button>
      </form>
      {result && (
        <div className={`result ${result === 'phishing' ? 'phishing' : 'safe'}`}>
          {result === 'phishing' ? '⚠️ Phishing Email Detected!' : '✅ Email Looks Safe'}
        </div>
      )}
    </div>
  );
}

export default App;