from typing import List
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def check_domain_relevance(
    candidate_tags: List[str],
    job_tags: List[str],
    embeddings
) -> float:
    """
    Quick check to filter out completely irrelevant candidates.
    
    Returns: 0-100 score indicating if candidate is in the right domain
    
    Examples:
    - Software Engineer job + ML Engineer candidate → 85% (relevant)
    - Software Engineer job + Chef candidate → 15% (out of domain)
    - Data Scientist job + Data Analyst candidate → 75% (relevant)
    """
    
    candidate_vectors = embeddings.embed_documents(candidate_tags)
    job_vectors = embeddings.embed_documents(job_tags)
    
    sim_matrix = cosine_similarity(candidate_vectors, job_vectors)
    
    # Check if there's ANY reasonable overlap
    # Use max similarity across all tag pairs
    max_similarity = sim_matrix.max()
    
    # Also check average of top matches
    best_per_job = sim_matrix.max(axis=0)
    top_k = min(3, len(job_tags))
    top_matches = np.sort(best_per_job)[-top_k:]
    avg_top_matches = top_matches.mean()
    
    # Combined relevance score
    # If even the BEST match is poor, candidate is out of domain
    relevance_score = (max_similarity * 0.4 + avg_top_matches * 0.6) * 100
    
    return relevance_score


# ============================================================================
# ALTERNATIVE: Stricter Domain Check
# ============================================================================
def check_domain_relevance_strict(
    candidate_tags: List[str],
    job_tags: List[str],
    embeddings
) -> float:
    """
    Stricter version that requires multiple good matches.
    Use this if you're getting too many false positives.
    """
    
    candidate_vectors = embeddings.embed_documents(candidate_tags)
    job_vectors = embeddings.embed_documents(job_tags)
    
    sim_matrix = cosine_similarity(candidate_vectors, job_vectors)
    best_per_job = sim_matrix.max(axis=0)
    
    # Count how many job tags have at least a decent match
    decent_threshold = 0.45
    num_decent_matches = (best_per_job >= decent_threshold).sum()
    coverage_ratio = num_decent_matches / len(job_tags)
    
    # Average quality of matches
    avg_quality = best_per_job.mean()
    
    # Must have both coverage AND quality
    relevance_score = (coverage_ratio * 0.6 + avg_quality * 0.4) * 100
    
    return relevance_score


# ============================================================================
# DETAILED MATCH SCORING (Second Filter)
# ============================================================================
def calculate_weighted_coverage_score(
    candidate_tags: List[str],
    job_tags: List[str],
    embeddings
) -> float:
    """
    Detailed scoring for candidates who passed domain check.
    Uses exponential weighting to create good separation.
    """
    
    candidate_vectors = embeddings.embed_documents(candidate_tags)
    job_vectors = embeddings.embed_documents(job_tags)
    
    sim_matrix = cosine_similarity(candidate_vectors, job_vectors)
    best_match_per_job_tag = sim_matrix.max(axis=0)
    
    # Exponential weighting rewards strong matches
    weighted_scores = np.power(best_match_per_job_tag, 2)
    final_score = weighted_scores.mean() * 100
    
    return final_score


# ============================================================================
# ALTERNATIVE: Combined Single-Pass Filter
# ============================================================================
def calculate_relevance_and_score_combined(
    candidate_tags: List[str],
    job_tags: List[str],
    embeddings,
    min_relevance: float = 0.65
) -> tuple[bool, float]:
    """
    Single function that checks both relevance and calculates score.
    More efficient than two separate calls.
    
    Returns: (is_relevant, match_score)
    """
    
    candidate_vectors = embeddings.embed_documents(candidate_tags)
    job_vectors = embeddings.embed_documents(job_tags)
    
    sim_matrix = cosine_similarity(candidate_vectors, job_vectors)
    best_match_per_job_tag = sim_matrix.max(axis=0)
    
    # Quick relevance check
    max_sim = sim_matrix.max()
    avg_top_3 = np.sort(best_match_per_job_tag)[-3:].mean() if len(best_match_per_job_tag) >= 3 else best_match_per_job_tag.mean()
    
    is_relevant = (max_sim >= min_relevance) and (avg_top_3 >= min_relevance * 0.8)
    
    if not is_relevant:
        return False, 0.0
    
    # Calculate detailed score only if relevant
    weighted_scores = np.power(best_match_per_job_tag, 2)
    match_score = weighted_scores.mean() * 100
    
    return True, match_score