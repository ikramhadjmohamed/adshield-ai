import { useState } from "react";
import axios from "axios";
import AdReviewForm from "./components/AdReviewForm";
import Adshielddashboard from "./components/Adshielddashboard";

const API_URL = `${import.meta.env.VITE_API_URL}/review-ad`;

export default function App() {
  const [ad, setAd] = useState(null);
  const [report, setReport] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(formData) {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post(API_URL, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setAd({
        brand_name: formData.get("brand_name"),
        headline: formData.get("headline"),
        landing_url: formData.get("landing_url"),
      });
      setReport(response.data);
    } catch (err) {
      setError(err.response?.data?.detail ?? "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

 return (
    <div
      className={`min-h-screen bg-[#14161C] flex flex-col ${
        report ? "justify-start pt-10" : "justify-center"
      }`}
    >
      <AdReviewForm onSubmit={handleSubmit} isLoading={isLoading} />

      {error && (
        <p className="max-w-5xl mx-auto text-center text-[#E4483C] font-mono text-sm mb-6">
          {String(error)}
        </p>
      )}

      {report && <Adshielddashboard ad={ad} report={report} />}
    </div>
  );
}
