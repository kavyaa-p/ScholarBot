import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000"; // Adjust for deployment

export const uploadPDF = async (file, apiKey) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("api_key", apiKey);

  return axios.post(`${API_BASE_URL}/upload/`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const queryPDF = async (query, fileName, apiKey) => {
  return axios.post(`${API_BASE_URL}/query/`, {
    query,
    file_name: fileName,
    api_key: apiKey,
  });
};