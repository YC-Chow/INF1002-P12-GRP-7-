import React, { useState } from "react";

function AnalyzePage() {
  const [formData, setFormData] = useState({
    sender: "",
    subject: "",
    body: "",
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");
    setResult(null);

    try {
      const res = await fetch("http://localhost:5000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setErrorMsg("Something went wrong analyzing this email. Please try again.");
    } finally {
      setLoading(false);
    }
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

        <div className="flex items-center gap-3">
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-60"
            disabled={loading}
          >
            {loading ? "Analyzing..." : "Analyze Email"}
          </button>
          <button
            type="button"
            onClick={() => {
              setFormData({ sender: "", subject: "", body: "" });
              setResult(null);
              setErrorMsg("");
            }}
            className="px-3 py-2 rounded border"
          >
            Reset
          </button>
        </div>

        {errorMsg && (
          <p className="text-red-600 mt-3">{errorMsg}</p>
        )}
      </form>

      {/* Full Analysis (mirrors HomePage full analysis) */}
      {result && (
        <div className="max-w-3xl mx-auto mt-6 bg-white border rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold mb-4">Full Analysis</h3>

          <div className="space-y-2">
            <p><span className="font-semibold">Sender:</span> {result.sender}</p>
            <p><span className="font-semibold">Subject:</span> {result.subject}</p>
            <p><span className="font-semibold">Body:</span> {result.body || <em>(no body)</em>}</p>
            <p><span className="font-semibold">Total Risk Score:</span> {result.riskScore}</p>
            <p>
              <span className="font-semibold">Whitelisted:</span>{" "}
              {result.is_whitelisted ? "✅ Yes" : "❌ No"}
            </p>
          </div>

          <div className="mt-5">
            <h4 className="font-semibold mb-2">Risk Breakdown:</h4>
            {result.risk_breakdown ? (
              <ul className="list-disc pl-6">
                {Object.entries(result.risk_breakdown).map(([k, v]) => (
                  <li key={k}>
                    {k}: {v}
                  </li>
                ))}
              </ul>
            ) : (
              <p>No breakdown available.</p>
            )}
          </div>

          <div className="mt-5">
            <h4 className="font-semibold mb-2">Keywords Detected:</h4>
            {Array.isArray(result.keywords) && result.keywords.length > 0 ? (
              <ul className="list-disc pl-6">
                {result.keywords.map((kw, i) => (
                  <li key={`${kw}-${i}`}>{kw}</li>
                ))}
              </ul>
            ) : (
              <p>No keywords detected.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default AnalyzePage;