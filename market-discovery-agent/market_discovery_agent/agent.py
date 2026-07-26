#!/usr/bin/env python3
"""
Early-Stage Market Discovery Agent — terminal CLI.

Implements, phase by phase, the workflow:

    Business Idea -> Problem Discovery -> Market Discovery -> ICP Discovery
    -> Customer Discovery -> Validation -> GTM Recommendation

All 7 phases are built: Business Understanding (Phase 1), the Research
Planner, 7 secondary-research agents (Phase 2), the Research Synthesizer
(Phase 3), ICP Discovery (Phase 4), Customer Discovery (Phase 5),
Validation (Phase 6), and GTM Recommendation (Phase 7). See README.md for
the full command reference.

All phases run on OpenAI + Perplexity — no Anthropic. Structured-output-
only steps (discover/plan/synthesize/validate) call OpenAI directly via
`llm_utils.call_openai_structured`; the 7 secondary-research agents and
the phases that ground themselves in live search (icp, customer-discovery,
gtm) use the two-step Perplexity(search) + OpenAI(structuring) pipeline in
`research_agents/_base.py`.

Usage:
    python agent.py init                     # Phase 1: collect input
    python agent.py discover --session <id>  # Phase 1: synthesize
    python agent.py plan --session <id>      # Research Planner
    python agent.py plan --session latest    # use most recent session
    python agent.py gtm --session latest     # Phase 7: GTM recommendation

Requires:
    pip install -r requirements.txt
    export OPENAI_API_KEY=sk-...
    export PERPLEXITY_API_KEY=pplx-...
"""
import argparse
import json
import os
import sys
from typing import Optional

from dotenv import load_dotenv

load_dotenv()  # walks up from cwd, so it finds market-discovery-agent/.env whether run from there or from market_discovery_agent/

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import state
import lead
from llm_utils import call_openai_structured
from models import FounderInput, Phase1Output, ResearchPlan, ResearchAgentBrief, ResearchQuestion
from research_agents.industry_agent import run_industry_research
from research_agents.competitor_agent import run_competitor_batch
from research_agents.community_agent import run_community_research
from research_agents.search_intent_agent import run_search_intent_research
from research_agents.funding_agent import run_funding_research
from research_agents.job_market_agent import run_job_market_research
from research_agents.social_intelligence_agent import run_social_intelligence_research
from synthesizer import run_synthesis, AGENT_DISPLAY
from icp_discovery import run_icp_discovery
from market_sizing import run_market_sizing
from target_account_agent import run_target_account_discovery
from lookalike_account_agent import run_lookalike_account_discovery
from customer_discovery import run_customer_discovery
from validation import run_validation
from gtm import run_gtm_recommendation


# --------------------------------------------------------------------------
# Terminal I/O helpers
# --------------------------------------------------------------------------

def _safe_input(prompt: str = "") -> str:
    """Wraps input() so a closed/exhausted stdin (piped input missing a
    trailing blank line, running in a context with no real interactive
    terminal, Ctrl+D/Ctrl+Z) fails with one clear message instead of an
    unhandled EOFError traceback. Every interactive prompt helper below
    routes through this rather than calling input() directly."""
    try:
        return input(prompt)
    except EOFError:
        print(
            "\n\nInput ended unexpectedly (no more lines to read from stdin). "
            "If you're piping input, make sure it has a blank line to end each "
            "multi-line field AND a final blank line to end the whole list. "
            "If you're running this interactively, use `python agent.py run "
            "--input <file>` instead for a fully non-interactive run."
        )
        sys.exit(1)


def _prompt(label: str, multiline: bool = False) -> str:
    if multiline:
        print(f"\n{label} (end with a blank line):")
        lines = []
        while True:
            line = _safe_input()
            if line.strip() == "" and lines:
                break
            if line.strip() == "" and not lines:
                continue
            lines.append(line)
        return "\n".join(lines).strip()
    return _safe_input(f"\n{label}: ").strip()


def _prompt_list(label: str) -> list:
    print(f"\n{label} (one per line, blank line to finish):")
    items = []
    while True:
        line = _safe_input(f"  {len(items) + 1}. ").strip()
        if line == "":
            break
        items.append(line)
    return items


def _section(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# --------------------------------------------------------------------------
# Phase 1a — collect input
# --------------------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> None:
    """Collects Phase 1 founder input. Interactive by default (prompts for
    each field); if `args.founder_input` is already set to a dict (used by
    `cmd_run`'s non-interactive pipeline, which reads it from a JSON file
    instead of prompting), that's used verbatim instead of prompting."""
    _section("PHASE 1 — Business Understanding: Input")

    pre_supplied = getattr(args, "founder_input", None)
    if pre_supplied is not None:
        founder_input = FounderInput(**pre_supplied)
    else:
        print("Answer in your own words. You can be rough — this just needs")
        print("to capture what's in your head right now.")

        product_idea = _prompt("Product idea — what are you building, in one or two sentences?")
        vision = _prompt("Vision — where does this go if it works?")
        features = _prompt_list("Features — the core things it does")
        assumptions = _prompt_list("Assumptions — things you believe but haven't proven")
        founder_knowledge = _prompt(
            "Founder knowledge — why you? what do you know about this space "
            "that most people don't?",
            multiline=True,
        )
        target_location = _prompt(
            "Target location — where should qualified target accounts be based? "
            "(e.g. 'India', 'United States'; leave blank for no location filter)"
        )

        founder_input = FounderInput(
            product_idea=product_idea,
            vision=vision,
            features=features,
            assumptions=assumptions,
            founder_knowledge=founder_knowledge,
            target_location=target_location,
        )

    session_id = args.session or state.new_session_id(founder_input.product_idea)
    state.save(session_id, {"founder_input": founder_input.to_dict()})

    _section("SAVED")
    print(f"Session ID: {session_id}")
    print(f"\nNext step:\n  python agent.py discover --session {session_id}")


# --------------------------------------------------------------------------
# Phase 1b — synthesize problem statement / hypotheses / success criteria
# --------------------------------------------------------------------------

PHASE1_TOOL = {
    "name": "record_phase1_output",
    "description": (
        "Record the synthesized problem statement, initial hypotheses, "
        "and success criteria for this business idea."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "problem_statement": {
                "type": "string",
                "description": (
                    "A sharp, falsifiable problem statement — who has "
                    "the problem, what the problem actually is, and why "
                    "it matters enough that someone would pay to solve it. "
                    "Not a restatement of the product idea."
                ),
            },
            "initial_hypotheses": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "3-6 testable hypotheses this business is implicitly "
                    "making (about the customer, the problem's severity, "
                    "willingness to pay, the channel, etc.) — phrased so "
                    "each one could be proven true or false by research."
                ),
            },
            "success_criteria": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "3-5 concrete, measurable signals that would tell the "
                    "founder this idea is worth pursuing further (not vague "
                    "goals — specific, checkable outcomes)."
                ),
            },
        },
        "required": ["problem_statement", "initial_hypotheses", "success_criteria"],
    },
}

PHASE1_SYSTEM_PROMPT = """You are a senior GTM engineer and market discovery \
analyst. Given a founder's raw, unpolished description of a product idea, \
your job is to sharpen it into:

1. A problem statement that is specific and falsifiable — not a rephrasing \
of the product idea, but a claim about who is hurting and why, that could \
turn out to be wrong.
2. Initial hypotheses — the assumptions the founder is implicitly making, \
made explicit and testable.
3. Success criteria — concrete signals (not vague aspirations) that would \
tell the founder this is worth pursuing.

Be direct and skeptical, the way a good advisor is. Do not just validate \
what the founder wrote — sharpen it, and call out where their input is \
vague or where they're assuming something they haven't shown evidence for. \
Call the tool exactly once with your output."""


def cmd_discover(args: argparse.Namespace) -> None:
    session_id = _resolve_session(args)
    data = state.load(session_id)

    if "founder_input" not in data:
        print("This session has no founder_input yet. Run `init` first.")
        sys.exit(1)

    founder_input = data["founder_input"]

    _section("PHASE 1 — Business Understanding: Synthesizing")
    print("Calling the model to sharpen your input into a problem statement,")
    print("hypotheses, and success criteria...\n")

    user_message = (
        f"Product idea: {founder_input['product_idea']}\n\n"
        f"Vision: {founder_input['vision']}\n\n"
        f"Features:\n" + "\n".join(f"- {f}" for f in founder_input["features"]) + "\n\n"
        f"Assumptions the founder already holds:\n"
        + "\n".join(f"- {a}" for a in founder_input["assumptions"]) + "\n\n"
        f"Founder knowledge / unfair advantage:\n{founder_input['founder_knowledge']}"
    )

    result = call_openai_structured(
        system=PHASE1_SYSTEM_PROMPT,
        user_message=user_message,
        tool_name="record_phase1_output",
        input_schema=PHASE1_TOOL["input_schema"],
    )

    phase1 = Phase1Output(
        problem_statement=result["problem_statement"],
        initial_hypotheses=result["initial_hypotheses"],
        success_criteria=result["success_criteria"],
    )

    data["phase1_output"] = phase1.to_dict()
    state.save(session_id, data)

    md_body = lead.render_business_understanding_md(founder_input, phase1.to_dict())
    lead.save_output(
        "Business Understanding", session_id, "Business Understanding", md_body,
        {"founder_input": founder_input, "phase1_output": phase1.to_dict()},
    )

    _section("PROBLEM STATEMENT")
    print(phase1.problem_statement)

    _section("INITIAL HYPOTHESES")
    for i, h in enumerate(phase1.initial_hypotheses, 1):
        print(f"  {i}. {h}")

    _section("SUCCESS CRITERIA")
    for i, s in enumerate(phase1.success_criteria, 1):
        print(f"  {i}. {s}")

    print(f"\nSession ID: {session_id}")
    print(f"\nNext step:\n  python agent.py plan --session {session_id}")


# --------------------------------------------------------------------------
# Research Planner — turn Phase 1 output into tailored agent briefs
# --------------------------------------------------------------------------

SECONDARY_AGENTS = [
    "Industry Agent",
    "Competitor Agent",
    "Community Agent",
    "Search Intent Agent",
    "Funding Agent",
    "Job Market Agent",
    "Social Intelligence Agent",
]

PLANNER_TOOL = {
    "name": "record_research_plan",
    "description": (
        "Record the research plan: which secondary-research agents to run, "
        "in what order, with what specific brief each."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "priority_order": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "The 7 agent names ordered from most to least valuable "
                    "to run first, given THIS specific problem statement and "
                    "hypotheses. Not every idea needs all 7 run with equal "
                    "priority."
                ),
            },
            "agent_briefs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "agent_name": {"type": "string"},
                        "objective": {
                            "type": "string",
                            "description": "One sentence: what this agent needs to find out for THIS idea specifically.",
                        },
                        "questions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {"type": "string"},
                                    "rationale": {
                                        "type": "string",
                                        "description": "Why this question matters for this specific hypothesis or problem statement.",
                                    },
                                },
                                "required": ["question", "rationale"],
                            },
                            "description": "3-5 specific research questions, tailored to this idea — not generic templates.",
                        },
                        "suggested_sources": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["agent_name", "objective", "questions", "suggested_sources"],
                },
                "description": "One brief per secondary-research agent (7 total).",
            },
            "open_questions_for_founder": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Anything the research plan can't resolve and only the "
                    "founder can answer (e.g. budget, timeline, willingness "
                    "to pursue a pivot the data might suggest)."
                ),
            },
        },
        "required": ["priority_order", "agent_briefs", "open_questions_for_founder"],
    },
}

PLANNER_SYSTEM_PROMPT = f"""You are the Research Planner in a Market \
Discovery pipeline. You do not do research yourself — you take a problem \
statement and a set of hypotheses, and produce a tailored brief for each \
of these 7 secondary-research agents: {", ".join(SECONDARY_AGENTS)}.

For each agent, write questions that are SPECIFIC to this business idea — \
never generic templates like "what is the market size?" with no connection \
to the actual hypotheses. Every question should trace back to a hypothesis \
or a gap in the problem statement that secondary research could actually \
close.

Also produce a priority order: which agents matter most for THIS idea, \
given what's genuinely uncertain versus already well-supported by the \
founder's own knowledge. Not every idea needs all 7 agents run with equal \
weight — say so plainly, and rank accordingly.

Call the tool exactly once with your output."""


def cmd_plan(args: argparse.Namespace) -> None:
    session_id = _resolve_session(args)
    data = state.load(session_id)

    if "phase1_output" not in data:
        print("This session has no phase1_output yet. Run `discover` first.")
        sys.exit(1)

    phase1 = data["phase1_output"]

    _section("RESEARCH PLANNER — building tailored briefs")
    print("Calling the model to turn your problem statement + hypotheses")
    print("into specific research briefs for each secondary agent...\n")

    user_message = (
        f"Problem statement:\n{phase1['problem_statement']}\n\n"
        f"Initial hypotheses:\n"
        + "\n".join(f"- {h}" for h in phase1["initial_hypotheses"]) + "\n\n"
        f"Success criteria:\n"
        + "\n".join(f"- {s}" for s in phase1["success_criteria"])
    )

    result = call_openai_structured(
        system=PLANNER_SYSTEM_PROMPT,
        user_message=user_message,
        tool_name="record_research_plan",
        input_schema=PLANNER_TOOL["input_schema"],
    )

    briefs = [
        ResearchAgentBrief(
            agent_name=b["agent_name"],
            objective=b["objective"],
            questions=[ResearchQuestion(**q) for q in b["questions"]],
            suggested_sources=b["suggested_sources"],
        )
        for b in result["agent_briefs"]
    ]
    plan = ResearchPlan(
        priority_order=result["priority_order"],
        agent_briefs=briefs,
        open_questions_for_founder=result.get("open_questions_for_founder", []),
    )

    data["research_plan"] = plan.to_dict()
    state.save(session_id, data)

    md_body = lead.render_research_plan_md(plan.to_dict())
    lead.save_output("Research Plan", session_id, "Research Plan", md_body, plan.to_dict())

    _section("PRIORITY ORDER")
    for i, name in enumerate(plan.priority_order, 1):
        print(f"  {i}. {name}")

    for brief in briefs:
        _section(brief.agent_name.upper())
        print(f"Objective: {brief.objective}\n")
        print("Questions:")
        for q in brief.questions:
            print(f"  - {q.question}")
            print(f"      why: {q.rationale}")
        print("\nSuggested sources: " + ", ".join(brief.suggested_sources))

    if plan.open_questions_for_founder:
        _section("OPEN QUESTIONS ONLY YOU CAN ANSWER")
        for q in plan.open_questions_for_founder:
            print(f"  - {q}")

    print(f"\nSession ID: {session_id}")
    print(f"\nFull plan saved to sessions/{session_id}.json")
    print("Secondary research execution (running these agents against real")
    print("sources) is the next phase to build.")


# --------------------------------------------------------------------------
# Phase 2A+ — landscape-level secondary-research agents (Industry, Community,
# and — once built — Search Intent, Funding, Job Market, Social Intelligence).
# All of these share one shape: a tailored brief from research_plan drives
# web-search questions, the model records {subject, findings, summary,
# opportunity_signal}. Per-item agents (like Competitor) don't fit this and
# get their own cmd_* — see below.
# --------------------------------------------------------------------------

def _find_brief(plan: dict, agent_name: str) -> Optional[dict]:
    return next(
        (b for b in plan.get("agent_briefs", []) if b["agent_name"] == agent_name),
        None,
    )


def _run_landscape_agent_command(
    args: argparse.Namespace,
    *,
    agent_name: str,
    label: str,
    run_fn,
    subject_attr: str,
    session_key: str,
) -> None:
    session_id = _resolve_session(args)
    data = state.load(session_id)

    if "phase1_output" not in data:
        print("This session has no phase1_output yet. Run `discover` first.")
        sys.exit(1)

    phase1 = data["phase1_output"]
    plan = data.get("research_plan")
    brief = _find_brief(plan, agent_name) if plan else None

    _section(f"{label.upper()} — researching")
    if brief:
        print("Using the tailored brief from your research plan...\n")
        questions = [q["question"] for q in brief["questions"]]
        rationale_by_question = {q["question"]: q["rationale"] for q in brief["questions"]}
        suggested_sources = brief["suggested_sources"]
    else:
        print("No research plan found for this session — using the default")
        print(f"questions instead. Run `plan` first for a brief tailored to")
        print("this specific idea.\n")
        questions = None
        rationale_by_question = None
        suggested_sources = None

    result = run_fn(
        problem_statement=phase1["problem_statement"],
        hypotheses=phase1["initial_hypotheses"],
        questions=questions,
        suggested_sources=suggested_sources,
        rationale_by_question=rationale_by_question,
    )

    result_dict = result.to_dict()
    data[session_key] = result_dict
    state.save(session_id, data)

    subject_name = getattr(result, subject_attr)
    md_body = lead.render_research_findings_md(
        agent_label=agent_name,
        subject_name=subject_name,
        findings=result_dict["findings"],
        summary=result.summary,
        opportunity_signal=result.opportunity_signal,
        objective=brief["objective"] if brief else None,
    )
    md_path, json_path = lead.save_output(
        agent_name, session_id, f"{label}: {subject_name}", md_body, result_dict,
    )

    _section(f"{label.upper()}: {subject_name}")
    for f in result.findings:
        print(f"\nQ: {f.question}")
        print(f"A: {f.answer}")
        print(f"   Confidence: {f.confidence}")
        print(f"   Sources: {', '.join(f.sources) if f.sources else '(none found)'}")

    _section("SUMMARY")
    print(result.summary)
    print(f"\nOpportunity signal: {result.opportunity_signal}")

    print(f"\nSession ID: {session_id}")
    print(f"Report saved to {md_path}\nand {json_path}")


def cmd_industry(args: argparse.Namespace) -> None:
    _run_landscape_agent_command(
        args,
        agent_name="Industry Agent",
        label="Industry Research",
        run_fn=run_industry_research,
        subject_attr="industry_name",
        session_key="industry_research",
    )


def cmd_community(args: argparse.Namespace) -> None:
    _run_landscape_agent_command(
        args,
        agent_name="Community Agent",
        label="Community Research",
        run_fn=run_community_research,
        subject_attr="community_landscape",
        session_key="community_research",
    )


def cmd_search_intent(args: argparse.Namespace) -> None:
    _run_landscape_agent_command(
        args,
        agent_name="Search Intent Agent",
        label="Search Intent Research",
        run_fn=run_search_intent_research,
        subject_attr="search_intent_landscape",
        session_key="search_intent_research",
    )


def cmd_funding(args: argparse.Namespace) -> None:
    _run_landscape_agent_command(
        args,
        agent_name="Funding Agent",
        label="Funding Research",
        run_fn=run_funding_research,
        subject_attr="funding_landscape",
        session_key="funding_research",
    )


def cmd_job_market(args: argparse.Namespace) -> None:
    _run_landscape_agent_command(
        args,
        agent_name="Job Market Agent",
        label="Job Market Research",
        run_fn=run_job_market_research,
        subject_attr="job_market_landscape",
        session_key="job_market_research",
    )


def cmd_social_intelligence(args: argparse.Namespace) -> None:
    _run_landscape_agent_command(
        args,
        agent_name="Social Intelligence Agent",
        label="Social Intelligence Research",
        run_fn=run_social_intelligence_research,
        subject_attr="social_intelligence_landscape",
        session_key="social_intelligence_research",
    )


# --------------------------------------------------------------------------
# Phase 2B — Competitor Agent (per-competitor, LinkedIn-URL-driven)
# --------------------------------------------------------------------------

def _prompt_competitors() -> list:
    print("\nCompetitors to research — public LinkedIn COMPANY PAGE URLs")
    print("(not personal profiles). One per line, blank line to finish:")
    competitors = []
    while True:
        url = _safe_input(f"  {len(competitors) + 1}. LinkedIn company page URL: ").strip()
        if url == "":
            break
        name = _safe_input("     Known name (optional, enter to skip): ").strip()
        competitors.append({"linkedin_url": url, "known_name": name or None})
    return competitors


def cmd_competitor(args: argparse.Namespace) -> None:
    """Interactive by default (prompts for LinkedIn URLs); if
    `args.competitors` is already set to a list (used by `cmd_run`'s
    non-interactive pipeline), that's used verbatim instead of prompting."""
    session_id = _resolve_session(args)
    data = state.load(session_id)

    if "phase1_output" not in data:
        print("This session has no phase1_output yet. Run `discover` first.")
        sys.exit(1)

    phase1 = data["phase1_output"]

    pre_supplied = getattr(args, "competitors", None)
    competitors = pre_supplied if pre_supplied is not None else _prompt_competitors()
    if not competitors:
        print("No competitors entered — nothing to research.")
        return

    _section("COMPETITOR AGENT — researching")

    def _on_result(result):
        print(f"  done: {result.company_name} ({result.linkedin_url})")

    results = run_competitor_batch(
        competitor_inputs=competitors,
        problem_statement=phase1["problem_statement"],
        on_result=_on_result,
    )

    result_dicts = [r.to_dict() for r in results]
    data["competitor_research"] = result_dicts
    state.save(session_id, data)

    md_body = lead.render_competitor_research_md(result_dicts)
    md_path, json_path = lead.save_output(
        "Competitor Agent", session_id, "Competitor Research", md_body,
        {"competitors": result_dicts},
    )

    for r in results:
        _section(f"COMPETITOR: {r.company_name}")
        print(f"LinkedIn: {r.linkedin_url}")
        print(f"Website: {r.website_url or '(not found)'}")
        for f in r.findings:
            print(f"\nQ: {f.question}")
            print(f"A: {f.answer}")
            print(f"   Confidence: {f.confidence}")
            print(f"   Sources: {', '.join(f.sources) if f.sources else '(none found)'}")
        print(f"\nSummary: {r.summary}")

    print(f"\nSession ID: {session_id}")
    print(f"Report saved to {md_path}\nand {json_path}")


# --------------------------------------------------------------------------
# Phase 3 — Research Synthesizer (rolls up whatever secondary-research
# agents have been run into one opportunity score + go/no-go call)
# --------------------------------------------------------------------------

def cmd_synthesize(args: argparse.Namespace) -> None:
    session_id = _resolve_session(args)
    data = state.load(session_id)

    if "phase1_output" not in data:
        print("This session has no phase1_output yet. Run `discover` first.")
        sys.exit(1)

    agents_present = [k for k in AGENT_DISPLAY if k in data]

    _section("RESEARCH SYNTHESIZER — synthesizing")
    if agents_present:
        names = ", ".join(AGENT_DISPLAY[k][0] for k in agents_present)
        print(f"Synthesizing {len(agents_present)} secondary-research agent(s): {names}\n")
    else:
        print("No secondary-research agents have been run yet for this session.")
        print("Synthesizing from Phase 1 alone — every hypothesis will come back 'Untested'.")
        print("Run `industry`/`community`/etc first for a real assessment.\n")

    result = run_synthesis(session_data=data)

    result_dict = result.to_dict()
    data["synthesis"] = result_dict
    state.save(session_id, data)

    md_body = lead.render_synthesis_md(result_dict)
    md_path, json_path = lead.save_output(
        "Research Synthesizer", session_id, "Research Synthesis & Opportunity Assessment",
        md_body, result_dict,
    )

    _section(f"RECOMMENDATION: {result.recommendation}  (score: {result.opportunity_score}/100)")
    print(result.executive_summary)

    _section("HYPOTHESIS ASSESSMENTS")
    for h in result.hypothesis_assessments:
        print(f"\n[{h.verdict}] {h.hypothesis}")
        print(f"  {h.evidence_summary}")
        print(f"  Evidence from: {', '.join(h.supporting_agents) if h.supporting_agents else '(none)'}")

    _section("KEY STRENGTHS")
    for s in result.key_strengths:
        print(f"  + {s}")

    _section("KEY RISKS")
    for r in result.key_risks:
        print(f"  - {r}")

    _section("CRITICAL OPEN QUESTIONS (primary research needed)")
    for q in result.critical_open_questions:
        print(f"  ? {q}")

    _section("RECOMMENDED NEXT STEPS")
    for i, s in enumerate(result.recommended_next_steps, 1):
        print(f"  {i}. {s}")

    print(f"\nSession ID: {session_id}")
    print(f"Report saved to {md_path}\nand {json_path}")


# --------------------------------------------------------------------------
# Phase 4 — ICP Discovery (who to sell to, not just whether the idea works)
# --------------------------------------------------------------------------

def cmd_icp(args: argparse.Namespace) -> None:
    session_id = _resolve_session(args)
    data = state.load(session_id)

    if "phase1_output" not in data:
        print("This session has no phase1_output yet. Run `discover` first.")
        sys.exit(1)

    _section("ICP DISCOVERY — researching")
    context_notes = []
    context_notes.append("synthesis" if "synthesis" in data else "no synthesis")
    agents_present = [k for k in AGENT_DISPLAY if k in data]
    context_notes.append(f"{len(agents_present)} secondary-research agent(s)" if agents_present else "no secondary research")
    print(f"Context available: {', '.join(context_notes)}.")
    if not agents_present and "synthesis" not in data:
        print("Working from Phase 1 alone plus fresh external buyer/segment research —")
        print("run `synthesize` (and the secondary-research agents) first for a sharper ICP.\n")
    else:
        print()

    result = run_icp_discovery(session_data=data)

    result_dict = result.to_dict()
    data["icp_discovery"] = result_dict
    state.save(session_id, data)

    md_body = lead.render_icp_discovery_md(result_dict)
    md_path, json_path = lead.save_output(
        "ICP Discovery Agent", session_id, "ICP Discovery", md_body, result_dict,
    )

    _section(
        f"PRIMARY ICP: {result.primary_icp.segment_name}  "
        f"(confidence: {result.primary_icp.confidence}, fit score: {result.primary_icp.fit_score}/100)"
    )
    print(f"Market: {result.primary_icp.market}")
    print(f"Industry: {result.primary_icp.industry}")
    print(f"Firmographics: {result.primary_icp.firmographics}")
    print(f"Technographics: {result.primary_icp.technographics}")
    print(f"Buyer persona: {result.primary_icp.buyer_persona}")
    print(f"Pain points: {result.primary_icp.pain_points}")
    print(f"Buying signals: {result.primary_icp.buying_signals}")
    print(f"Evidence: {result.primary_icp.evidence}")

    if result.secondary_icps:
        _section("SECONDARY ICPs")
        for p in result.secondary_icps:
            print(f"\n{p.segment_name} (confidence: {p.confidence}, fit score: {p.fit_score}/100)")
            print(f"  {p.firmographics}")
            print(f"  {p.buyer_persona}")

    _section("EXCLUSION CRITERIA — WHO NOT TO TARGET")
    print(result.exclusion_criteria)

    _section("ICP SCORING RUBRIC")
    for c in result.scoring_rubric:
        print(f"  - {c.criterion} (weight: {c.weight}) — {c.how_to_score}")

    _section("QUALIFIED ACCOUNT SPEC — paste into Clay / Apollo / Sales Navigator")
    spec = result.qualified_account_spec
    print(f"Firmographic filters: {spec.firmographic_filters}")
    print(f"Technographic filters: {spec.technographic_filters}")
    print(f"Buyer titles: {', '.join(spec.buyer_titles)}")
    print(f"Buying-signal filters: {spec.buying_signal_filters}")
    print(f"Minimum fit score to pursue: {spec.minimum_fit_score}/100")

    _section(f"SUMMARY  (overall ICP confidence: {result.icp_confidence})")
    print(result.summary)

    _section("RECOMMENDED VALIDATION STEPS")
    for i, s in enumerate(result.recommended_validation_steps, 1):
        print(f"  {i}. {s}")

    print(f"\nSession ID: {session_id}")
    print(f"Report saved to {md_path}\nand {json_path}")


# --------------------------------------------------------------------------
# Phase 4b — Market Sizing (TAM / SAM / SOM)
# --------------------------------------------------------------------------

def cmd_market_sizing(args: argparse.Namespace) -> None:
    session_id = _resolve_session(args)
    data = state.load(session_id)

    if "phase1_output" not in data:
        print("This session has no phase1_output yet. Run `discover` first.")
        sys.exit(1)

    _section("MARKET SIZING — researching")
    context_notes = []
    context_notes.append("ICP" if "icp_discovery" in data else "no ICP")
    context_notes.append("synthesis" if "synthesis" in data else "no synthesis")
    agents_present = [k for k in AGENT_DISPLAY if k in data]
    context_notes.append(f"{len(agents_present)} secondary-research agent(s)" if agents_present else "no secondary research")
    print(f"Context available: {', '.join(context_notes)}.")
    if "icp_discovery" not in data:
        print("Run `icp` first so SAM can be narrowed by real firmographic/technographic filters —")
        print("without it, SAM falls back to the segment implied by the problem statement.\n")
    else:
        print()

    result = run_market_sizing(session_data=data)

    result_dict = result.to_dict()
    data["market_sizing"] = result_dict
    state.save(session_id, data)

    md_body = lead.render_market_sizing_md(result_dict)
    md_path, json_path = lead.save_output(
        "Market Sizing Agent", session_id, "Market Sizing (TAM / SAM / SOM)", md_body, result_dict,
    )

    _section(f"TAM: {result.tam.value_usd}  (confidence: {result.tam.confidence})")
    print(f"Timeframe: {result.tam.timeframe}")
    print(f"Methodology: {result.tam.methodology}")

    _section(f"SAM: {result.sam.value_usd}  (confidence: {result.sam.confidence})")
    print(f"Narrowed by: {result.sam_narrowing_criteria}")

    _section(f"SOM: {result.som.value_usd}  (confidence: {result.som.confidence})")
    print(f"Capture rationale: {result.som_capture_rationale}")

    _section(f"SUMMARY  (overall confidence: {result.overall_confidence})")
    print(result.summary)

    print(f"\nSession ID: {session_id}")
    print(f"Report saved to {md_path}\nand {json_path}")


# --------------------------------------------------------------------------
# Phase 4c — Target Account Agent (real, LinkedIn-verified candidate
# companies scored against the ICP's qualified-account spec/rubric)
# --------------------------------------------------------------------------

def cmd_target_accounts(args: argparse.Namespace) -> None:
    session_id = _resolve_session(args)
    data = state.load(session_id)

    if "phase1_output" not in data:
        print("This session has no phase1_output yet. Run `discover` first.")
        sys.exit(1)
    if "icp_discovery" not in data:
        print("This session has no icp_discovery yet. Run `icp` first —")
        print("Target Account Agent scores candidates against Phase 4's scoring rubric.")
        sys.exit(1)

    location = args.location or data.get("founder_input", {}).get("target_location") or ""
    _section("TARGET ACCOUNT AGENT — researching")
    print(f"Target location: {location or '(none set — searching without a location filter)'}")
    print(f"Requested count: {args.count}\n")

    try:
        result = run_target_account_discovery(session_data=data, target_location=args.location, count=args.count)
    except RuntimeError as e:
        print(str(e))
        sys.exit(1)

    result_dict = result.to_dict()
    data["target_accounts"] = result_dict
    state.save(session_id, data)

    md_body = lead.render_target_accounts_md(result_dict)
    md_path, json_path = lead.save_output(
        "Target Account Agent", session_id, "Target Account List", md_body, result_dict,
    )

    if result.accounts:
        _section(f"TARGET ACCOUNTS  ({len(result.accounts)} verified)")
        for a in result.accounts:
            print(f"\n{a.company_name}  (fit score: {a.fit_score}/100)")
            print(f"  LinkedIn: {a.linkedin_url}")
            print(f"  Website: {a.website_url}")
            print(f"  Industry: {a.industry} | Employees: {a.employee_count}")
            print(f"  Why: {a.fit_score_rationale}")
    else:
        _section("NO VERIFIED TARGET ACCOUNTS")
        print("No candidates could be confirmed via a real LinkedIn scrape this run.")

    if result.unverified_candidates:
        _section("UNVERIFIED CANDIDATES (dropped, not recommended)")
        for name in result.unverified_candidates:
            print(f"  - {name}")

    _section("SUMMARY")
    print(result.summary)

    print(f"\nSession ID: {session_id}")
    print(f"Report saved to {md_path}\nand {json_path}")


# --------------------------------------------------------------------------
# Phase 4d — Lookalike Account Agent (more real, LinkedIn-verified
# companies resembling the Target Account Agent's verified seed accounts)
# --------------------------------------------------------------------------

def cmd_lookalike_accounts(args: argparse.Namespace) -> None:
    session_id = _resolve_session(args)
    data = state.load(session_id)

    if "phase1_output" not in data:
        print("This session has no phase1_output yet. Run `discover` first.")
        sys.exit(1)
    if "icp_discovery" not in data:
        print("This session has no icp_discovery yet. Run `icp` first —")
        print("Lookalike Account Agent scores candidates against Phase 4's scoring rubric.")
        sys.exit(1)
    if "target_accounts" not in data:
        print("This session has no target_accounts yet. Run `target-accounts` first —")
        print("Lookalike Account Agent uses its verified accounts as the seed set.")
        sys.exit(1)

    location = args.location or data.get("target_accounts", {}).get("target_location") or ""
    _section("LOOKALIKE ACCOUNT AGENT — researching")
    print(f"Target location: {location or '(none set — searching without a location filter)'}")
    print(f"Requested count: {args.count}\n")

    try:
        result = run_lookalike_account_discovery(session_data=data, target_location=args.location, count=args.count)
    except RuntimeError as e:
        print(str(e))
        sys.exit(1)

    result_dict = result.to_dict()
    data["lookalike_accounts"] = result_dict
    state.save(session_id, data)

    md_body = lead.render_target_accounts_md(result_dict)
    md_path, json_path = lead.save_output(
        "Lookalike Account Agent", session_id, "Lookalike Account List", md_body, result_dict,
    )

    if result.accounts:
        _section(f"LOOKALIKE ACCOUNTS  ({len(result.accounts)} verified)")
        for a in result.accounts:
            print(f"\n{a.company_name}  (fit score: {a.fit_score}/100)")
            print(f"  LinkedIn: {a.linkedin_url}")
            print(f"  Website: {a.website_url}")
            print(f"  Industry: {a.industry} | Employees: {a.employee_count}")
            print(f"  Why: {a.fit_score_rationale}")
    else:
        _section("NO VERIFIED LOOKALIKE ACCOUNTS")
        print("No candidates could be confirmed via a real LinkedIn scrape this run.")

    if result.unverified_candidates:
        _section("UNVERIFIED CANDIDATES (dropped, not recommended)")
        for name in result.unverified_candidates:
            print(f"  - {name}")

    _section("SUMMARY")
    print(result.summary)

    print(f"\nSession ID: {session_id}")
    print(f"Report saved to {md_path}\nand {json_path}")


# --------------------------------------------------------------------------
# Phase 5 — Customer Discovery (interview guide, recruiting channels,
# outreach template, and success criteria for talking to real prospects)
# --------------------------------------------------------------------------

def cmd_customer_discovery(args: argparse.Namespace) -> None:
    session_id = _resolve_session(args)
    data = state.load(session_id)

    if "phase1_output" not in data:
        print("This session has no phase1_output yet. Run `discover` first.")
        sys.exit(1)

    _section("CUSTOMER DISCOVERY — researching")
    context_notes = []
    context_notes.append("ICP" if "icp_discovery" in data else "no ICP")
    context_notes.append("synthesis" if "synthesis" in data else "no synthesis")
    agents_present = [k for k in AGENT_DISPLAY if k in data]
    context_notes.append(f"{len(agents_present)} secondary-research agent(s)" if agents_present else "no secondary research")
    print(f"Context available: {', '.join(context_notes)}.")
    if "icp_discovery" not in data:
        print("Run `icp` first for a plan targeted at a specific buyer segment —")
        print("without it, questions are built around the founder's raw hypotheses.\n")
    else:
        print()

    result = run_customer_discovery(session_data=data)

    result_dict = result.to_dict()
    data["customer_discovery"] = result_dict
    state.save(session_id, data)

    md_body = lead.render_customer_discovery_md(result_dict)
    md_path, json_path = lead.save_output(
        "Customer Discovery Agent", session_id, "Customer Discovery Plan", md_body, result_dict,
    )

    _section("DISCOVERY QUESTIONS")
    for q in result.discovery_questions:
        print(f"\nQ: {q.question}")
        print(f"  Tests: {q.tests}")
        print(f"  Listen for: {q.what_to_listen_for}")

    _section("RECRUITING CHANNELS")
    for c in result.recruiting_channels:
        print(f"\n{c.channel}")
        print(f"  Why: {c.why_this_channel}")
        print(f"  Evidence: {c.evidence}")

    _section("OUTREACH MESSAGE TEMPLATE")
    print(result.outreach_message_template)

    _section("SCREENING CRITERIA")
    for s in result.screening_criteria:
        print(f"  - {s}")

    _section("SUCCESS CRITERIA")
    print(result.success_criteria)

    _section("SUMMARY")
    print(result.summary)

    _section("RECOMMENDED NEXT STEPS")
    for i, s in enumerate(result.recommended_next_steps, 1):
        print(f"  {i}. {s}")

    print(f"\nSession ID: {session_id}")
    print(f"Report saved to {md_path}\nand {json_path}")


# --------------------------------------------------------------------------
# Phase 6 — Validation (analyzes REAL interview notes the founder gathered
# against the hypotheses/success criteria from earlier phases)
# --------------------------------------------------------------------------

def _prompt_interviews() -> list:
    print("\nEnter notes from the customer-discovery interviews you conducted")
    print("(ideally using the Phase 5 discovery guide). One interview at a")
    print("time — leave the interviewee label blank when you're done.")
    interviews = []
    while True:
        label = _safe_input(f"\n  Interview {len(interviews) + 1} — interviewee label (e.g. 'Founder #1', blank to finish): ").strip()
        if label == "":
            break
        fits = _safe_input("    Fits the ICP? (Yes/No/Partial/Unsure): ").strip() or "Unsure"
        notes = _prompt("    Notes from this conversation", multiline=True)
        interviews.append({"interviewee_label": label, "fits_icp": fits, "notes": notes})
    return interviews


def cmd_validate(args: argparse.Namespace) -> None:
    """Interactive by default (prompts for interview notes); if
    `args.interviews` is already set to a list (used by `cmd_run`'s
    non-interactive pipeline, when the input file supplies real interview
    notes), that's used verbatim instead of prompting."""
    session_id = _resolve_session(args)
    data = state.load(session_id)

    if "phase1_output" not in data:
        print("This session has no phase1_output yet. Run `discover` first.")
        sys.exit(1)

    _section("VALIDATION — enter your interview notes")
    if "customer_discovery" in data:
        print(f"Success criteria to check against: {data['customer_discovery']['success_criteria']}")
    else:
        print("No Phase 5 customer discovery plan found for this session —")
        print("falling back to your Phase 1 success criteria. Run `customer-discovery`")
        print("first for a plan with concrete, falsifiable success criteria.")

    pre_supplied = getattr(args, "interviews", None)
    interviews = pre_supplied if pre_supplied is not None else _prompt_interviews()
    if not interviews:
        print("No interviews entered — nothing to validate.")
        return

    _section("VALIDATION — analyzing")
    print(f"Analyzing {len(interviews)} interview(s) against your hypotheses and success criteria...\n")

    result = run_validation(session_data=data, interviews=interviews)

    result_dict = result.to_dict()
    data["interview_notes"] = interviews
    data["validation"] = result_dict
    state.save(session_id, data)

    md_body = lead.render_validation_md(result_dict, interviews)
    md_path, json_path = lead.save_output(
        "Validation Agent", session_id, "Validation Results", md_body, result_dict,
    )

    met = "Yes" if result.success_criteria_met else "No"
    _section(f"VERDICT: {result.overall_verdict}  (success criteria met: {met})")
    print(result.success_criteria_assessment)

    _section("HYPOTHESIS VALIDATIONS")
    for h in result.hypothesis_validations:
        print(f"\n[{h.verdict}] {h.hypothesis_or_question}")
        print(f"  {h.evidence_summary}")
        print(f"  Supporting interviews: {h.supporting_interview_count}")

    _section("NOTABLE PATTERNS")
    for p in result.notable_patterns:
        print(f"  + {p}")

    _section("RED FLAGS")
    if result.red_flags:
        for r in result.red_flags:
            print(f"  ! {r}")
    else:
        print("  (none noted)")

    _section("SUMMARY")
    print(result.summary)

    _section("RECOMMENDED NEXT STEPS")
    for i, s in enumerate(result.recommended_next_steps, 1):
        print(f"  {i}. {s}")

    print(f"\nSession ID: {session_id}")
    print(f"Report saved to {md_path}\nand {json_path}")


# --------------------------------------------------------------------------
# Phase 7 — GTM Recommendation (final phase: turns everything learned into
# one concrete go-to-market plan — motion, positioning, channels, pricing,
# launch sequence, and the metrics that would tell the founder it's working)
# --------------------------------------------------------------------------

def cmd_gtm(args: argparse.Namespace) -> None:
    session_id = _resolve_session(args)
    data = state.load(session_id)

    if "phase1_output" not in data:
        print("This session has no phase1_output yet. Run `discover` first.")
        sys.exit(1)

    _section("GTM RECOMMENDATION — researching")
    context_notes = []
    context_notes.append("synthesis" if "synthesis" in data else "no synthesis")
    context_notes.append("ICP" if "icp_discovery" in data else "no ICP")
    agents_present = [k for k in AGENT_DISPLAY if k in data]
    context_notes.append(f"{len(agents_present)} secondary-research agent(s)" if agents_present else "no secondary research")
    context_notes.append("customer discovery plan" if "customer_discovery" in data else "no customer discovery plan")
    context_notes.append("validation (real interviews)" if "validation" in data else "no validation")
    print(f"Context available: {', '.join(context_notes)}.")
    if "validation" not in data:
        print("No Phase 6 validation found for this session — recommending a")
        print("narrower, validation-first motion rather than a full launch plan.")
        print("Run `validate` first if you've already conducted real interviews.\n")
    else:
        print()

    result = run_gtm_recommendation(session_data=data)

    result_dict = result.to_dict()
    data["gtm_recommendation"] = result_dict
    state.save(session_id, data)

    md_body = lead.render_gtm_recommendation_md(result_dict)
    md_path, json_path = lead.save_output(
        "GTM Recommendation Agent", session_id, "GTM Recommendation", md_body, result_dict,
    )

    _section(f"PRIMARY MOTION: {result.primary_motion}  (confidence: {result.confidence})")
    print(result.summary)

    _section("POSITIONING STATEMENT")
    print(result.positioning_statement)

    _section("MESSAGING PILLARS")
    for m in result.messaging_pillars:
        print(f"  - {m}")

    _section("PRIMARY CHANNELS")
    for c in result.primary_channels:
        print(f"\n{c.channel}")
        print(f"  Why: {c.why_this_channel}")
        print(f"  Evidence: {c.evidence}")
        print("  First actions:")
        for i, a in enumerate(c.first_actions, 1):
            print(f"    {i}. {a}")

    _section("PRICING & PACKAGING")
    print(result.pricing_and_packaging)

    _section("LAUNCH SEQUENCE")
    for i, s in enumerate(result.launch_sequence, 1):
        print(f"  {i}. {s}")

    _section("METRICS TO TRACK")
    for m in result.metrics_to_track:
        print(f"  - {m}")

    _section("KEY RISKS")
    for r in result.key_risks:
        print(f"  - {r}")

    _section("RECOMMENDED NEXT STEPS")
    for i, s in enumerate(result.recommended_next_steps, 1):
        print(f"  {i}. {s}")

    print(f"\nSession ID: {session_id}")
    print(f"Report saved to {md_path}\nand {json_path}")


# --------------------------------------------------------------------------
# Full pipeline — one JSON input file in, zero interactive prompts, every
# phase run and saved automatically. See input_template.json for the schema.
# --------------------------------------------------------------------------

def cmd_run(args: argparse.Namespace) -> None:
    """Runs the ENTIRE pipeline start to finish from one JSON input file,
    with NO interactive prompts or confirmations anywhere — the single
    entrypoint for "give it input once, come back to finished output."

    Every phase is invoked by calling its existing `cmd_*` handler
    directly with a constructed `argparse.Namespace`, so this reuses each
    phase's existing terminal output and output/-saving logic verbatim
    rather than duplicating it. `cmd_init`/`cmd_competitor`/`cmd_validate`
    accept pre-supplied data (`founder_input`/`competitors`/`interviews`)
    for exactly this reason — this is their non-interactive path.

    Validation (Phase 6) is the one phase that's skipped rather than
    faked when the input doesn't supply it: there is no way to validate
    against real customer interviews that haven't happened yet. GTM
    (Phase 7) still runs either way — it already knows how to scope
    itself down to a validation-first motion when Phase 6 hasn't run
    (see `gtm.py`), so running it unconditionally is safe and correct.
    Competitor research (Phase 2B) is likewise skipped if the input
    supplies no competitor LinkedIn URLs, rather than prompting for them.
    """
    with open(args.input, encoding="utf-8") as f:
        payload = json.load(f)

    required = ["product_idea", "vision", "features", "assumptions", "founder_knowledge"]
    missing = [k for k in required if k not in payload]
    if missing:
        print(f"Input file is missing required field(s): {', '.join(missing)}")
        sys.exit(1)

    founder_input = {
        "product_idea": payload["product_idea"],
        "vision": payload["vision"],
        "features": payload["features"],
        "assumptions": payload["assumptions"],
        "founder_knowledge": payload["founder_knowledge"],
        "target_location": payload.get("target_location", ""),
    }
    competitors = payload.get("competitors") or []
    interviews = payload.get("interview_notes") or []
    target_account_count = payload.get("target_account_count", 5)

    session_id = args.session or state.new_session_id(founder_input["product_idea"])

    cmd_init(argparse.Namespace(session=session_id, founder_input=founder_input))
    cmd_discover(argparse.Namespace(session=session_id))
    cmd_plan(argparse.Namespace(session=session_id))
    cmd_industry(argparse.Namespace(session=session_id))
    cmd_community(argparse.Namespace(session=session_id))
    cmd_search_intent(argparse.Namespace(session=session_id))
    cmd_funding(argparse.Namespace(session=session_id))
    cmd_job_market(argparse.Namespace(session=session_id))
    cmd_social_intelligence(argparse.Namespace(session=session_id))

    if competitors:
        cmd_competitor(argparse.Namespace(session=session_id, competitors=competitors))
    else:
        print("\n(no `competitors` supplied in input — skipping Competitor Agent)")

    cmd_synthesize(argparse.Namespace(session=session_id))
    cmd_icp(argparse.Namespace(session=session_id))
    cmd_market_sizing(argparse.Namespace(session=session_id))
    cmd_target_accounts(argparse.Namespace(session=session_id, location=None, count=target_account_count))
    cmd_customer_discovery(argparse.Namespace(session=session_id))

    if interviews:
        cmd_validate(argparse.Namespace(session=session_id, interviews=interviews))
    else:
        print("\n(no `interview_notes` supplied in input — skipping Validation; "
              "GTM will scope down to a validation-first motion accordingly)")

    cmd_gtm(argparse.Namespace(session=session_id))

    print("\n" + "=" * 70)
    print("The agent has completed the run. The outputs have been generated and "
          f"saved to the respective folder (output/*/{session_id}.md and .json).")
    print("Please review the results.")
    print("=" * 70)


# --------------------------------------------------------------------------
# CLI wiring
# --------------------------------------------------------------------------

def _resolve_session(args: argparse.Namespace) -> str:
    if args.session == "latest":
        return state.latest_session_id()
    if not args.session:
        print("Pass --session <id> (from `init`'s output) or --session latest")
        sys.exit(1)
    return args.session


def main() -> None:
    parser = argparse.ArgumentParser(description="Early-Stage Market Discovery Agent")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Run the ENTIRE pipeline start to finish from one JSON input file — zero interactive prompts (see input_template.json)")
    p_run.add_argument("--input", required=True, help="Path to a JSON file with founder input, competitors, target_location, etc. — see input_template.json")
    p_run.add_argument("--session", help="Session ID to use (default: auto-generated from product_idea)")
    p_run.set_defaults(func=cmd_run)

    p_init = sub.add_parser("init", help="Phase 1: collect founder input")
    p_init.add_argument("--session", help="Session ID to write to (default: auto-generated)")
    p_init.set_defaults(func=cmd_init)

    p_discover = sub.add_parser("discover", help="Phase 1: synthesize problem statement / hypotheses / success criteria")
    p_discover.add_argument("--session", required=True, help="Session ID from `init`, or 'latest'")
    p_discover.set_defaults(func=cmd_discover)

    p_plan = sub.add_parser("plan", help="Research Planner: build tailored briefs for secondary research")
    p_plan.add_argument("--session", required=True, help="Session ID, or 'latest'")
    p_plan.set_defaults(func=cmd_plan)

    p_industry = sub.add_parser("industry", help="Phase 2A: run the Industry Agent (web-search-grounded industry research)")
    p_industry.add_argument("--session", required=True, help="Session ID, or 'latest'")
    p_industry.set_defaults(func=cmd_industry)

    p_competitor = sub.add_parser("competitor", help="Phase 2B: run the Competitor Agent (prompts for competitor LinkedIn URLs, researches each one)")
    p_competitor.add_argument("--session", required=True, help="Session ID, or 'latest'")
    p_competitor.set_defaults(func=cmd_competitor)

    p_community = sub.add_parser("community", help="Phase 2C: run the Community Agent (web-search-grounded evidence from founder/user communities)")
    p_community.add_argument("--session", required=True, help="Session ID, or 'latest'")
    p_community.set_defaults(func=cmd_community)

    p_search_intent = sub.add_parser("search-intent", help="Phase 2D: run the Search Intent Agent (web-search-grounded search demand/volume research)")
    p_search_intent.add_argument("--session", required=True, help="Session ID, or 'latest'")
    p_search_intent.set_defaults(func=cmd_search_intent)

    p_funding = sub.add_parser("funding", help="Phase 2E: run the Funding Agent (web-search-grounded investor/funding research)")
    p_funding.add_argument("--session", required=True, help="Session ID, or 'latest'")
    p_funding.set_defaults(func=cmd_funding)

    p_job_market = sub.add_parser("job-market", help="Phase 2F: run the Job Market Agent (web-search-grounded hiring-signal research)")
    p_job_market.add_argument("--session", required=True, help="Session ID, or 'latest'")
    p_job_market.set_defaults(func=cmd_job_market)

    p_social = sub.add_parser("social-intelligence", help="Phase 2G: run the Social Intelligence Agent (web-search-grounded organic social/virality research)")
    p_social.add_argument("--session", required=True, help="Session ID, or 'latest'")
    p_social.set_defaults(func=cmd_social_intelligence)

    p_synthesize = sub.add_parser("synthesize", help="Phase 3: synthesize all secondary research into an opportunity score + go/no-go recommendation")
    p_synthesize.add_argument("--session", required=True, help="Session ID, or 'latest'")
    p_synthesize.set_defaults(func=cmd_synthesize)

    p_icp = sub.add_parser("icp", help="Phase 4: discover the Ideal Customer Profile (firmographics, technographics, buyer persona, exclusion criteria, scoring rubric, qualified-account spec)")
    p_icp.add_argument("--session", required=True, help="Session ID, or 'latest'")
    p_icp.set_defaults(func=cmd_icp)

    p_market_sizing = sub.add_parser("market-sizing", help="Phase 4b: size TAM / SAM / SOM (run after `icp` for a properly narrowed SAM)")
    p_market_sizing.add_argument("--session", required=True, help="Session ID, or 'latest'")
    p_market_sizing.set_defaults(func=cmd_market_sizing)

    p_target_accounts = sub.add_parser("target-accounts", help="Phase 4c: find real, LinkedIn-verified target companies scored against the ICP's qualified-account spec (requires `icp` to have been run)")
    p_target_accounts.add_argument("--session", required=True, help="Session ID, or 'latest'")
    p_target_accounts.add_argument("--location", help="Override the target location (defaults to founder_input.target_location from `init`, or none)")
    p_target_accounts.add_argument("--count", type=int, default=5, help="Number of verified target accounts to return (default: 5)")
    p_target_accounts.set_defaults(func=cmd_target_accounts)

    p_lookalike_accounts = sub.add_parser("lookalike-accounts", help="Phase 4d: find MORE real, LinkedIn-verified companies resembling the Target Account Agent's verified accounts (requires `target-accounts` to have been run)")
    p_lookalike_accounts.add_argument("--session", required=True, help="Session ID, or 'latest'")
    p_lookalike_accounts.add_argument("--location", help="Override the target location (defaults to the prior target-accounts run's location, or founder_input.target_location)")
    p_lookalike_accounts.add_argument("--count", type=int, default=5, help="Number of verified lookalike accounts to return (default: 5)")
    p_lookalike_accounts.set_defaults(func=cmd_lookalike_accounts)

    p_customer_discovery = sub.add_parser("customer-discovery", help="Phase 5: build a customer discovery plan (interview guide, recruiting channels, outreach template)")
    p_customer_discovery.add_argument("--session", required=True, help="Session ID, or 'latest'")
    p_customer_discovery.set_defaults(func=cmd_customer_discovery)

    p_validate = sub.add_parser("validate", help="Phase 6: analyze real interview notes against your hypotheses and success criteria")
    p_validate.add_argument("--session", required=True, help="Session ID, or 'latest'")
    p_validate.set_defaults(func=cmd_validate)

    p_gtm = sub.add_parser("gtm", help="Phase 7: build the GTM recommendation (motion, positioning, channels, pricing, launch sequence)")
    p_gtm.add_argument("--session", required=True, help="Session ID, or 'latest'")
    p_gtm.set_defaults(func=cmd_gtm)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
