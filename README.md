# AdShield AI

An AI-powered ad moderation platform that automatically reviews advertisements before they go live, detects signs of scams, impersonation, and manipulation, and generates an explainable trust report for human moderators.

> **Challenge:** Ad Trust & Authenticity — Detection & Verification angle
> **User:** Advertising platform moderators (Google Ads / TikTok Ads / Meta Ads style)

---

## The problem

Millions of ads are submitted to platforms every day. Humans cannot manually inspect all of them, and generative AI makes scam ads cheaper and more convincing to produce. Platforms need a way to **prioritize** which ads deserve a closer look before they reach real users.

## What it does

AdShield AI assists advertising platform moderators by prioritizing potentially fraudulent advertisements before publication. It answers one question: **"Should this advertisement be manually reviewed before publication?"**

An advertiser (or in this MVP, a moderator testing a submission) provides a brand name, headline, description, landing URL, and optionally an image. The system runs four specialized reviewers, each inspecting one dimension of the advertisement, before a final Decision Agent reasons over their combined evidence to produce a trust report — not just a score, but a clear explanation of *why*.

```
                       Advertisement  
                            │
                            ▼
┌─────────────┬─────────────┬─────────────┬─────────────┐
│  URL Agent  │ Text Agent  │ Image Agent │ Brand Agent │
│ (rule-based)│   (LLM)     │ (OCR + LLM) │   (LLM)     │
└─────────────┴─────────────┴─────────────┴─────────────┘
      │             │              │             │
      └─────────────┴──────┬───────┴─────────────┘
                            ▼
                     Decision Agent (LLM)
                            │
                            ▼
                      Trust Report
              (risk score, recommendation,
               evidence-based explanation)
```

**Important design choice:** the system never claims "our AI decides." It says "our AI assists human moderators by prioritizing risky advertisements and explaining why." The final recommendation is always one of `Approve`, `Reject`, or `Manual Review` — a human stays in the loop.

---
 
## Demo

### Ad Submission Form

![Ad Submission Form](demo/approved/Screenshot%202026-07-29%20210120.png)

### Trust Report — Approved

![Approved Trust Report](demo/approved/Screenshot%202026-07-29%20210150.png)

### Trust Report — Rejected

![Rejected Trust Report](demo/rejected/Screenshot%202026-07-29%20205115.png)

### Investigation Details

![Rejected Ad Evidence](demo/rejected/Screenshot%202026-07-29%20205135.png)

---

## Why a multi-agent architecture?

Rather than relying on a single model to make a moderation decision, AdShield AI decomposes the problem into specialized reviewers. Each agent focuses on one aspect of an advertisement (URL, text, image, or brand consistency), producing explainable evidence instead of a single opaque prediction.

A final Decision Agent synthesizes these independent findings into an evidence-based recommendation, making the system easier to understand, debug, and extend with new reviewers over time.

---

## Pipeline components

| Component | Type | What it checks |
|---|---|---|
| **URL Agent** | Rule-based (no LLM) | Typosquatting, suspicious TLDs, missing HTTPS, scam keywords in the domain |
| **Text Agent** | LLM (Groq / Llama 3.3) | Urgency tactics, unrealistic promises, phishing language, manipulative wording, misleading claims |
| **Image Agent** | OCR (EasyOCR) + LLM | Uses EasyOCR to extract visible text from an advertisement image, then applies the same language-based fraud analysis as the Text Agent. *The MVP does not perform visual deepfake or logo analysis.* |
| **Brand Agent** | LLM | Checks whether the ad's tone/claims are consistent with the stated brand's known public identity (returns a neutral result for unrecognized/fictional brands rather than guessing) |
| **Decision Agent** | LLM | **Reasons over evidence rather than averaging scores** to produce the final risk score, recommendation, and explanation |

Every agent shares a common `AgentResult` contract (risk score, issues, confidence, reasoning, execution metadata) and a common resilience strategy: retry once on malformed output, fall back to a safe "Manual Review" signal rather than crashing the pipeline if an LLM call fails.

---

## Tech stack

| Layer | Choice |
|---|---|
| Backend | FastAPI (Python) |
| Data validation | Pydantic v2 |
| LLM | Groq API — `llama-3.3-70b-versatile` |
| OCR | EasyOCR |
| Frontend | React (Vite) |
| Styling | Tailwind CSS |
| HTTP client | Axios |

---

## Project structure

```
adshield-ai/
├── backend/
│   ├── agents/
│   │   ├── url_agent.py
│   │   ├── text_agent.py
│   │   ├── image_agent.py
│   │   ├── brand_agent.py
│   │   └── decision_agent.py
│   ├── api/
│   │   └── routes.py
│   ├── models/
│   │   └── schemas.py
│   ├── scripts/
│   │   ├── test_url_agent.py
│   │   ├── test_text_agent.py
│   │   ├── test_image_agent.py
│   │   ├── test_brand_agent.py
│   │   ├── test_decision_agent.py
│   │   └── test_images/
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AdReviewForm.jsx
│   │   │   └── AdShieldDashboard.jsx
│   │   ├── App.jsx
│   │   └── index.css
│   └── .env.example
│
└── README.md
```

---

## Running the project

### Prerequisites

- Python 3.11+
- Node.js 18+
- A Groq API key ([console.groq.com](https://console.groq.com))

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

Create a `.env` file in `backend/`:
```
GROQ_API_KEY=your_groq_api_key_here
```

Run the server:
```bash
uvicorn main:app --reload
```
API available at `http://127.0.0.1:8000` (interactive docs at `/docs`).

### Frontend

```bash
cd frontend
npm install
```

Create a `.env` file in `frontend/` (see `.env.example`):
```
VITE_API_URL=http://127.0.0.1:8000
```

Run the dev server:
```bash
npm run dev
```
App available at `http://localhost:5173`.

Both servers must be running simultaneously for the app to work end to end.

---

## Testing

Each agent has an isolated test script under `backend/scripts/`, following an incremental build-test-freeze workflow: every agent was validated on its own (including edge cases and false-positive checks) before being wired into the full pipeline.

```bash
cd backend/scripts
python test_url_agent.py
python test_text_agent.py
python test_image_agent.py
python test_brand_agent.py
python test_decision_agent.py
```

---

## Design decisions worth noting

- **Evidence over averaging** — the Decision Agent does not compute a weighted average of the four agent scores. A single strong signal (e.g. explicit phishing language) can justify rejection even if the other three agents report low risk, matching how a human moderator would actually reason.
- **Heuristic weights are labeled as such** — the URL Agent's rule-based scoring uses expert-defined baseline weights, explicitly documented as a starting point that would be calibrated on labeled data in a production system, not presented as scientifically precise.
- **Honest uncertainty** — the Brand Agent returns a neutral, low-confidence result for brands it doesn't recognize rather than guessing. No agent invents facts it isn't confident about.
- **Resilience by design** — every LLM-based agent retries once on malformed output, then falls back to a safe "flag for manual review" result instead of crashing the pipeline.
- **Sequential by choice, not by necessity** — the four specialized agents are fully independent of each other's outputs, so the current sequential execution could be parallelized (e.g. with `asyncio.gather`) as a straightforward future optimization without any architectural changes.

---

## Roadmap

Given more time, natural next steps for this project:

- Deepfake video/audio detection
- Digital signatures / content credentials for brand-verified ads (provenance angle)
- Brand knowledge base with official guidelines, to make the Brand Agent reliable beyond well-known brands
- Moderator feedback loop — storing human decisions to eventually replace hand-picked heuristic weights with learned ones
- Parallel agent execution for lower latency
- Browser extension for consumers to check any ad they encounter