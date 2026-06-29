# TakeMeter — r/soccer Discourse Classifier

**AI201 · Project 3**

A fine-tuned DistilBERT classifier that labels r/soccer Reddit posts by discourse type: structured analysis, bold hot takes, or emotional reactions. This README is the complete evaluation report.

---

## Community

**r/soccer** is one of the largest sports communities on Reddit. Discourse quality varies enormously within the same thread — a post-match discussion can contain rigorous tactical breakdowns, pure emotional reactions, and confident assertions with no supporting evidence, often within a few replies of each other.

This variation makes r/soccer a strong classification target: the distinctions are real, they are frequent enough to produce 200+ labeled examples without scraping obscure content, and the community itself uses terms like "hot take" and "tactical analysis" conversationally — meaning the labels are grounded in how members already think about discourse quality.

---

## Label Taxonomy

Three labels, mutually exclusive:

**`analysis`** — A post that makes a structured argument supported by specific, verifiable evidence — statistics, tactical observations, historical comparisons, or formation breakdowns — where the evidence is doing genuine reasoning work toward the conclusion.

- Example 1: *"City's high press against Real wasn't working because Valverde was dropping into the half-space and bypassing the press trigger — Rodri had to cover too much ground, which is why you saw so many gaps in the 6-8 channel in the second half."*
- Example 2: *"Mbappé's xG last season was 28.4 but he scored 22 — his conversion rate has been below average two seasons running. People acting surprised by the drought aren't paying attention."*

**`hot_take`** — A bold, confident opinion stated without meaningful supporting evidence. The author asserts a verdict — sometimes provocative, sometimes contrarian — but does not reason through it.

- Example 1: *"Messi is done. He's been coasting on reputation for two years and everyone's too scared to say it."*
- Example 2: *"Premier League football is genuinely more entertaining to watch than La Liga and it's not close. The pace, the intensity — there's no comparison."*

**`reaction`** — An immediate emotional response to a specific moment, result, or event. Little to no argument — the post is expressing a feeling in real time, tied to something that just happened.

- Example 1: *"WHAT. A. GOAL. I don't even support Arsenal but that was absolutely filthy."*
- Example 2: *"Can't believe we just dropped two points to a ten-man side. Absolutely gutted. Season feels over."*

---

## Data Collection

**Source:** r/soccer (Reddit) — public posts and comments only  
**Collection method:** Manual — posts representative of each label type were gathered from post-match discussion threads, unpopular opinion threads, match live threads, and goal clip comment sections. An LLM (Claude) was used to generate additional examples grounded in authentic r/soccer style and voice, which were then reviewed and labeled manually. All AI-assisted examples were reviewed for label correctness before inclusion. See the AI Usage section for details.

**Total examples:** 212  
**File:** `soccer_takes.csv` (columns: `text`, `label`, `notes`)

**Label distribution:**

| Label | Count | % |
|---|---|---|
| `reaction` | 80 | 37.7% |
| `hot_take` | 67 | 31.6% |
| `analysis` | 65 | 30.7% |

**Train / Validation / Test split (70% / 15% / 15%, stratified):**

| Split | Total | analysis | hot_take | reaction |
|---|---|---|---|---|
| Train | 148 | 45 | 47 | 56 |
| Validation | 32 | 10 | 10 | 12 |
| Test | 32 | 10 | 10 | 12 |

---

## Difficult-to-Label Examples

**1. Single stat + bold verdict**
> *"Rashford has zero goals in his last 12 starts. Sell him."*

Could be `analysis` (cites a number) or `hot_take` (confident verdict). Decided **`hot_take`**: the stat is ammunition for a conclusion already reached, not a reasoned argument. Removing the stat leaves the claim intact — the evidence isn't doing genuine reasoning work.

**2. Tactical observation with expected-outcome framing**
> *"Kane's movement in behind the City defensive line was exactly what we expected and they still couldn't stop it."*

Could be `reaction` (post-match feeling) or `analysis` (names a specific tactic). Decided **`analysis`**: it identifies a specific tactical mechanism with enough precision to constitute structured observation, even if the framing is after-the-fact.

**3. Emotional reaction with embedded managerial verdict**
> *"Just seen the lineup. We're playing a 4-5-1 away to bottom of the table. What is this manager thinking."*

Could be `hot_take` (managerial critique) or `reaction` (real-time frustration). Decided **`reaction`**: the emotion is the primary content. The formation reference is an expression of frustration tied to a specific just-seen event, not a structured critique.

---

## Fine-Tuning Approach

**Base model:** `distilbert-base-uncased` (HuggingFace)  
**Training framework:** HuggingFace `Trainer` on Google Colab T4 GPU  
**Training time:** ~5 minutes

**Hyperparameters (defaults kept):**
- Epochs: 3
- Learning rate: 2e-5
- Batch size: 16 (train), 32 (eval)
- Weight decay: 0.01
- Warmup steps: 50

**Key hyperparameter decision:** Kept `num_train_epochs=3` rather than increasing to 5. With only 148 training examples, more epochs risk overfitting — the model memorizes training examples rather than learning generalizable boundaries. The validation accuracy after epoch 3 was used as the stopping criterion via `load_best_model_at_end=True`.

---

## Baseline

**Model:** Groq `llama-3.3-70b-versatile` (zero-shot)  
**Prompt approach:** System prompt included all three label definitions (copied from `planning.md`), one example post per label, the decision rule for borderline cases, and an instruction to output only the label name.

The prompt specified mutual exclusivity, provided clear one-sentence definitions, and included the `hot_take` vs. `analysis` decision rule explicitly. The model output clean label names for all 32 test examples (0 unparseable responses).

---

## Evaluation Report

### Overall Accuracy

| Model | Accuracy |
|---|---|
| Zero-shot baseline (Groq llama-3.3-70b-versatile) | **96.9%** |
| Fine-tuned DistilBERT | **62.5%** |
| Delta | −34.4 pp (fine-tuning regression) |

### Per-Class Metrics — Fine-Tuned Model

| Label | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| `analysis` | 0.45 | 1.00 | 0.62 | 10 |
| `hot_take` | 0.00 | 0.00 | 0.00 | 10 |
| `reaction` | 1.00 | 0.83 | 0.91 | 12 |
| **macro avg** | 0.48 | 0.61 | 0.51 | 32 |

### Per-Class Metrics — Baseline (Groq)

| Label | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| `analysis` | 1.00 | 0.90 | 0.95 | 10 |
| `hot_take` | 0.91 | 1.00 | 0.95 | 10 |
| `reaction` | 1.00 | 1.00 | 1.00 | 12 |
| **macro avg** | 0.97 | 0.97 | 0.97 | 32 |

### Confusion Matrix — Fine-Tuned Model (Test Set)

Rows = true label, columns = predicted label.

|  | pred: analysis | pred: hot_take | pred: reaction |
|---|---|---|---|
| **true: analysis** | 10 | 0 | 0 |
| **true: hot_take** | 10 | 0 | 0 |
| **true: reaction** | 2 | 0 | 10 |

The dominant pattern is immediately clear: the model predicted `analysis` for every single `hot_take` example in the test set (10/10), and also for 2 `reaction` examples. It never predicted `hot_take` once.

---

## Wrong Predictions — Analysis

12 of 32 test examples were wrong. All 12 were predicted as `analysis` when the true label was either `hot_take` (10 cases) or `reaction` (2 cases).

**Error #1 — hot_take → analysis**
> *"Rashford has zero goals in his last 12 starts. Sell him."*  
> True: `hot_take` | Predicted: `analysis` (confidence: 0.39)

**Why it failed:** This is the canonical borderline case. The sentence structure is declarative and fact-citing — exactly the surface pattern the model associated with `analysis` during training. DistilBERT learned that posts containing stats or precise references belong to `analysis`, without learning the deeper distinction that the stat here is verdict-support rather than reasoned argument. The model is pattern-matching on surface form, not logical structure.

**Error #2 — hot_take → analysis**
> *"The Bundesliga's 50+1 ownership rule is the only thing keeping German football authentic. The Premier League sold its soul."*  
> True: `hot_take` | Predicted: `analysis` (confidence: 0.35)

**Why it failed:** This post references a real rule (50+1) and makes a structural claim about football governance — both surface signals the model learned to associate with `analysis`. But there's no actual reasoning: it asserts a verdict without evidence. The model doesn't distinguish between "mentions a real thing" and "reasons from a real thing."

**Error #3 — reaction → analysis**
> *"That red card was the most ridiculous decision I've seen all season. Completely changed the game."*  
> True: `reaction` | Predicted: `analysis` (confidence: 0.35)

**Why it failed:** This post doesn't contain emotional language strong enough (no caps, no exclamation marks) for the model to recognize it as `reaction`. It reads like a calm judgment, and the model interpreted "completely changed the game" as a causal observation — the type of claim that appears in `analysis` posts. The `reaction` label was apparently learned primarily through strong affective markers, and this example lacks them.

---

## Sample Classifications

Fine-tuned model predictions on 5 examples with confidence scores:

| Post (truncated) | True Label | Predicted | Confidence |
|---|---|---|---|
| *"Bellingham's positioning is elite. He makes runs that time perfectly..."* | analysis | analysis | 0.71 |
| *"WHAT A GOAL. I don't even support Arsenal but that was absolutely filthy."* | reaction | reaction | 0.97 |
| *"Messi is done. He's been coasting on reputation for two years..."* | hot_take | analysis | 0.36 |
| *"I can't believe we just dropped two points to a ten-man side. Absolutely gutted."* | reaction | reaction | 0.95 |
| *"Klopp leaving Liverpool is the best thing that could have happened to them."* | hot_take | analysis | 0.38 |

**Correct prediction explained:** The Bellingham post (analysis → analysis, 0.71 confidence) is correctly classified because it contains specific, verifiable claims about player movement and timing that are grounded in observable tactical behavior. The model learned this pattern reliably. The confidence of 0.71 is moderate — reflecting that the language isn't dramatically different from some hot_take posts — but correct.

---

## Reflection: What the Model Learned vs. What I Intended

I intended the model to learn a semantic distinction: whether a post *reasons* toward its conclusion or merely *asserts* it. That is a logical-structural distinction.

What the model actually learned was a surface-form distinction: posts with longer, more complex sentences, tactical vocabulary (formations, player names, statistical references), or structured grammar patterns → `analysis`. Posts with all-caps, exclamation marks, or explicit emotional words → `reaction`. Everything else → `analysis` by default.

The `hot_take` label was the casualty. `hot_take` posts are structurally similar to `analysis` posts — both are declarative, both reference real players or rules, both sound like someone who knows football. The difference is in the logical relationship between the claim and the evidence, which is not visible in surface tokens. DistilBERT, fine-tuned on 47 `hot_take` training examples, never learned this boundary. With more training examples and possibly a longer model (BERT-base or RoBERTa), the model might have extracted deeper contextual cues — but 47 examples of a subtly-defined label is not enough.

The baseline (Groq llama-3.3-70b-versatile) did learn this distinction because it was given the decision rule explicitly in the prompt and has sufficient prior knowledge of argumentation structure to apply it. That is not a fair comparison in terms of training — the LLM has seen billions of examples of logical vs. assertive writing. But it is the honest baseline: a capable general model with a good prompt outperforms a small specialized model on a task where the label distinction is semantic rather than surface-level.

---

## Spec Reflection

**One way the spec helped:** The requirement to identify a hard edge case before annotating forced me to write the `analysis` vs. `hot_take` decision rule early. That rule — "if you could remove the evidence and the claim still stands, it's `hot_take`" — became the clearest guidance I had during annotation and was later confirmed as exactly the boundary the model couldn't learn.

**One way implementation diverged:** The spec assumes fine-tuning will outperform the zero-shot baseline, and the success criteria in my `planning.md` (≥0.70 accuracy, ≥10pp improvement over baseline) were written with that assumption. The result inverted: the baseline (96.9%) dramatically outperformed the fine-tuned model (62.5%). This revealed that the task is hard for the *wrong reasons* — not because the labels are ambiguous to humans, but because the label distinction is below the surface-token level that a small fine-tuned model can reliably detect. The spec's framing of "fine-tuning should help" is correct in general but depends on whether the label signal is learnable from surface form.

---

## AI Usage

**1. Dataset generation (annotation assistance)**  
I directed Claude to generate r/soccer-style posts that authentically represent each label type, providing it with the full label definitions and decision rules from `planning.md`. Claude produced draft examples; I reviewed every example, corrected labels where needed, and removed any that didn't meet the definition. The AI generated the initial text; the labeling judgment and quality review were mine. This is disclosed as the primary data collection method.

**2. Failure pattern analysis**  
After seeing the wrong predictions from Section 4, I asked Claude to identify common patterns across the 12 misclassified examples. Claude identified that 10/12 errors were `hot_take` → `analysis` confusions and hypothesized that the model was pattern-matching on surface-level formality rather than reasoning structure. I verified this by re-reading all 12 wrong predictions myself and confirmed the pattern held: every misclassified `hot_take` contained language that sounded substantive (references to rules, players, or statistics) without actually constructing a reasoned argument. The pattern held; I included it in the evaluation.

---

## How to Run

The fine-tuning pipeline runs in Google Colab (T4 GPU required):

1. Open `takemeter.ipynb` in Google Colab
2. Set runtime to T4 GPU (Runtime → Change runtime type → T4 GPU)
3. Run all cells in order
4. Upload `soccer_takes.csv` when Section 1 prompts
5. Add your `GROQ_API_KEY` via Colab Secrets before running Section 5
6. Download `evaluation_results.json` and `confusion_matrix.png` from the Files panel after Section 6
