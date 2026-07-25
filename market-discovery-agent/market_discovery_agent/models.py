"""
Data models for the Early-Stage Market Discovery Agent.

Kept as plain dataclasses (not pydantic) so the project has zero
dependencies beyond the `openai` SDK itself.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class FounderInput:
    """Raw input collected from the founder in Phase 1."""
    product_idea: str
    vision: str
    features: List[str]
    assumptions: List[str]
    founder_knowledge: str
    target_location: str = ""  # where qualified target accounts should be based, e.g. "India" — optional; consumed by the Target Account Agent (Phase 4c). Defaults to "" for sessions created before this field existed.

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Phase1Output:
    """
    The synthesized output of Phase 1 — Business Understanding.
    This is what every later phase (research planning, ICP discovery,
    validation, GTM recommendation) is built on top of.
    """
    problem_statement: str
    initial_hypotheses: List[str]
    success_criteria: List[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ResearchQuestion:
    question: str
    rationale: str


@dataclass
class ResearchAgentBrief:
    """
    A brief for one of the seven secondary-research agents
    (Industry, Competitor, Community, Search Intent, Funding,
    Job Market, Social Intelligence).
    """
    agent_name: str
    objective: str
    questions: List[ResearchQuestion]
    suggested_sources: List[str]

    def to_dict(self) -> dict:
        return {
            "agent_name": self.agent_name,
            "objective": self.objective,
            "questions": [asdict(q) for q in self.questions],
            "suggested_sources": self.suggested_sources,
        }


@dataclass
class ResearchPlan:
    """
    Output of the Research Planner — turns Phase 1's problem statement
    and hypotheses into concrete, tailored briefs for each secondary
    research agent. This is what Phase 2 (Secondary Research) will
    execute against once it's built.
    """
    priority_order: List[str]
    agent_briefs: List[ResearchAgentBrief]
    open_questions_for_founder: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "priority_order": self.priority_order,
            "agent_briefs": [b.to_dict() for b in self.agent_briefs],
            "open_questions_for_founder": self.open_questions_for_founder,
        }


@dataclass
class ResearchFinding:
    """One answered research question, as recorded by a secondary-research agent."""
    question: str
    answer: str
    confidence: str  # "High" | "Medium" | "Low"
    sources: List[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class IndustryResearchOutput:
    """
    Output of the Industry Agent (Phase 2A of Secondary Research) —
    grounded, sourced findings on the industry this idea actually serves.
    """
    industry_name: str
    findings: List[ResearchFinding]
    summary: str
    opportunity_signal: str  # "Strong" | "Moderate" | "Weak" | "Unclear"

    def to_dict(self) -> dict:
        return {
            "industry_name": self.industry_name,
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
            "opportunity_signal": self.opportunity_signal,
        }


@dataclass
class CompetitorResearchOutput:
    """
    Output of the Competitor Agent (Phase 2B of Secondary Research) for
    ONE competitor, identified from a public LinkedIn company-page URL —
    grounded, sourced findings on their product, positioning, pricing,
    customers, and weaknesses. No opportunity_signal here: that's a
    landscape-level judgment made by looking across all competitors
    together, not per-competitor.
    """
    linkedin_url: str
    company_name: str
    website_url: str
    findings: List[ResearchFinding]
    summary: str

    def to_dict(self) -> dict:
        return {
            "linkedin_url": self.linkedin_url,
            "company_name": self.company_name,
            "website_url": self.website_url,
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
        }


@dataclass
class CommunityResearchOutput:
    """
    Output of the Community Agent (Phase 2C of Secondary Research) —
    grounded, sourced findings from founder/user communities (Reddit,
    Indie Hackers, Slack/Discord, Hacker News, LinkedIn posts/comments)
    on whether the problem this idea addresses actually surfaces
    organically in how people talk, in their own words.
    """
    community_landscape: str
    findings: List[ResearchFinding]
    summary: str
    opportunity_signal: str  # "Strong" | "Moderate" | "Weak" | "Unclear"

    def to_dict(self) -> dict:
        return {
            "community_landscape": self.community_landscape,
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
            "opportunity_signal": self.opportunity_signal,
        }


@dataclass
class SearchIntentResearchOutput:
    """
    Output of the Search Intent Agent (Phase 2D of Secondary Research) —
    grounded, sourced findings on whether people actually search for this
    problem/solution (volume, trend direction, autocomplete/PAA patterns),
    as opposed to only discovering it via some other trigger.
    """
    search_intent_landscape: str
    findings: List[ResearchFinding]
    summary: str
    opportunity_signal: str  # "Strong" | "Moderate" | "Weak" | "Unclear"

    def to_dict(self) -> dict:
        return {
            "search_intent_landscape": self.search_intent_landscape,
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
            "opportunity_signal": self.opportunity_signal,
        }


@dataclass
class FundingResearchOutput:
    """
    Output of the Funding Agent (Phase 2E of Secondary Research) —
    grounded, sourced findings on investor appetite and funding activity in
    this idea's space: how much capital adjacent/competing players have
    raised, whether any funded player is already targeting this specific
    niche, and how much competitive capital could flow in soon.
    """
    funding_landscape: str
    findings: List[ResearchFinding]
    summary: str
    opportunity_signal: str  # "Strong" | "Moderate" | "Weak" | "Unclear"

    def to_dict(self) -> dict:
        return {
            "funding_landscape": self.funding_landscape,
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
            "opportunity_signal": self.opportunity_signal,
        }


@dataclass
class JobMarketResearchOutput:
    """
    Output of the Job Market Agent (Phase 2F of Secondary Research) —
    grounded, sourced findings from hiring signals: whether competitors or
    adjacent players are staffing up for roles that suggest they're already
    building toward this idea's specific niche, ahead of any public launch.
    """
    job_market_landscape: str
    findings: List[ResearchFinding]
    summary: str
    opportunity_signal: str  # "Strong" | "Moderate" | "Weak" | "Unclear"

    def to_dict(self) -> dict:
        return {
            "job_market_landscape": self.job_market_landscape,
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
            "opportunity_signal": self.opportunity_signal,
        }


@dataclass
class SocialIntelligenceResearchOutput:
    """
    Output of the Social Intelligence Agent (Phase 2G of Secondary
    Research, the last of the 7) — grounded, sourced findings on real-time
    organic social conversation about this idea's problem: how often and in
    what tone the target audience posts about it, and how similar
    content/hook formats (scorecards, audits, comparisons) actually perform
    when shared, as opposed to assumed.
    """
    social_intelligence_landscape: str
    findings: List[ResearchFinding]
    summary: str
    opportunity_signal: str  # "Strong" | "Moderate" | "Weak" | "Unclear"

    def to_dict(self) -> dict:
        return {
            "social_intelligence_landscape": self.social_intelligence_landscape,
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
            "opportunity_signal": self.opportunity_signal,
        }


@dataclass
class HypothesisAssessment:
    """
    One Phase 1 hypothesis, assessed against the combined evidence from
    all secondary-research agents that were run for the session.
    """
    hypothesis: str
    verdict: str  # "Supported" | "Refuted" | "Mixed" | "Untested"
    evidence_summary: str
    supporting_agents: List[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SynthesisOutput:
    """
    Output of the Research Synthesizer (Phase 3) — the last analytical step
    before a go/no-go call. Reasons over every secondary-research agent's
    findings that exist for the session (not all 7 need to have been run)
    plus Phase 1's hypotheses, and rolls them into one opportunity
    assessment: which hypotheses actually held up, an overall score and
    recommendation, and what only primary research (real customer
    conversations) can still resolve.
    """
    opportunity_score: int  # 0-100
    recommendation: str  # "Pursue" | "Pursue with caution" | "Pivot needed" | "Do not pursue"
    executive_summary: str
    hypothesis_assessments: List[HypothesisAssessment]
    key_strengths: List[str]
    key_risks: List[str]
    critical_open_questions: List[str]
    recommended_next_steps: List[str]

    def to_dict(self) -> dict:
        return {
            "opportunity_score": self.opportunity_score,
            "recommendation": self.recommendation,
            "executive_summary": self.executive_summary,
            "hypothesis_assessments": [h.to_dict() for h in self.hypothesis_assessments],
            "key_strengths": self.key_strengths,
            "key_risks": self.key_risks,
            "critical_open_questions": self.critical_open_questions,
            "recommended_next_steps": self.recommended_next_steps,
        }


@dataclass
class ICPProfile:
    """One Ideal Customer Profile segment, built from the 9-step ICP
    framework (Market -> Industry -> Firmographics -> Technographics ->
    Buyer Persona -> Pain Points -> Buying Signals -> Scoring) — concrete
    enough to target, not a vague persona sketch. Exclusion Criteria and
    the scoring rubric/qualified-account spec live on ICPDiscoveryOutput
    instead, since those apply across all segments rather than per-segment."""
    segment_name: str  # short label, e.g. "Seed-to-Series A B2B SaaS founder-led marketers"
    market: str  # the broader market/category this segment buys within (TAM context)
    industry: str  # specific industry vertical(s), e.g. "B2B SaaS", not "technology"
    firmographics: str  # company stage, size range, geography
    technographics: str  # tools/platforms this segment typically already has in place, and what that signals about fit
    buyer_persona: str  # role/title, seniority, decision + budget authority
    pain_points: str  # the pain as THEY'D describe it
    buying_signals: str  # trigger events/intent signals (incl. budget/willingness-to-pay norms) that prompt a purchase
    evidence: str  # what research (Phase 1-3 + fresh external grounding) actually supports this segment being viable
    confidence: str  # "High" | "Medium" | "Low" — how evidence-backed this segment's claims are
    fit_score: int  # 0-100 — this segment's priority/fit score against the scoring rubric
    fit_score_rationale: str  # which rubric criteria drove the score, and why

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ScoringCriterion:
    """One weighted, checkable criterion in the ICP scoring rubric (Step
    9 — ICP Scoring & Prioritization). Reusable beyond the hypothesized
    segments above: the same rubric scores real candidate accounts once
    a founder pulls them into Clay/Apollo/Sales Navigator using the
    qualified-account spec."""
    criterion: str  # a specific, checkable criterion, e.g. "Uses a competing tool today"
    weight: int  # 0-100 — how much this criterion counts toward a candidate account's total score; all criteria should sum to ~100
    how_to_score: str  # concretely how to check/award this criterion for a real account

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class QualifiedAccountSpec:
    """Step 9's terminal deliverable: a ready-to-use filter spec for
    manually building a target-account list in a tool like Clay or Apollo.
    This pipeline does not call those APIs itself — it hands off a
    concrete-enough spec that a founder can paste straight into one."""
    firmographic_filters: str  # concrete filters mapping onto Clay/Apollo/Sales Navigator fields
    technographic_filters: str  # concrete tech-stack signals to filter/search for
    buyer_titles: List[str]  # specific job titles to search for as the buyer-persona contact
    buying_signal_filters: str  # concrete, searchable intent signals to prioritize (funding, hiring, tech adoption, ...)
    minimum_fit_score: int  # only pursue accounts scoring at/above this threshold (0-100) on the rubric

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ICPDiscoveryOutput:
    """
    Output of the ICP Discovery Agent (Phase 4) — the first phase that
    reasons about WHO to sell to, not just whether the idea is viable.
    Grounds itself in real-world buyer/segment benchmarks (via Perplexity)
    combined with everything already known from Phase 1-3 (problem
    statement, hypotheses, synthesis verdict, secondary-research findings),
    and ends in a scoring rubric plus a spec for building a real qualified-
    account list by hand (no Clay/Apollo API calls happen in this pipeline).
    """
    primary_icp: ICPProfile
    secondary_icps: List[ICPProfile]  # 0-2 other viable segments, if evidence supports them
    exclusion_criteria: str  # who looks superficially similar to the ICP but should NOT be targeted, and why
    scoring_rubric: List[ScoringCriterion]  # weighted criteria used to prioritize segments/accounts
    qualified_account_spec: QualifiedAccountSpec  # spec for manually building the real account list
    summary: str
    icp_confidence: str  # "High" | "Medium" | "Low" — how evidence-backed this ICP is overall
    recommended_validation_steps: List[str]  # concrete next actions to validate/refine via real customer contact

    def to_dict(self) -> dict:
        return {
            "primary_icp": self.primary_icp.to_dict(),
            "secondary_icps": [s.to_dict() for s in self.secondary_icps],
            "exclusion_criteria": self.exclusion_criteria,
            "scoring_rubric": [c.to_dict() for c in self.scoring_rubric],
            "qualified_account_spec": self.qualified_account_spec.to_dict(),
            "summary": self.summary,
            "icp_confidence": self.icp_confidence,
            "recommended_validation_steps": self.recommended_validation_steps,
        }


@dataclass
class MarketSizeEstimate:
    """One TAM/SAM/SOM tier estimate. Combines top-down (published
    market-size reports, where they exist) and bottom-up (company-count x
    average deal size) reasoning, since niche/emerging categories often
    lack a clean published number."""
    value_usd: str  # a range, e.g. "$450M-$600M annually" -- never false precision
    timeframe: str  # what the figure represents, e.g. "current annual market size" or "3-year obtainable revenue"
    methodology: str  # top-down (published estimate) and/or bottom-up (company-count x ACV), and exactly how derived
    key_assumptions: List[str]  # specific assumptions behind the number, so it can be sanity-checked/updated later
    confidence: str  # "High" | "Medium" | "Low"
    sources: List[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MarketSizingOutput:
    """
    Output of Phase 4b — Market Sizing (TAM/SAM/SOM). Runs after ICP
    Discovery: SAM narrows TAM using the ICP's actual firmographic/
    industry/technographic filters (not a generic percentage), and SOM
    applies a realistic capture-rate assumption grounded in the named
    competitors' scale/funding and the Phase 3 synthesis's confidence.
    """
    tam: MarketSizeEstimate
    sam: MarketSizeEstimate
    sam_narrowing_criteria: str  # exactly which ICP filters were applied to narrow TAM -> SAM
    som: MarketSizeEstimate
    som_capture_rationale: str  # why this capture rate/timeframe is realistic given competitors + synthesis
    overall_confidence: str  # "High" | "Medium" | "Low"
    summary: str

    def to_dict(self) -> dict:
        return {
            "tam": self.tam.to_dict(),
            "sam": self.sam.to_dict(),
            "sam_narrowing_criteria": self.sam_narrowing_criteria,
            "som": self.som.to_dict(),
            "som_capture_rationale": self.som_capture_rationale,
            "overall_confidence": self.overall_confidence,
            "summary": self.summary,
        }


@dataclass
class TargetAccount:
    """One verified, scored candidate company for the qualified-account
    list — the terminal deliverable of the 9-step ICP framework's final
    step. "Verified" means Apify successfully scraped the company's public
    LinkedIn page; candidates that don't verify are dropped rather than
    presented as a real recommendation (see
    TargetAccountListOutput.unverified_candidates)."""
    company_name: str
    linkedin_url: str
    website_url: str
    industry: str
    employee_count: str  # as reported by LinkedIn — a string since it's often a range/approximation
    fit_score: int  # 0-100, scored against the ICP's scoring_rubric
    fit_score_rationale: str
    key_matching_signals: List[str]  # concrete evidence this account matches, e.g. "708 employees on LinkedIn"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TargetAccountListOutput:
    """
    Output of the Target Account Agent (Phase 4c) — turns the ICP's
    qualified_account_spec and scoring_rubric from criteria into an actual
    ranked list of real, LinkedIn-verified candidate companies. Requires
    ICP Discovery to have been run first (it scores candidates against
    that phase's rubric); Market Sizing is optional context.
    """
    target_location: str  # the location filter actually used (may be "" if none was ever provided)
    accounts: List[TargetAccount]  # ranked highest fit_score first
    unverified_candidates: List[str]  # company names surfaced by research but not confirmed via a real LinkedIn scrape
    summary: str

    def to_dict(self) -> dict:
        return {
            "target_location": self.target_location,
            "accounts": [a.to_dict() for a in self.accounts],
            "unverified_candidates": self.unverified_candidates,
            "summary": self.summary,
        }


@dataclass
class DiscoveryQuestion:
    """One customer-discovery interview question, tied to a specific
    hypothesis or open question it's designed to test."""
    question: str
    tests: str  # which hypothesis/open question this is meant to validate or refute
    what_to_listen_for: str  # the signal that would count as validating vs. refuting

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RecruitingChannel:
    """One specific, named place to find real prospects matching the ICP."""
    channel: str
    why_this_channel: str
    evidence: str  # what supports this channel actually reaching the ICP

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CustomerDiscoveryOutput:
    """
    Output of the Customer Discovery Agent (Phase 5) — turns the ICP and
    the still-open hypotheses from Phase 3/4 into an actionable plan for
    talking to real prospective customers: a tailored interview guide
    (every question tied to a specific hypothesis/open question it tests),
    where to recruit design partners matching the ICP, an outreach message
    template, screening criteria, and what counts as a validating signal.
    """
    discovery_questions: List[DiscoveryQuestion]
    recruiting_channels: List[RecruitingChannel]
    outreach_message_template: str
    screening_criteria: List[str]
    success_criteria: str
    summary: str
    recommended_next_steps: List[str]

    def to_dict(self) -> dict:
        return {
            "discovery_questions": [q.to_dict() for q in self.discovery_questions],
            "recruiting_channels": [c.to_dict() for c in self.recruiting_channels],
            "outreach_message_template": self.outreach_message_template,
            "screening_criteria": self.screening_criteria,
            "success_criteria": self.success_criteria,
            "summary": self.summary,
            "recommended_next_steps": self.recommended_next_steps,
        }


@dataclass
class InterviewNote:
    """One raw customer-discovery interview, as reported by the founder
    (not fabricated or researched — this is primary data only the founder
    can supply)."""
    interviewee_label: str  # e.g. "Founder #1 - SaaS analytics tool" (no real names needed)
    fits_icp: str  # "Yes" | "No" | "Partial" | "Unsure" — founder's own quick judgment
    notes: str  # raw freeform notes/summary from the conversation

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class HypothesisValidation:
    """One hypothesis or discovery question, validated against actual
    interview evidence (not secondary research)."""
    hypothesis_or_question: str
    verdict: str  # "Validated" | "Refuted" | "Mixed" | "Inconclusive"
    evidence_summary: str  # what the interviews actually showed, referencing which ones
    supporting_interview_count: int  # how many interviews showed supporting signal

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ValidationOutput:
    """
    Output of the Validation Agent (Phase 6) — analyzes REAL interview
    notes the founder gathered (using the Phase 5 discovery plan) against
    the hypotheses and success criteria defined earlier in the pipeline,
    and produces a validation verdict. Pure reasoning over primary data
    the founder provides — no search, no secondary research.
    """
    overall_verdict: str  # "Validated" | "Partially Validated" | "Invalidated" | "Inconclusive — need more interviews"
    success_criteria_met: bool
    success_criteria_assessment: str  # why met/not met, with actual counts from the interviews
    hypothesis_validations: List[HypothesisValidation]
    notable_patterns: List[str]  # recurring themes/quotes across interviews
    red_flags: List[str]  # surprises or concerning signals not anticipated going in
    summary: str
    recommended_next_steps: List[str]

    def to_dict(self) -> dict:
        return {
            "overall_verdict": self.overall_verdict,
            "success_criteria_met": self.success_criteria_met,
            "success_criteria_assessment": self.success_criteria_assessment,
            "hypothesis_validations": [h.to_dict() for h in self.hypothesis_validations],
            "notable_patterns": self.notable_patterns,
            "red_flags": self.red_flags,
            "summary": self.summary,
            "recommended_next_steps": self.recommended_next_steps,
        }


@dataclass
class GTMChannelRecommendation:
    """One specific, named GTM channel/motion recommended as part of the
    launch mix — not a generic category ("content marketing") but a
    concrete instantiation of it for this specific idea/ICP."""
    channel: str
    why_this_channel: str
    evidence: str  # what supports this channel actually working for this ICP/category
    first_actions: List[str]  # 2-4 concrete actions to kick this channel off

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GTMRecommendationOutput:
    """
    Output of the GTM Recommendation Agent (Phase 7) — the final phase,
    turning everything learned in Phases 1-6 (problem statement, synthesis
    verdict, ICP, secondary research, and — if available — real validation
    results from Phase 6) into a concrete go-to-market plan: which motion to
    run, sharpened positioning, the specific channel mix, pricing/packaging,
    an ordered launch sequence, and the metrics that would tell the founder
    it's working.
    """
    primary_motion: str  # short label, e.g. "Content-led founder brand + free-audit lead magnet"
    positioning_statement: str
    messaging_pillars: List[str]
    primary_channels: List[GTMChannelRecommendation]
    pricing_and_packaging: str
    launch_sequence: List[str]  # ordered, concrete steps (roughly first 30/60/90 days)
    metrics_to_track: List[str]
    key_risks: List[str]
    confidence: str  # "High" | "Medium" | "Low"
    summary: str
    recommended_next_steps: List[str]

    def to_dict(self) -> dict:
        return {
            "primary_motion": self.primary_motion,
            "positioning_statement": self.positioning_statement,
            "messaging_pillars": self.messaging_pillars,
            "primary_channels": [c.to_dict() for c in self.primary_channels],
            "pricing_and_packaging": self.pricing_and_packaging,
            "launch_sequence": self.launch_sequence,
            "metrics_to_track": self.metrics_to_track,
            "key_risks": self.key_risks,
            "confidence": self.confidence,
            "summary": self.summary,
            "recommended_next_steps": self.recommended_next_steps,
        }
