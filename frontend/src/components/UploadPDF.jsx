import React, { useState } from "react";
import { uploadPDF } from "../api";
import { toast } from "react-toastify";

const UploadPDF = ({ setFileName }) => {
  const [file, setFile] = useState(null);
  const [aiapiKey, setAIApiKey] = useState("");

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file || !aiapiKey) {
      toast.error("Please select a file and enter an API key.");
      return;
    }

    try {
      const response = await uploadPDF(file, aiapiKey);
      setFileName(file.name);
      toast.success(response.data.message);
    } catch (error) {
      toast.error("Upload failed: " + error.response?.data?.detail);
    }
  };

  return (
    <div>
      <h2>Upload PDF</h2>
      <input type="file" accept="application/pdf" onChange={handleFileChange} />
      <input
        type="text"
        placeholder="Enter OpenAI API Key"
        value={aiapiKey}
        onChange={(e) => setAIApiKey(e.target.value)}
      />
      <button onClick={handleUpload}>Upload</button>
    </div>
  );
};

export default UploadPDF;