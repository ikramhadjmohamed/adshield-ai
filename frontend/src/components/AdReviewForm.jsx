import React, { useState } from "react";

export default function AdReviewForm({ onSubmit, isLoading }) {
  const [brandName, setBrandName] = useState("");
  const [headline, setHeadline] = useState("");
  const [description, setDescription] = useState("");
  const [landingUrl, setLandingUrl] = useState("");
  const [image, setImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [errors, setErrors] = useState({});

  function clearError(field) {
    setErrors((prev) => (prev[field] ? { ...prev, [field]: undefined } : prev));
  }

  function setSelectedImage(file) {
    if (!file) {
      setImage(null);
      setPreviewUrl(null);
      return;
    }
    setImage(file);
    setPreviewUrl(URL.createObjectURL(file));
  }

  function handleDrop(e) {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith("image/")) setSelectedImage(file);
  }

  function validate() {
    const newErrors = {};
    if (!brandName.trim()) newErrors.brandName = "Brand name is required";
    if (!headline.trim()) newErrors.headline = "Headline is required";
    if (!description.trim()) newErrors.description = "Description is required";
    if (!landingUrl.trim()) {
      newErrors.landingUrl = "Landing URL is required";
    } else if (!/^https?:\/\/.+/i.test(landingUrl.trim())) {
      newErrors.landingUrl = "Must be a valid URL starting with http:// or https://";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!validate()) return;

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
      noValidate
      className="max-w-5xl mx-auto mb-10 bg-[#1C1F27] border border-[#2A2E38] rounded-sm p-6 md:p-8 flex flex-col gap-4"
    >
      <h2 className="font-sans text-xs uppercase tracking-[0.2em] text-[#8B8F9B] mb-2">
        Submit Advertisement for Review
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <label className="flex flex-col gap-1">
          <span className="font-mono text-xs text-[#6B6F7A]">Brand name</span>
          <input
            value={brandName}
            onChange={(e) => {
              setBrandName(e.target.value);
              clearError("brandName");
            }}
            className={`bg-[#161821] border rounded-sm px-3 py-2 text-[#F1EFE9] font-sans text-sm focus:outline-none transition-colors ${
              errors.brandName ? "border-[#E4483C]" : "border-[#2A2E38] focus:border-[#4CAF7D]"
            }`}
            placeholder="Nike"
          />
          {errors.brandName && (
            <span className="font-mono text-xs text-[#E4483C]">{errors.brandName}</span>
          )}
        </label>

        <label className="flex flex-col gap-1">
          <span className="font-mono text-xs text-[#6B6F7A]">Landing URL</span>
          <input
            value={landingUrl}
            onChange={(e) => {
              setLandingUrl(e.target.value);
              clearError("landingUrl");
            }}
            className={`bg-[#161821] border rounded-sm px-3 py-2 text-[#F1EFE9] font-sans text-sm focus:outline-none transition-colors ${
              errors.landingUrl ? "border-[#E4483C]" : "border-[#2A2E38] focus:border-[#4CAF7D]"
            }`}
            placeholder="https://nike.com"
          />
          {errors.landingUrl && (
            <span className="font-mono text-xs text-[#E4483C]">{errors.landingUrl}</span>
          )}
        </label>
      </div>

      <label className="flex flex-col gap-1">
        <span className="font-mono text-xs text-[#6B6F7A]">Headline</span>
        <input
          value={headline}
          onChange={(e) => {
            setHeadline(e.target.value);
            clearError("headline");
          }}
          className={`bg-[#161821] border rounded-sm px-3 py-2 text-[#F1EFE9] font-sans text-sm focus:outline-none transition-colors ${
            errors.headline ? "border-[#E4483C]" : "border-[#2A2E38] focus:border-[#4CAF7D]"
          }`}
          placeholder="New Air Max Collection"
        />
        {errors.headline && (
          <span className="font-mono text-xs text-[#E4483C]">{errors.headline}</span>
        )}
      </label>

      <label className="flex flex-col gap-1">
        <span className="font-mono text-xs text-[#6B6F7A]">Description</span>
        <textarea
          rows={3}
          value={description}
          onChange={(e) => {
            setDescription(e.target.value);
            clearError("description");
          }}
          className={`bg-[#161821] border rounded-sm px-3 py-2 text-[#F1EFE9] font-sans text-sm resize-none focus:outline-none transition-colors ${
            errors.description ? "border-[#E4483C]" : "border-[#2A2E38] focus:border-[#4CAF7D]"
          }`}
          placeholder="Free shipping on orders over $50"
        />
        {errors.description && (
          <span className="font-mono text-xs text-[#E4483C]">{errors.description}</span>
        )}
      </label>

      {/* Dropzone */}
      <div className="flex flex-col gap-1">
        <span className="font-mono text-xs text-[#6B6F7A]">Ad image (optional)</span>

        <label
          htmlFor="ad-image-input"
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          className={`relative cursor-pointer rounded-sm border-2 border-dashed transition-colors flex items-center gap-4 px-4 py-4 ${
            isDragging
              ? "border-[#4CAF7D] bg-[#1A2620]"
              : "border-[#2A2E38] bg-[#161821] hover:border-[#3A3F4C]"
          }`}
        >
          <input
            id="ad-image-input"
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => setSelectedImage(e.target.files?.[0] ?? null)}
          />

          {previewUrl ? (
            <>
              <img
                src={previewUrl}
                alt="Ad preview"
                className="w-14 h-14 object-cover rounded-sm border border-[#2A2E38]"
              />
              <div className="flex flex-col gap-0.5 flex-1 min-w-0">
                <span className="font-sans text-sm text-[#F1EFE9] truncate">
                  {image.name}
                </span>
                <span className="font-mono text-xs text-[#6B6F7A]">
                  {(image.size / 1024).toFixed(0)} KB — click to replace
                </span>
              </div>
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  setSelectedImage(null);
                }}
                className="shrink-0 w-7 h-7 flex items-center justify-center rounded-full bg-[#2A2E38] text-[#8B8F9B] hover:bg-[#E4483C] hover:text-white transition-colors"
                aria-label="Remove image"
              >
                ✕
              </button>
            </>
          ) : (
            <>
              <div className="shrink-0 w-10 h-10 flex items-center justify-center rounded-full bg-[#2A2E38] text-[#8B8F9B]">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 16V4M12 4l4 4M12 4L8 8" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M20 16v3a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-3" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <div className="flex flex-col gap-0.5">
                <span className="font-sans text-sm text-[#F1EFE9]">
                  Drag & drop an image, or click to browse
                </span>
                <span className="font-mono text-xs text-[#6B6F7A]">PNG, JPG up to a few MB</span>
              </div>
            </>
          )}
        </label>
      </div>

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