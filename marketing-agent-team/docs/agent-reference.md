# 🤖 Agent Reference Guide — v2

> 13 agents across 5 layers. Quick reference for what each agent does, when to invoke it, and what it produces.

---

## 🎯 marketing-orchestrator

| | |
|---|---|
| **Role** | Lead agent — coordinates all teams, enforces quality gates, manages revision loops |
| **Reads** | `pipeline/00-campaign-brief.md` + `pipeline/12-campaign-learnings.md` |
| **Writes** | Updates `pipeline/12-campaign-learnings.md` after each run |
| **Best for** | Full campaign runs, multi-channel campaigns, anything spanning 2+ teams |
| **Skip when** | You only need one agent — invoke the specialist directly |

---

## 🧭 Strategy Layer

### content-strategist
| | |
|---|---|
| **Role** | Decides what to create, why, for which funnel stage, in which format |
| **Reads** | `pipeline/00-campaign-brief.md`, `pipeline/12-campaign-learnings.md`, `CLAUDE.md` |
| **Writes** | `pipeline/00b-content-strategy.md` |
| **Key outputs** | Strategic recommendation, pillar/funnel alignment, content angle, distribution plan |
| **Run order** | First — before Research Team on full campaigns |
| **Skip when** | Quick single-piece runs where format is already decided |

---

## 🔍 Research Team

### market-researcher
| | |
|---|---|
| **Role** | Finds trends, competitor signals, industry data, content hook opportunities |
| **Reads** | `pipeline/00-campaign-brief.md` + web search |
| **Writes** | `pipeline/01-market-research.md` |
| **Key outputs** | Trend signals, competitor moves, key data points, hook opportunities |
| **Run order** | First in Research Team |

### audience-analyst
| | |
|---|---|
| **Role** | Maps ICP pain points, buying triggers, objections, and exact audience language |
| **Reads** | `pipeline/00-campaign-brief.md`, `pipeline/01-market-research.md` |
| **Writes** | `pipeline/02-audience-insights.md` |
| **Key outputs** | Pain hierarchy, VOC phrases, buying triggers, messaging recommendations |
| **Run order** | Second in Research Team |

### social-listener
| | |
|---|---|
| **Role** | Identifies what content formats and hooks are performing on LinkedIn now |
| **Reads** | `pipeline/00`, `01`, `02` |
| **Writes** | `pipeline/03-social-signals.md` |
| **Key outputs** | Format performance, hook patterns, topic saturation, competitor content gaps |
| **Run order** | Third in Research Team |
| **Skip when** | Email-only or blog-only campaigns |

---

## ✍️ Content Team

### linkedin-writer
| | |
|---|---|
| **Role** | Writes 2–3 LinkedIn post variants |
| **Reads** | `pipeline/00`, `01`, `02`, `03` |
| **Writes** | `pipeline/04-linkedin-draft.md` |
| **Revision mode** | Re-invoke with QA report to fix only flagged sections |
| **Run order** | After Research Team |

### email-writer
| | |
|---|---|
| **Role** | Writes email sequences (cold 1–3, nurture 3–5, re-engage 1–2) |
| **Reads** | `pipeline/00`, `01`, `02` |
| **Writes** | `pipeline/05-email-draft.md` |
| **Revision mode** | Re-invoke with QA report to fix only flagged emails/elements |
| **Run order** | After Research Team |

### blog-writer
| | |
|---|---|
| **Role** | Writes long-form SEO blog posts (1,000–2,500 words) |
| **Reads** | `pipeline/00`, `01`, `02`, `08` (if SEO ran first) |
| **Writes** | `pipeline/06-blog-draft.md` |
| **Revision mode** | Re-invoke with QA or SEO report to fix only flagged sections |
| **Run order** | After Research Team |

---

## 🧪 Quality Team

### qa-agent
| | |
|---|---|
| **Role** | Reviews grammar, clarity, structure, factual accuracy |
| **Reads** | `pipeline/04`, `05`, `06`, `02` |
| **Writes** | `pipeline/07-qa-report.md` |
| **Key outputs** | Critical/Major/Minor issue table, fix recommendations, routing instructions |
| **Run order** | First in Quality Team — always before brand-voice-checker |
| **Revision loop** | If FAIL → content agent fixes → re-run qa-agent (max 2 cycles) |

### seo-optimizer
| | |
|---|---|
| **Role** | Optimizes blog for search: keywords, meta, E-E-A-T, AI Overviews, schema |
| **Reads** | `pipeline/06`, `00`, `02` |
| **Writes** | `pipeline/08-seo-report.md` |
| **Key outputs** | Metadata recommendations, on-page fixes, featured snippet, 2025 SEO signals |
| **Run order** | After qa-agent, blog posts only |

### brand-voice-checker
| | |
|---|---|
| **Role** | Checks all content against brand voice guide, provides specific rewrites |
| **Reads** | `pipeline/04`, `05`, `06`, `docs/brand-voice-guide.md` |
| **Writes** | `pipeline/09-brand-check.md` |
| **Key outputs** | Tone scores, red flag table with rewrites, cross-channel consistency check |
| **Run order** | After qa-agent |
| **Revision loop** | If OFF-BRAND → content agent applies rewrites → re-run brand-voice-checker |

---

## 📊 Analytics + Planning

### performance-analyst
| | |
|---|---|
| **Role** | Analyzes content performance data, finds patterns, drives next-campaign strategy |
| **Reads** | `pipeline/00` + pasted performance data + `pipeline/12` |
| **Writes** | `pipeline/10-performance-report.md` |
| **Key outputs** | Scorecard vs benchmarks, top/underperformers, patterns, recommendations |
| **Run order** | Post-publish (retrospective) OR pre-campaign (inform strategy) |

### ab-test-designer
| | |
|---|---|
| **Role** | Designs structured A/B tests with hypotheses, variants, and success criteria |
| **Reads** | `pipeline/04`, `05`, `10` |
| **Writes** | `pipeline/11-ab-variants.md` |
| **Key outputs** | Test hypotheses, A/B variants, success criteria, testing roadmap |
| **Run order** | After content drafts exist; ideally after performance-analyst |

### content-calendar-planner
| | |
|---|---|
| **Role** | Builds publish-ready calendar with dates, times, dependencies, engagement actions |
| **Reads** | `pipeline/04`, `05`, `06`, `07`, `09`, `00b`, `11` |
| **Writes** | `pipeline/13-content-calendar.md` |
| **Key outputs** | Weekly schedule grid, pre-publish checklists, engagement protocol |
| **Run order** | After Quality Team sign-off — final step before publish |

---

## 🔗 Agent Flow Diagram

```
00-campaign-brief.md (YOU)
         │
         ▼
content-strategist ──────────────────────► 00b-content-strategy.md
         │                                          │
         ▼                                          │ (informs)
market-researcher ──► 01-market-research.md         │
         │                                          │
audience-analyst ──── 02-audience-insights.md ◄─────┘
         │
social-listener ───── 03-social-signals.md
         │
    ┌────┴──────────────┐
    ▼                   ▼                    ▼
linkedin-writer    email-writer         blog-writer
    │                   │                    │
    ▼                   ▼                    ▼
   04                  05                   06
    └───────────────────┴────────────────────┘
                        │
              ┌─────────┼──────────┐
              ▼         ▼          ▼
          qa-agent  seo-optim.  brand-voice
              │         │          │
              ▼         ▼          ▼
             07        08         09
              │
    ┌─────────┤ [FAIL? → back to content agents]
    │         │
    ▼         ▼
perf-analyst  ab-designer
    │              │
    ▼              ▼
   10             11
                   │
                   ▼
        content-calendar-planner ──► 13
                   │
                   ▼
        Orchestrator updates ──────► 12-campaign-learnings.md
```
