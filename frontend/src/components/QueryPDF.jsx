import { useState } from "react";
import { queryPDF } from "../api";
import { toast } from "react-toastify";

const QueryPDF = ({ fileName }) => {
  const [query, setQuery] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [response, setResponse] = useState(null);

  const handleQuery = async () => {
    if (!query || !fileName || !apiKey) {
      toast.error("Please enter a query, API key, and ensure a PDF is uploaded.");
      return;
    }

    try {
      const res = await queryPDF(query, fileName, apiKey);
      setResponse(res.data);
    } catch (error) {
      toast.error("Query failed: " + error.response?.data?.detail);
    }
  };

  return (
    <div>
      <h2>Ask a Question</h2>
      <input
        type="text"
        placeholder="Enter your question"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <input
        type="text"
        placeholder="Enter OpenAI API Key"
        value={apiKey}
        onChange={(e) => setApiKey(e.target.value)}
      />
      <button onClick={handleQuery}>Ask</button>

      {response && (
        <div>
          <h3>Answer:</h3>
          <p>{response.answer}</p>
        </div>
      )}
    </div>
  );
};

export default QueryPDF;