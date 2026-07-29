import React, { useState } from "react";

export default function AdReviewForm({ onSubmit, isLoading }) {
  const [brandName, setBrandName] = useState("");
  const [headline, setHeadline] = useState("");
  const [description, setDescription] = useState("");
  const [landingUrl, setLandingUrl] = useState("");
  const [image, setImage] = useState(null);

  function handleSubmit(e) {
    e.preventDefault();
    const formData = new FormData();
    formData.append("brand_name", brandName);
    formData.append("headline", headline);
    formData.append("description", description);
    formData.append("landing_url", landingUrl);
    if (image) formData.append("image", image);
    onSubmit(formData);
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="max-w-5xl mx-auto mb-10 bg-[#1C1F27] border border-[#2A2E38] rounded-sm p-6 md:p-8 flex flex-col gap-4"
    >
      <h2 className="font-sans text-xs uppercase tracking-[0.2em] text-[#8B8F9B] mb-2">
        Submit Advertisement for Review
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <label className="flex flex-col gap-1">
          <span className="font-mono text-xs text-[#6B6F7A]">Brand name</span>
          <input
            required
            value={brandName}
            onChange={(e) => setBrandName(e.target.value)}
            className="bg-[#161821] border border-[#2A2E38] rounded-sm px-3 py-2 text-[#F1EFE9] font-sans text-sm focus:outline-none focus:border-[#4CAF7D]"
            placeholder="Nike"
          />
        </label>

        <label className="flex flex-col gap-1">
          <span className="font-mono text-xs text-[#6B6F7A]">Landing URL</span>
          <input
            required
            type="url"
            value={landingUrl}
            onChange={(e) => setLandingUrl(e.target.value)}
            className="bg-[#161821] border border-[#2A2E38] rounded-sm px-3 py-2 text-[#F1EFE9] font-sans text-sm focus:outline-none focus:border-[#4CAF7D]"
            placeholder="https://nike.com"
          />
        </label>
      </div>

      <label className="flex flex-col gap-1">
        <span className="font-mono text-xs text-[#6B6F7A]">Headline</span>
        <input
          required
          value={headline}
          onChange={(e) => setHeadline(e.target.value)}
          className="bg-[#161821] border border-[#2A2E38] rounded-sm px-3 py-2 text-[#F1EFE9] font-sans text-sm focus:outline-none focus:border-[#4CAF7D]"
          placeholder="New Air Max Collection"
        />
      </label>

      <label className="flex flex-col gap-1">
        <span className="font-mono text-xs text-[#6B6F7A]">Description</span>
        <textarea
          required
          rows={3}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="bg-[#161821] border border-[#2A2E38] rounded-sm px-3 py-2 text-[#F1EFE9] font-sans text-sm resize-none focus:outline-none focus:border-[#4CAF7D]"
          placeholder="Free shipping on orders over $50"
        />
      </label>

      <label className="flex flex-col gap-1">
        <span className="font-mono text-xs text-[#6B6F7A]">Ad image (optional)</span>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setImage(e.target.files?.[0] ?? null)}
          className="font-sans text-sm text-[#8B8F9B]"
        />
      </label>

      <button
        type="submit"
        disabled={isLoading}
        className="mt-2 self-start px-6 py-2.5 rounded-sm font-sans font-bold text-sm uppercase tracking-wider bg-[#4CAF7D] text-[#14161C] disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#5BC08E] transition-colors"
      >
        {isLoading ? "Reviewing…" : "Review Ad"}
      </button>
    </form>
  );
}