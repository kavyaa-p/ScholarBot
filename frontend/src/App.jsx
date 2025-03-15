import  { useState } from "react";
import UploadPDF from "./components/UploadPDF";
import QueryPDF from "./components/QueryPDF";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const App = () => {
  const [fileName, setFileName] = useState("");

  return (
    <div>
      <h1>PDF Chatbot</h1>
      <UploadPDF setFileName={setFileName} />
      {fileName && <QueryPDF fileName={fileName} />}
      <ToastContainer position="top-right" />
    </div>
  );
};

export default App;