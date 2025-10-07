import React, { useState } from "react";

function AnalyzePage() {
  const [formData, setFormData] = useState({
    sender: "",
    subject: "",
    body: "",
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    fetch("http://localhost:5000/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    })
      .then((res) => res.json())
      .then((data) => {
        setResult(data);
        setLoading(false);
      })
      .catch((err) => console.error(err));
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h2 className="text-2xl font-semibold text-center mb-4">
        Analyze Custom Email
      </h2>

      <form
        onSubmit={handleSubmit}
        className="max-w-lg mx-auto bg-white p-6 rounded-lg shadow-md"
      >
        <label className="block mb-2 font-medium">Sender:</label>
        <input
          type="text"
          name="sender"
          value={formData.sender}
          onChange={handleChange}
          className="w-full border p-2 mb-4 rounded"
          placeholder="e.g., support@paypa1.com"
          required
        />

        <label className="block mb-2 font-medium">Subject:</label>
        <input
          type="text"
          name="subject"
          value={formData.subject}
          onChange={handleChange}
          className="w-full border p-2 mb-4 rounded"
        />

        <label className="block mb-2 font-medium">Body:</label>
        <textarea
          name="body"
          value={formData.body}
          onChange={handleChange}
          className="w-full border p-2 mb-4 rounded"
          rows="5"
        />

        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          {loading ? "Analyzing..." : "Analyze Email"}
        </button>
      </form>

      {result && (
        <div className="max-w-lg mx-auto mt-6 bg-gray-200 p-4 rounded">
          <h3 className="font-semibold mb-2">Result:</h3>
          <p><strong>Sender:</strong> {result.sender}</p>
          <p><strong>Subject:</strong> {result.subject}</p>
          <p><strong>Risk Score:</strong> {result.riskScore}</p>
          <p><strong>Whitelisted:</strong> {result.is_whitelisted ? "✅ Yes" : "❌ No"}</p>
        </div>
      )}
    </div>
  );
}

export default AnalyzePage;