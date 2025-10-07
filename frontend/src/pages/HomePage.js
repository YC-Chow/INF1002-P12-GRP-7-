import React, { useEffect, useState } from "react";

function HomePage() {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchEmails = () => {
    setLoading(true);
    fetch("http://localhost:5000/emails")
      .then((res) => res.json())
      .then((data) => {
        setEmails(data);
        setLoading(false);
      })
      .catch((err) => console.error(err));
  };

  useEffect(() => {
    fetchEmails();
  }, []);

  if (loading) return <p className="text-center mt-10">Loading emails...</p>;

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h2 className="text-2xl font-semibold text-center mb-4">
        Random Email Risk Scores
      </h2>
      <button
        onClick={fetchEmails}
        className="bg-blue-500 text-white px-4 py-2 rounded mb-6"
      >
        🔄 Refresh Emails
      </button>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {emails.map((email, index) => {
          const risk = email.riskScore;
          let color =
            risk >= 10 ? "bg-red-200" : risk >= 5 ? "bg-yellow-200" : "bg-green-200";

          return (
            <div
              key={index}
              className={`rounded-xl shadow-md p-4 ${color}`}
            >
              <h2 className="font-semibold">{email.sender}</h2>
              <p className="text-sm mt-1">
                <strong>Subject:</strong> {email.subject || "(No subject)"}
              </p>
              <p className="text-sm mt-2">
                <strong>Risk Score:</strong> {email.riskScore}
              </p>
              <p className="text-sm mt-1">
                <strong>Whitelisted:</strong>{" "}
                {email.is_whitelisted ? "✅ Yes" : "❌ No"}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default HomePage;