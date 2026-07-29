import React from "react";

// ---------------------------------------------------------------------------
// Mock data — shaped exactly like the real Advertisement + TrustReport
// coming back from POST /review-ad. Swap these two objects for the live
// Axios response later; nothing else in this file needs to change.
// ---------------------------------------------------------------------------

const mockAd = {
  brand_name: "Amazon",
  headline: "Your account has been suspended",
  landing_url: "http://arnazon-login.top",
};

const mockReport = {
  ad_id: "e09a49d1-b06c-4f00-9578-135133000207",
  overall_risk: 92,
  recommendation: "Reject",
  confidence: 0.98,
  agent_results: [
    {
      agent_name: "URL Agent",
      risk_score: 65,
      issues: [
        "Domain segment closely resembles brand name 'Amazon' — possible typosquatting",
        "Suspicious top-level domain: .top",
        "Landing page does not use HTTPS",
      ],
      confidence: 0.9,
      execution: { duration_seconds: 0.0002, retries: 0, status: "success" },
    },
    {
      agent_name: "Text Agent",
      risk_score: 95,
      issues: ["PHISHING LANGUAGE"],
      confidence: 0.99,
      execution: { duration_seconds: 0.5391, retries: 0, status: "success" },
    },
    {
      agent_name: "Image Agent",
      risk_score: 0,
      issues: ["No image provided"],
      confidence: 0.5,
      execution: { duration_seconds: 0, retries: 0, status: "success" },
    },
    {
      agent_name: "Brand Agent",
      risk_score: 80,
      issues: ["Potential phishing attempt", "Urgency tactic"],
      confidence: 0.9,
      execution: { duration_seconds: 0.7006, retries: 0, status: "success" },
    },
  ],
  summary:
    "The Text Agent's high-confidence detection of phishing language and the Brand Agent's identification of potential phishing tactics and urgency, combined with the URL Agent's findings of a suspicious domain and lack of HTTPS, provide strong evidence of a phishing attempt. The corroboration of these findings across multiple agents justifies a rejection of the advertisement.",
  execution: { duration_seconds: 0.6094, retries: 0, status: "success" },
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function riskLevel(score) {
  if (score < 34) return "safe";
  if (score < 67) return "caution";
  return "danger";
}

const LEVEL_COLOR = {
  safe: "#4CAF7D",
  caution: "#E8A33D",
  danger: "#E4483C",
};

const VERDICT_STYLE = {
  Approve: { color: "#4CAF7D", label: "APPROVED" },
  "Manual Review": { color: "#E8A33D", label: "MANUAL REVIEW" },
  Reject: { color: "#E4483C", label: "REJECTED" },
};

function shortId(id) {
  return id ? id.slice(0, 8).toUpperCase() : "—";
}

// ---------------------------------------------------------------------------
// Gauge — semicircle dial, needle sweeps from 0 (safe) to 100 (danger)
// ---------------------------------------------------------------------------

function RiskGauge({ value }) {
  const angle = (value / 100) * 180 - 90; // -90deg (left) .. 90deg (right)
  const r = 80;
  const circumference = Math.PI * r;
  const dash = (value / 100) * circumference;

  return (
    <div className="relative w-[220px] h-[120px] mx-auto">
      <svg viewBox="0 0 200 110" className="w-full h-full">
        <defs>
          <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#4CAF7D" />
            <stop offset="50%" stopColor="#E8A33D" />
            <stop offset="100%" stopColor="#E4483C" />
          </linearGradient>
        </defs>
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke="#2A2E38"
          strokeWidth="10"
          strokeLinecap="round"
        />
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke="url(#gaugeGradient)"
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={`${dash} ${circumference}`}
        />
        <circle cx="100" cy="100" r="5" fill="#F1EFE9" />
        <line
          x1="100"
          y1="100"
          x2="100"
          y2="30"
          stroke="#F1EFE9"
          strokeWidth="3"
          strokeLinecap="round"
          transform={`rotate(${angle} 100 100)`}
        />
      </svg>
      <div className="absolute inset-x-0 bottom-0 text-center">
        <span
          className="font-mono text-3xl font-bold"
          style={{ color: LEVEL_COLOR[riskLevel(value)] }}
        >
          {value}
        </span>
        <span className="font-mono text-sm text-[#8B8F9B]">/100</span>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Agent card — one "index card" per specialist reviewer
// ---------------------------------------------------------------------------

function AgentCard({ result }) {
  const level = riskLevel(result.risk_score);
  const color = LEVEL_COLOR[level];

  return (
    <div
      className="relative flex flex-col rounded-sm bg-[#1C1F27] border border-[#2A2E38] overflow-hidden"
      style={{ borderTopWidth: "3px", borderTopColor: color }}
    >
      <div className="p-4 flex-1 flex flex-col gap-3">
        <div className="flex items-baseline justify-between">
          <h3 className="font-sans text-xs uppercase tracking-[0.15em] text-[#8B8F9B]">
            {result.agent_name}
          </h3>
          <span
            className="font-mono text-lg font-semibold"
            style={{ color }}
          >
            {result.risk_score}
          </span>
        </div>

        <div className="h-1.5 rounded-full bg-[#2A2E38] overflow-hidden">
          <div
            className="h-full rounded-full transition-all"
            style={{ width: `${result.risk_score}%`, backgroundColor: color }}
          />
        </div>

        <ul className="flex flex-col gap-1.5 mt-1 min-h-[3.5rem]">
          {result.issues.map((issue, i) => (
            <li
              key={i}
              className="text-[13px] leading-snug text-[#D7D4C9] flex gap-2"
            >
              <span style={{ color }} className="shrink-0">▸</span>
              <span>{issue}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="flex items-center justify-between px-4 py-2 bg-[#161821] border-t border-[#2A2E38] font-mono text-[11px] text-[#6B6F7A]">
        <span>conf {Math.round(result.confidence * 100)}%</span>
        <span>{result.execution.duration_seconds.toFixed(3)}s</span>
        <span className={result.execution.status === "success" ? "text-[#4CAF7D]" : "text-[#E8A33D]"}>
          {result.execution.status}
        </span>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Verdict stamp — the signature element
// ---------------------------------------------------------------------------

function VerdictStamp({ recommendation }) {
  const style = VERDICT_STYLE[recommendation] ?? VERDICT_STYLE["Manual Review"];
  return (
    <div
      className="inline-flex items-center justify-center px-6 py-3 border-[3px] rounded-sm select-none"
      style={{
        borderColor: style.color,
        color: style.color,
        transform: "rotate(-4deg)",
        boxShadow: `0 0 0 1px ${style.color}33 inset`,
      }}
    >
      <span className="font-sans font-bold text-2xl tracking-[0.2em]">
        {style.label}
      </span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main dashboard
// ---------------------------------------------------------------------------

export default function AdShieldDashboard({ ad = mockAd, report = mockReport }) {
  const verdict = VERDICT_STYLE[report.recommendation] ?? VERDICT_STYLE["Manual Review"];

  return (
    <div className="min-h-full w-full bg-[#14161C] text-[#F1EFE9] font-sans p-6 md:p-10">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
        .font-sans { font-family: 'Space Grotesk', system-ui, sans-serif; }
        .font-mono { font-family: 'IBM Plex Mono', monospace; }
      `}</style>

      {/* Case file header */}
      <div className="max-w-5xl mx-auto mb-8 border-b border-[#2A2E38] pb-6">
        <div className="flex flex-wrap items-baseline justify-between gap-3">
          <div>
            <p className="font-mono text-xs text-[#6B6F7A] uppercase tracking-[0.2em] mb-1">
              Case File · {shortId(report.ad_id)}
            </p>
            <h1 className="font-sans text-2xl font-bold">
              {ad.brand_name} — {ad.headline}
            </h1>
            <p className="font-mono text-xs text-[#6B6F7A] mt-1">{ad.landing_url}</p>
          </div>
          <p className="font-mono text-xs text-[#6B6F7A]">
            reviewed in {report.execution.duration_seconds.toFixed(2)}s
          </p>
        </div>
      </div>

      {/* Agent reports */}
      <div className="max-w-5xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        {report.agent_results.map((result) => (
          <AgentCard key={result.agent_name} result={result} />
        ))}
      </div>

      {/* Verdict */}
      <div className="max-w-5xl mx-auto rounded-sm bg-[#1C1F27] border border-[#2A2E38] p-6 md:p-8">
        <div className="flex flex-col md:flex-row gap-8 items-center">
          <RiskGauge value={report.overall_risk} />

          <div className="flex-1 flex flex-col gap-4 items-center md:items-start text-center md:text-left">
            <VerdictStamp recommendation={report.recommendation} />
            <p className="text-[15px] leading-relaxed text-[#D7D4C9] max-w-xl">
              {report.summary}
            </p>
            <p className="font-mono text-xs text-[#6B6F7A]">
              decision confidence {Math.round(report.confidence * 100)}%
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}