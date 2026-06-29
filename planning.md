# TakeMeter — Planning Document
**Project:** AI201 Project 3  
**Community:** r/soccer  
**Author:** Mamadou Ba

---

## 1. Community

**Chosen community:** r/soccer (Reddit)

r/soccer is one of the largest sports communities on Reddit, with millions of members discussing matches, transfers, tactics, and player performance across all major leagues. The discourse is notably varied in quality — the same match thread can contain rigorous tactical breakdowns, pure emotional reactions, and confident assertions stated with no supporting evidence. That range of quality is exactly what makes it a strong fit for a classification task: the distinctions are real, they matter to regular participants, and they are frequent enough to produce 200+ labeled examples without scraping obscure content.

The community itself uses terms like "hot take" and "tactical analysis" conversationally, which signals that these distinctions are meaningful to members — not just imposed from outside.

---

## 2. Label Taxonomy

### Labels (3 total)

**`analysis`**  
A post that makes a structured argument supported by specific, verifiable evidence — statistics, tactical observations, historical comparisons, or positional/formation breakdowns — where the evidence is doing genuine reasoning work toward the conclusion.

- Example 1: "City's high press against Real wasn't working because Valverde was dropping into the half-space and bypassing the press trigger — Rodri had to cover too much ground, which is why you saw so many gaps in the 6–8 channel in the second half."
- Example 2: "Mbappé's xG last season was 28.4 but he scored 22 — his conversion rate has been below average two seasons running. People acting surprised by the drought aren't paying attention."

---

**`hot_take`**  
A bold, confident opinion stated without meaningful supporting evidence. The author asserts a verdict — sometimes provocative, sometimes contrarian — but doesn't reason through it. The framing is declarative, not investigative.

- Example 1: "Messi is done. He's been coasting on reputation for two years and everyone's too scared to say it."
- Example 2: "Premier League football is genuinely more entertaining than La Liga and it's not close. The pace, the intensity — there's no comparison."

---

**`reaction`**  
An immediate emotional response to a specific moment, result, or event. Little to no argument — the post is expressing a feeling in real time, tied to something that just happened.

- Example 1: "WHAT. A. GOAL. I don't even support Arsenal but that was absolutely filthy."
- Example 2: "Can't believe we just dropped two points to a ten-man side. Absolutely gutted. Season feels over."

---

### Mutual Exclusivity Check

A post belongs to exactly one label:
- If it argues with evidence → `analysis`
- If it asserts a verdict without evidence → `hot_take`
- If it expresses a feeling about a specific just-happened moment → `reaction`

Posts that mix mild emotion with argument default to whichever is structurally dominant — if the argument is the point, it's `analysis`; if the emotion is the point, it's `reaction`.

---

## 3. Hard Edge Cases

### Primary edge case: single-stat + verdict posts

**Example post:** "Rashford has zero goals in his last 12 starts. Sell him."

This sits between `hot_take` (confident verdict, sell-him framing) and `analysis` (cites a specific number).

**Decision rule:** If the evidence genuinely *reasons toward* the conclusion — meaning you couldn't remove it without the argument collapsing — label it `analysis`. If the stat is there to *sound credible* but the post is fundamentally asserting a conclusion already reached, label it `hot_take`. A single cherry-picked stat bolted onto a verdict is `hot_take`. A stat situated within a pattern, compared against a benchmark, or used to build a case is `analysis`.

- "Rashford has zero goals in 12 starts. Sell him." → **`hot_take`** (stat is ammunition, not argument)
- "Rashford has zero goals in 12 starts — worse than any United striker since Sheringham in 2001. His xG in that stretch is 4.2, so he's not even getting into positions. It's a system issue, not finishing." → **`analysis`** (evidence builds a case, reaches a nuanced conclusion)

### Secondary edge case: emotional reaction with one opinion attached

**Example post:** "What a horrible game. Honestly Tuchel should be sacked."

Is this `reaction` (emotional response to the match) or `hot_take` (managerial opinion)?

**Decision rule:** If the opinion is embedded inside the emotional reaction and the post is primarily about the feeling, label it `reaction`. If the opinion is the main point and the emotion is context, label it `hot_take`. The above example is `reaction` — the sacking opinion is a venting add-on, not the argument.

---

## 4. Data Collection Plan

**Source:** r/soccer on Reddit (public posts and comments)  
**Method:** Manual collection — reading post threads and copy-pasting into a CSV spreadsheet. No scraping tool needed for 200 examples.

**Target distribution:**
| Label | Target count | % |
|---|---|---|
| `analysis` | 70 | 35% |
| `hot_take` | 70 | 35% |
| `reaction` | 60 | 30% |

Aim for no label above 40% of the total dataset.

**Where to find each label:**
- `analysis`: Post-match discussion threads (typically 2–6 hours after a game), dedicated "tactical breakdown" posts, transfer debate threads
- `hot_take`: Weekly discussion threads, "unpopular opinion" posts, transfer rumor comment sections
- `reaction`: Live match threads, goal clip comment sections, breaking news comment sections

**If a label is underrepresented after 150 examples:** Deliberately seek posts of that type — e.g., go to a specific post-match tactical thread for more `analysis` examples, or a goal clip comment section for more `reaction` examples.

**CSV format:**
```
text, label, notes
```
The `notes` column will flag difficult cases for the hard-cases section.

---

## 5. Evaluation Metrics

**Primary metrics:**
- **Overall accuracy** — gives the headline number for comparing baseline vs. fine-tuned model, but alone it can mask class-level failure
- **Per-class F1** — the most important single number per label; it balances precision and recall and surfaces whether the model can distinguish each individual label, not just the easy majority
- **Confusion matrix** — shows *which* labels the model confuses and in which direction (e.g., does it predict `hot_take` when the true label is `analysis`?), which is more actionable than any aggregate number

**Why accuracy alone isn't enough:** If the dataset is 40/35/25 split, a model predicting the majority class every time would achieve 40% accuracy without learning anything. Per-class F1 catches this; accuracy doesn't. The confusion matrix reveals whether errors are symmetric or directional, which informs what to fix.

**Why these metrics fit this task specifically:** The `analysis`/`hot_take` boundary is the hardest — a model that can't distinguish them would show up as a large off-diagonal cell in the confusion matrix at that pair. Per-class metrics will reveal if one label is getting ignored entirely. These three metrics together give a complete picture.

---

## 6. Definition of Success

**Minimum acceptable (worth deploying):**
- Fine-tuned model overall accuracy ≥ 0.70
- Per-class F1 ≥ 0.60 for all three labels (no label completely ignored)
- Fine-tuned model outperforms zero-shot baseline by at least 10 percentage points overall

**Good outcome:**
- Overall accuracy ≥ 0.78
- Per-class F1 ≥ 0.70 for all labels
- Confusion matrix shows no single off-diagonal cell with more than 30% of a class's examples

**The `analysis`/`hot_take` boundary is the key test.** If the model can reliably distinguish those two labels, the taxonomy is working. If it can't, either the labels need tightening or the training data is inconsistent at that boundary.

A classifier that hits the "minimum acceptable" bar would be genuinely useful as a moderation aid or content-quality signal in a community tool — not as a ground truth, but as a first-pass filter.

---

## 7. AI Tool Plan

### Label stress-testing
Before annotating 200 examples, I will give Claude my three label definitions and edge case description and ask it to generate 10 posts that sit at the boundary between `analysis` and `hot_take` — the hardest pair. If it produces posts I can't classify cleanly under my current definitions, I'll tighten the decision rule before committing to annotation.

### Annotation assistance
I will use an LLM (Claude) to pre-label batches of 20–30 examples at a time by providing it with my label definitions and unlabeled posts, then review and correct every pre-assigned label myself. I will not skim — I will read each post and override any label that doesn't match my definition. Pre-labeled examples that I override will be flagged in the `notes` column of the CSV. This will be disclosed in the AI usage section of the README.

### Failure analysis
After fine-tuning, I will paste the full list of wrong predictions into Claude and ask it to identify common patterns — e.g., "do most errors involve short posts?", "is there a specific label pair that accounts for most confusion?", "does sarcasm appear frequently in misclassified examples?" I will then verify each claimed pattern by re-reading the examples myself before including findings in the evaluation report.

---

## Hard Annotation Decisions (updated during Milestone 3)

### Case 1: Single stat + bold verdict
**Post:** "Rashford has zero goals in his last 12 starts. Sell him."  
**Ambiguity:** Could be `analysis` (cites a specific number) or `hot_take` (confident verdict with minimal reasoning).  
**Decision:** `hot_take` — the stat is ammunition for a conclusion already reached, not a reasoned argument. The post doesn't situate the stat in context, compare it to a baseline, or reason toward a nuanced conclusion. Applying the decision rule: removing the stat leaves the claim intact ("Sell him") which means the evidence isn't doing genuine reasoning work.

### Case 2: Tactical observation + expected outcome framing
**Post:** "Kane's movement in behind the City defensive line was exactly what we expected and they still couldn't stop it."  
**Ambiguity:** Names a specific tactical mechanism (`movement in behind`) which pulls toward `analysis`, but the framing ("exactly what we expected") implies no new reasoning is being offered — it's more of a validated observation than a built argument.  
**Decision:** `analysis` — even though the framing is observational rather than argumentative, the post identifies a specific tactical mechanism (runs in behind vs. a named defensive system) with enough precision to constitute structured observation. Borderline, but the tactical specificity tips it over.

### Case 3: Emotional reaction with an embedded managerial verdict
**Post:** "Just seen the lineup. We're playing a 4-5-1 away to bottom of the table. What is this manager thinking."  
**Ambiguity:** The formation reference could push toward `hot_take` (bold opinion on the manager's decision) but the framing is reactive — the user just saw the lineup and is expressing frustration in real time.  
**Decision:** `reaction` — the emotion is the primary content. The formation reference is an expression of frustration not a structured critique of tactical choice. Applying the decision rule: the opinion ("what is this manager thinking") is embedded inside a real-time emotional response and isn't the main point.

---

## Evaluation Results Summary (added after Milestone 5)

- Fine-tuned DistilBERT accuracy: 62.5%
- Baseline (Groq llama-3.3-70b-versatile) accuracy: 96.9%
- Fine-tuning was a regression of 34.4pp — baseline dramatically outperformed
- Root cause: `hot_take` F1 = 0.00 — model collapsed all hot_take predictions into `analysis`
- `reaction` F1 = 0.91 (learned well), `analysis` F1 = 0.62 (recall perfect but precision low due to hot_take bleed)
- The label distinction between `hot_take` and `analysis` is semantic (logical structure), not surface-level — below what DistilBERT could learn from 47 training examples

---

## Stretch Features (updated if attempted)

*(This section will be updated before starting any stretch feature.)*
