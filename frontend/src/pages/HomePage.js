import React, { useEffect, useState } from "react";

export default function HomePage() {
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);

  // Fetch random emails
  const fetchEmails = async () => {
    const response = await fetch("http://localhost:5000/emails");
    const data = await response.json();
    setEmails(data);
    setSelectedEmail(null);
  };

  useEffect(() => {
    fetchEmails();
  }, []);


  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h2>Email Risk Analysis</h2>

      {/* Refresh Emails */}
      <button onClick={fetchEmails} style={{ padding: "10px 15px", marginBottom: "20px" }}>Refresh Emails</button>

      {/* Email List */}
      {!selectedEmail && emails.map((email, index) => (
        <div key={index} style={{ border: "1px solid #ccc", padding: "10px", marginBottom: "10px" }}>
          <p><strong>Sender:</strong> {email.sender}</p>
          <p><strong>Subject:</strong> {email.subject}</p>
          <p><strong>Risk Score:</strong> {email.riskScore}</p>
          <button onClick={() => setSelectedEmail(email)} style={{ padding: "5px 10px" }}>View Full Analysis</button>
        </div>
      ))}

      {/* Full Analysis */}
      {selectedEmail && (
        <div style={{ border: "1px solid #888", padding: "15px", marginTop: "20px" }}>
          <h3>Full Analysis</h3>
          <p><strong>Sender:</strong> {selectedEmail.sender}</p>
          <p><strong>Subject:</strong> {selectedEmail.subject}</p>
          <p><strong>Body:</strong> {selectedEmail.body}</p>
          <p><strong>Total Risk Score:</strong> {selectedEmail.riskScore}</p>
          <h4>Risk Breakdown:</h4>
          <ul>
            {Object.entries(selectedEmail.risk_breakdown).map(([key, value]) => (
              <li key={key}>{key}: {value}</li>
            ))}
          </ul>
          <h4>Keywords Detected:</h4>
          {selectedEmail.keywords.length > 0 ? (
            <ul>
              {selectedEmail.keywords.map((kw, i) => <li key={i}>{kw}</li>)}
            </ul>
          ) : <p>No keywords detected.</p>}
          <button onClick={() => setSelectedEmail(null)} style={{ padding: "10px 15px" }}>Close Full Analysis</button>
        </div>
      )}
    </div>
  );
}