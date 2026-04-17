# Resume Matching Design — intelliHR AI
> **Last Updated:** 2026-02-19  
> **Scenario:** 1 Job × N Candidate CVs → Ranked, scored shortlist

---

## Complete End-to-End Flow (Both Services)

```
[Frontend / Recruiter UI]
        │ POST /ai-matching?jobId=&title=&threshold=
        ▼
[Backend — AIAnalysisMatchingQueryHandler.cs]
        │
        ├─ 1. Fetch Job from DB (title, JD, skills, tags, qualifications)
        │
        ├─ 2. STAGE 1 HARD FILTER (in DB query):
        │      · Status IN (Sourced, TalentPool)
        │      · NOT IsHrShortlisted
        │      · experience_year WITHIN job's ExperienceRange ± tolerance
        │                              ↓ Drop ineligible candidates
        │
        ├─ 3. BuildCandidateResponsesAsync() — maps DB entities → CandidateMatchResponse DTOs
        │
        │ POST {AI_BASE_URL}/api/v1/ai/batch-analyze-resumes
        ▼
[Python AI Service — resume_data.py]
        │
        ├─ 4. STAGE 2 SEMANTIC PRE-FILTER (Embedding/Cosine):
        │      · For each candidate: check_domain_relevance_strict + calculate_weighted_coverage_score
        │      · Only candidates with score ≥ MINIMUM_ELIGIBLE_SCORE proceed
        │
        └─ 5. STAGE 3 LLM DEEP SCORING (resume_analyze.py):
               · temperature=0.4, GPT model
               · Skills(50%) + Experience(30%) + CulturalFit(20%) → matchScore
               · threshold filter applied after
               · Returns List[CandidateAnalysisResponse]
        ▼
[Backend — Hangfire Background Job]
        │ GenerateMatchAnalysisEvent → GenerateMatchAnalysisEventHandler
        └─ 6. Upsert AIMatchingResult rows in DB (MatchScore, TechnicalMatch,
               ExperienceMatch, SoftSkillsMatch, MatchDetails JSON, AIInsights JSON)
```

---

## Identified Gaps (Both Codebases)

| # | File | Problem |
|---|------|---------|
| 1 | `AIAnalysisMatchingQueryHandler.cs` | `BuildCandidateResponsesAsync` deserializes `candidate.AiAnalysis` **3× per candidate** (once per field extraction) — wasteful |
| 2 | `resume_data.py` | Embeddings computed **twice** per candidate (domain check + score check) — could be one call |
| 3 | `resume_analyze.py` | `job.description` field is serialized inside `job_json` but **never explicitly used** in the prompt instructions — LLM may ignore free-text JD |
| 4 | `resume_analyze.py` | **No `qualificationScore`** dimension — `qualification` data is available (sent from backend) but never explicitly scored |
| 5 | `resume_analyze.py` | **No experience level mismatch penalty** — Junior at Senior level job loses no explicit points in the prompt |
| 6 | `ai_match_score.py` | Scoring is **one-directional** (job-tag coverage only) — candidates with 50 generic tags can unfairly inflate score |
| 7 | `MatchAnalysis.cs / batch_analyze_model.py` | `AiInsights` DTO has no `qualificationScore` or `experienceLevelFit` fields — backend can't display these |

---

## Industry-Standard Architecture: Hybrid 3-Stage Funnel

```
N Candidates
     │
     ▼
┌─────────────────────────┐  Zero AI cost
│  STAGE 1: Hard Filter   │  O(N), DB-side
│  · ExperienceRange ✓    │──────┐
│  · Status check ✓       │      │ Drop ~30-50%
│  · Not shortlisted ✓    │      │
└─────────────────────────┘      │
     │ (already exists in backend, could be improved)
     ▼
┌─────────────────────────┐  Fast AI (~2ms/candidate)
│  STAGE 2: Semantic      │
│  Pre-Filter             │──────┐ Drop another ~30%
│  · Embed JD ONCE        │      │
│  · Bidirectional cosine │      │
└─────────────────────────┘      │
     │
     ▼
┌─────────────────────────┐  Slow AI (only top candidates)
│  STAGE 3: LLM Scoring   │
│  · 4-dimensional score  │
│  · Full JD description  │
└─────────────────────────┘
     │
     ▼
  Ranked Shortlist → Background Job → DB
```

---

## Proposed Improvements

### A. Backend — `AIAnalysisMatchingQueryHandler.cs`

**Fix: Deserialize AiAnalysis once per candidate**

```csharp
// BEFORE (3 deserialization calls per candidate):
ExperienceLevel = JsonHelper.DeserializeObject<CandidateAnalysis>(candidate.AiAnalysis)!.ExperienceLevel,
ExperienceYear  = JsonHelper.DeserializeObject<CandidateAnalysis>(candidate.AiAnalysis)!.ExperienceYear,
CurrentTitle    = JsonHelper.DeserializeObject<CandidateAnalysis>(candidate.AiAnalysis)!.PrimaryDomain,

// AFTER (1 deserialization per candidate):
var analysis = JsonHelper.DeserializeObject<CandidateAnalysis>(candidate.AiAnalysis);
ExperienceLevel = analysis?.ExperienceLevel,
ExperienceYear  = analysis?.ExperienceYear,
CurrentTitle    = analysis?.PrimaryDomain,
```

**Improvement: Widen Stage 1 experience tolerance**

Current: strict exact-range match with no tolerance  
Proposed: allow ±1 year tolerance (prevents cutting off near-miss candidates)

```csharp
// Add tolerance buffer so AI Stage 2/3 can make the nuanced call
if (currentExperience < minExp - 1.0 || currentExperience > maxExp + 1.5)
    continue;
```

---

### B. AI Service — `app/services/ai_match_score.py`

**Replace two separate calls with one combined bidirectional function:**

```python
def calculate_match_scores_combined(
    candidate_tags: List[str],
    job_tags: List[str],
    embeddings
) -> tuple[float, float]:
    """
    Single-pass: compute embeddings ONCE, return (relevance_score, match_score).
    Bidirectional: penalises candidates with many irrelevant tags.
    """
    c_vecs = np.array(embeddings.embed_documents(candidate_tags))
    j_vecs = np.array(embeddings.embed_documents(job_tags))

    sim = cosine_similarity(c_vecs, j_vecs)           # shape (C, J)

    # Job-side: how well does candidate cover JD tags?
    job_coverage  = sim.max(axis=0)                    # Best C match per J tag
    # Candidate-side: how relevant are candidate tags to JD?
    cand_coverage = sim.max(axis=1)                    # Best J match per C tag

    relevance_score = (job_coverage.mean() * 0.6 + cand_coverage.mean() * 0.4) * 100

    weighted = np.power(job_coverage, 2) * 0.6 + np.power(cand_coverage, 2) * 0.4
    match_score = weighted.mean() * 100

    return relevance_score, match_score
```

**In `resume_data.py` — embed JD ONCE, reuse for all candidates:**

```python
# Compute job embedding once per job (outside candidate loop)
job_tag_str = " ".join(job.job_tag)
job_vector = embeddings.embed_query(job_tag_str)

for candidate in request.candidates:
    candidate_vector = embeddings.embed_query(" ".join(candidate.candidate_tag))
    relevance, score = calculate_match_scores_combined_from_vectors(
        job_vector, candidate_vector, job.job_tag, candidate.candidate_tag
    )
```

---

### C. AI Service — `agents/resume_analyze.py` (Prompt Improvements)

**Scoring formula change (4 dimensions):**

```
CURRENT:  matchScore = Skills(50%) + Experience(30%) + CulturalFit(20%)
PROPOSED: matchScore = Skills(45%) + Experience(30%) + CulturalFit(15%) + Qualification(10%)
```

**Add experience level mismatch penalty:**

```
Experience Level Alignment (add to Experience scoring section):
  · If candidate is 1 level below JD requirement  → deduct 10 pts from experienceScore
  · If candidate is 2+ levels below               → deduct 20 pts
  · If candidate is overqualified by 2+ levels    → deduct 5 pts (flight risk)
  Level ladder: Entry < Junior < Mid < Mid-Senior < Senior < Lead < Principal
```

**Add full JD description to DATA section:**

```
### Data for Evaluation:
Job Information:
{job_json}

Full Job Description (use to identify implicit requirements):
{job_description}

Candidate Information:
{candidate_json}
```

**Add qualificationScore to JSON output schema:**

```json
"aiInsights": {
    "coreSkillsScore": 0,
    "experienceScore": 0,
    "culturalFitScore": 0,
    "qualificationScore": 0,         ← NEW
    "experienceLevelFit": "string",  ← NEW: "matched"|"underqualified"|"overqualified"
    ...
}
```

---

### D. DTOs — Add new fields to support new scores

**`MatchAnalysis.cs` (backend):**

```csharp
public class AiInsights
{
    // ... existing fields ...
    [JsonPropertyName("qualificationScore")]
    public float? QualificationScore { get; set; }   // NEW

    [JsonPropertyName("experienceLevelFit")]
    public string? ExperienceLevelFit { get; set; }  // NEW
}
```

**`batch_analyze_model.py` (AI service):**

```python
class AIInsights(BaseModel):
    # ... existing ...
    qualificationScore: Optional[float] = 0.0      # NEW
    experienceLevelFit: Optional[str] = None        # NEW
```

---

## Stage 2 Threshold Guide

| Score | Decision |
|-------|----------|
| ≥ 40% | ✅ Pass to LLM (Stage 3) |
| 25–39% | ⚠️ Borderline — include only if not enough Stage-3 candidates |
| < 25%  | ❌ Reject — out of domain |

---

## Files to Modify — Summary

| File | Codebase | Change |
|------|----------|--------|
| `AIAnalysisMatchingQueryHandler.cs` | Backend | Fix triple-deserialization; widen experience tolerance |
| `MatchAnalysis.cs` | Backend | Add `QualificationScore`, `ExperienceLevelFit` to `AiInsights` |
| `ai_match_score.py` | AI | New `calculate_match_scores_combined()` — bidirectional, single-embedding-call |
| `resume_data.py` | AI | Embed JD once; call new combined function |
| `resume_analyze.py` | AI | 4-dimension prompt; JD description variable; level penalty; lower temp to 0.2 |
| `batch_analyze_model.py` | AI | Add `qualificationScore`, `experienceLevelFit` to `AIInsights` |
| `config/Settings.py` | AI | Add `experience_level_tolerance` setting |

---

## Performance Impact (Estimated)

| Metric | Before | After |
|--------|--------|-------|
| Embedding API calls per N candidates | 2N | ~N + 1 |
| Candidates reaching LLM (Stage 3) | ~70% | ~30–40% |
| AiAnalysis deserialization per candidate | 3× | 1× |
| Qualification scoring | Implicit | Explicit 10% |
| Level mismatch penalty | None | −10 to −20 pts |
