---

## Abstract

A *world model* is an internal predictor over environment dynamics, used to imagine the consequences of actions. In coding, the environment is the program: its runtime state, execution trace, filesystem, tests, and developer task. Zaremba and Sutskever [@arxiv1410_4615] trained an LSTM to predict Python execution output in 2014. Meta FAIR released CWM [@arxiv2510_02387], the first open-weights LLM branded a Code World Model, in October 2025. Internal models of execution can be learned. Whether they are necessary, architecturally separable, or causally responsible for coding-agent gains remains unestablished.

This survey synthesizes 184 papers spanning four research lineages: neural execution, trace pretraining and the CWM line, agentic software engineering with execution feedback, and verifier-grounded code generation. It traces the twelve-year arc, builds a three-axis taxonomy (functionality, temporal, representation), produces system cards for thirteen representative systems, assembles protocol-stratified tables for SWE-bench, CRUXEval, web agents, and formal verification, develops seven critical theses, and lists open problems. The empirical evidence supports execution-grounded supervision as a reliable lever for code-agent gains on runtime-reasoning benchmarks. Open questions concern which architectural commitments — token-space prediction, latent dynamics, or synthesized simulators — best capture program semantics.

---

## Theses Summary

The seven critical theses developed in §17, each grounded in a specific disconfirmation from the corpus:

1. **The architectural design space for code WMs has three concrete forms.** Forward state prediction admits a clean tripartition (§3.1): neural dynamics models in compressed latent space (N1, no code exemplar yet), latent-action models such as CoLA (N2), and synthesized executable simulators such as GIF-MCTS and ARC executable WMs (N3). Most "Code World Model" systems today (CWM, TRACED, SemCoder, NExT) extend the LLM training distribution without committing to any of these three forms; whether the architectural commitment pays off remains the central open empirical question.

2. **Trace pretraining has a causal-isolation problem.** The ablation study Do Code Semantics Help? [@arxiv2509_11686] finds no trace representation consistently improves code synthesis across multiple backbones. CWM's 65.8% SWE-bench Verified result confounds trace mid-training, ForagerAgent trajectories, and RL.

3. **The Dreamer-for-code gap may be a non-problem.** Vision required latent rollouts because pixels are expensive. Python state is small and CPython is free, so the architectural pressure does not transfer. CWM in token space reaches 65.8% on SWE-bench Verified at 32B parameters.

4. **PRMs and forward WMs solve complementary problems.** Process reward models score partial trajectories; forward WMs predict next states. The design space for combining them — a PRM critic over rollouts from a forward predictor — is largely unexplored in code, despite being standard in model-based RL.

5. **General Agents Contain World Models [@arxiv2506_01622] is weaker than its title.** The theorem applies under restrictive assumptions (full observability, stationarity, deep-composite-goal regret bounds) that SWE agents demonstrably violate.

6. **The verifier-grounded lineage leads on a narrow scope.** ATLAS, Re:Form, CLEVER, VeriStruct, and AutoRocq produce machine-checkable correctness. They lead on synthesis-from-spec (e.g., ATLAS DafnySynthesis 65.8% pass@5); they do *not* lead on end-to-end verified codegen from natural language (CLEVER ≤1/161 Lean).

7. **The evaluation gap is structural.** No benchmark holds policy fixed and varies WM quality. Models with 85–98% output-prediction accuracy still produce traces with systematic errors throughout. Outcome accuracy decouples from process fidelity.

---

## 1. Introduction

Autoregressive code LLMs generate tokens conditioned on syntactic context. Correct programs are objects in two domains: source tokens, and the values, control flow, side effects, and developer intent those tokens encode. The world-model framing comes from model-based reinforcement learning, where it names an internal predictor of environment dynamics. The hypothesis examined here: training on execution rather than only on source-token prediction reduces the gap between code that compiles and code that runs.

Two adjacent surveys cover non-overlapping ground. A Survey on LLMs for Code Generation [@arxiv2406_00515] maps the code-LLM space without the world-model lens. Understanding World or Predicting Future [@arxiv2411_14499] maps world models in general without the code lens. A Comprehensive Survey on World Models for Embodied AI [@arxiv2510_16732] maps embodied world models but excludes the coding domain. The intersection, the subject of this document, has cohered only recently into a recognizable program.

---

## 2. Methodology

The corpus contains 184 arxiv preprints, assembled in four passes (March–May 2026) seeded from CWM [@arxiv2510_02387] via citation BFS and targeted topic searches. A paper enters the corpus if it intersects both world-model or state-tracking architectures and code generation, debugging, repair, or agentic coding. Pure vision world models (DreamerV1–V3, V-JEPA, Genie) and pure code-LLM papers without a world-model angle are excluded except as cited precedent. Date cutoff: 2026-05-15. One curator performed the taxonomy coding. Numerical claims in §§6–14 derive from abstracts, §16 from source PDFs. 60% of the corpus dates from 2025 or later.

---

## 3. Defining a World Model for Coding

The literature uses *world model* in two distinct senses, which this survey separates.

### 3.1 Two definitions

**Definition D (descriptive, permissive).** A *world model for coding* is any code LLM whose training objective concretely encodes program semantics — execution traces, runtime state, environment feedback, or simulated outcomes — in addition to or instead of source-token prediction. This matches the field's current usage. Under D, CWM, TRACED, SemCoder, LLM-JEPA, DyMo, RLEF, and most papers in the corpus qualify as world models.

**Definition N (normative, strict).** A *world model for coding* is a system with an explicit, separable forward-prediction mechanism. N splits into three sub-types:

- **N1 — Neural dynamics model.** A learned `W : (state, action) → next_state` instantiated as a distinct architectural component with latent recurrent state, separate dynamics head, or inverse model. Dreamer-class. No code exemplar in the corpus.
- **N2 — Latent-action model.** A learned action abstraction over a base LLM, with the LLM serving as transition model in compressed action space, supporting rollout or tree search over latent actions. CoLA [@arxiv2503_21383] provides the canonical example.
- **N3 — Synthesized executable simulator.** The world model is an executable program (Python, DSL) synthesized by an LLM and run against ground-truth transitions during planning. GIF-MCTS [@arxiv2405_15383], WorldCoder, Executable WMs for ARC-AGI-3 [@arxiv2605_05138].

Each N-subtype carries a distinct architectural commitment. N1 commits to learned latent dynamics; N2 commits to a discrete latent-action space; N3 commits to program synthesis as the dynamics. Conflating them, as the loose Dreamer-for-LLMs framing did, obscures which architectural bet a system makes. Under any N-subtype, CWM, TRACED, SemCoder, and most of the corpus do *not* qualify.

The two definitions agree on the empirical fact that execution-grounded supervision helps. They disagree on whether that grounding warrants the name *world model* in the model-based-RL sense.

| Aspect | Definition D (descriptive) | Definition N (normative) |
|---|---|---|
| Granted to | Any LLM trained with execution-related signal | Only systems with explicit forward-prediction module |
| Includes CWM | Yes | No (architecturally a Llama-class decoder) |
| Includes TRACED, SemCoder, NExT | Yes | No (auxiliary heads on a Transformer) |
| Includes CoLA, GIF-MCTS | Yes | Yes |
| Includes PRMs (ExecVerify, ThinkPRM) | Often grouped | No (critics, not forward predictors) |
| Includes verifiers (Lean, Dafny, Z3) | Sometimes grouped | No (deterministic oracles, not learned WMs) |
| Includes Dreamer / V-JEPA (vision precedents) | Yes | Yes |

This survey uses **D throughout the catalog sections (§§6–16)** because that reflects how the literature talks, and **N in §17** because the critical synthesis depends on it. The switch is marked each time it matters. The two-definition framework resolves the tension between field usage and architectural precision.

### 3.2 What is modeled

Orthogonal to D-vs-N, *what* a system models varies: variable values and stack frames (CWM, CodeExecutor); execution traces (NExT, SemCoder, TRACED); test outcomes (LEVER, RLEF); OS or web environment state (WebDreamer, Dyna-Think); repository state (RepoGraph); spec or developer intent (ATLAS, Re:Form); adversarial behavior (Double Life of CWMs). A system typically commits strongly to one or two of these.

CWM occupies an instructive position: behaviorally explicit (it emits stack frames) but architecturally implicit (a 32B Llama-class decoder with no separate dynamics head). SemCoder, NExT, and TRACED follow the same pattern. The explicit-WM label flattens this distinction; §17.1 develops the consequence.

---

## 4. Twelve Years of Code World Models

The lineage reads as a sequence of inheriting questions. Each era's answer dissolved the previous era's bottleneck and exposed the next.

(See Figure 1 at the start of the paper for the timeline diagram.)

Diamond markers in the figure tag the moments where *world model* enters the name of the contribution.

**Pre-2020: can a network execute code?** Learning to Execute [@arxiv1410_4615] trained an LSTM to predict Python output on bounded-loop programs. Neural Programmer-Interpreters [@arxiv1511_06279] and Differentiable Forth built differentiable program counters. Dynamic Neural Program Embedding [@arxiv1711_07163] embedded real interpreter traces. Neural Code Fusion [@arxiv1906_07181] and IPA-GNN [@arxiv2010_12621] used GNN attention as a program counter. By 2020 the answer was yes, but only with the interpreter encoded into architecture, which did not scale to real languages. Ha & Schmidhuber [@arxiv1803_10122] had named the pattern for vision-RL; the coding community had not yet borrowed it.

**2020–2022: can the training include execution?** Codex [@arxiv2107_03374] and MBPP [@arxiv2108_07732] made code generation a target. Scratchpads [@arxiv2112_00114] showed a Transformer could predict program output when allowed to emit intermediate computation first, the Dynamic-NPE move at LLM scale, without architectural surgery.

**2023: trace pretraining as a named recipe.** CodeExecutor [@arxiv2305_05383] trained a Transformer to emit per-line state traces from source. TRACED [@arxiv2306_07487] generalized this to a pretraining auxiliary. CRUXEval [@arxiv2401_03065] provided the eval that became standard. In parallel, Reflexion [@arxiv2303_11366] and Self-Debug [@arxiv2304_05128] used execution feedback in-context, LEVER [@arxiv2302_08468] used it during decoding, and RAP [@arxiv2305_14992] ran MCTS over an LLM-as-world-model.

**2024: from models that simulate to agents that act.** SWE-bench [@arxiv2310_06770] shifted the task to real GitHub repos. CodeAct [@arxiv2402_01030], SWE-agent [@arxiv2405_15793], NExT [@arxiv2404_14662], RLEF [@arxiv2410_02089], WebDreamer [@arxiv2411_06559], and Generating Code World Models via MCTS ([@arxiv2405_15383], source of the name) define the agentic turn. The WM moved from weights to loop.

**2025: the CWM artifact.** DeepSeek-R1 [@arxiv2501_12948] and SWE-RL [@arxiv2502_18449] scaled reasoning-RL. CoLA [@arxiv2503_21383] and LLM-JEPA [@arxiv2509_14252] ported Dreamer- and JEPA-style ideas to LLMs. General Agents Contain World Models [@arxiv2506_01622] provided the existence theorem. CWM [@arxiv2510_02387], 32B open-weights, mid-trained on 5T tokens of Python traces plus 3M ForagerAgent trajectories, made the artifact downloadable.

**2026: stress-testing and broadening.** Debugging CWMs [@arxiv2602_07672] and Demystifying Errors in LLM Reasoning Traces [@arxiv2512_00215] catalog failures. Industrial CWM [@arxiv2604_03144], Parallel-Code WMs [@arxiv2604_20926], and Executable WMs for ARC-AGI-3 [@arxiv2605_05138] generalize the recipe. Reinforcement World Model Learning [@arxiv2602_05842] trains the WM rather than the policy.


---

## 5. Taxonomy: Three Axes of Code World Models

Two cuts at the taxonomy prove useful, and they complement each other. The first, a *lineage* cut, asks which research thread produced the system, and structures §§6–13. The second, more durable cut adapts the three-axis framework of Li et al. [@arxiv2510_16732] to the code domain. The lineage map follows; the three axes appear in §§5.1–5.3.

![Representation taxonomy of code world models. Each row is one representation class (left), its vision precedent (centre), and the code-WM systems that instantiate it (right). Three classes — Global Latent Vector (Dreamer-style), Spatial/Structural Grid, and Decomposed Object/Slot — have no code exemplar in the corpus and are the survey's white-space gaps.](fig_taxonomy.pdf)

Adjacent WM surveys converge on overlapping splits that the three-axis framework subsumes as projections. Ding et al. [@arxiv2411_14499] split top-level by *implicit representation* vs *future prediction*. JiahuaDong's awesome-list organizes by *paradigm*: RL-based, observation-generative, latent-space, object-centric. knightnemo's list surfaces *pixel vs mesh vs latent* as cross-cutting tags. The three axes — functionality, temporal modeling, and representation — capture the choices a system makes regardless of which lineage it belongs to.

### 5.1 Axis 1 — Functionality

- **Decision-coupled WMs** model only the slice of the world relevant to acting on it. CWM [@arxiv2510_02387], RLEF [@arxiv2410_02089], and WebDreamer [@arxiv2411_06559] are decision-coupled. Their WMs exist to enable code generation, RL planning, or web navigation respectively. CWM does not predict global filesystem state; it predicts the next Python frame because the next action depends on it.
- **General-purpose WMs** model the environment without reference to a particular task. The general-agents-contain-world-models theorem [@arxiv2506_01622] provides the abstract limit. In the corpus, only the largest CWM-class models with broad mid-training approach generality; most code world models are decision-coupled to a sub-task (repair, completion, agent control).

### 5.2 Axis 2 — Temporal Modeling

- **Sequential simulation/inference.** Step-by-step autoregressive rollout. CWM, NExT, SemCoder, all the trace-pretraining systems, and most LLM-as-WM planners (RAP, WebDreamer in its MPC loop) live here. The state updates one timestep at a time. The vision analog is RSSM (Hafner et al., DreamerV1–V3).
- **Global difference prediction.** Predict the entire future state at once, in parallel. The vision analog is video-diffusion or masked-JEPA. In code, this fits diffusion code models (DiffuCoder, [@arxiv2506_20639]; Dream-Coder 7B, [@arxiv2509_01142]), where the next state is sampled jointly rather than autoregressively, and the specification-is-the-program framing [@arxiv2603_17399], where the entire trace is the spec.
- **Static, no-trace.** Some systems (SemCoder's static mode, the trace-free baselines in Do Code Semantics Help?) explicitly drop temporal modeling at inference, reducing to single-shot prediction.

### 5.3 Axis 3 — Representation

The WM literature has converged most strongly on this axis, and the code-WM literature remains most uneven on it. Adapting Li et al.'s four-category split (GLV / TFS / SLG / DRR) to code yields five classes, of which only two are well-populated.

| Class | Encodes the world as | Vision analog | Code exemplars |
|---|---|---|---|
| **Token Sequence (TS)** | Discrete or continuous token streams with execution traces, variable bindings, or rationales interleaved with source | Token-as-pixel (IRIS, TWM, Genie, Sora) | CWM [@arxiv2510_02387], CodeExecutor [@arxiv2305_05383], TRACED [@arxiv2306_07487], NExT [@arxiv2404_14662], SemCoder [@arxiv2406_01006] — the dominant code-WM mode |
| **Global Latent Vector (GLV)** | A compact vector updated recurrently, encoding the entire program/agent state | RSSM (Hafner et al., DreamerV1–V3) | No clean exemplar. CoLA [@arxiv2503_21383] introduces a learned action codebook but is otherwise a standard LLM, not RSSM-style |
| **Spatial / Structural Grid (SLG)** | A geometric or structural grid (BEV/voxel in vision; AST, call-graph, CFG in code) | OccWorld, DriveWorld | No exemplar. RepoGraph [@arxiv2410_14684] uses a static dependency graph but does not predict over it as a WM |
| **Decomposed Object / Slot (DOR)** | Distinct persistent latent slots for objects in the world | SlotFormer and object-centric WMs | No exemplar. No code-WM models variables, scopes, or classes as discrete persistent slots |
| **Synthesized executable (N3)** | The world model *is* an executable program, synthesized rather than learned | (orthogonal to vision) | GIF-MCTS [@arxiv2405_15383], WorldCoder, Executable WMs for ARC-AGI-3 [@arxiv2605_05138] |

Verifiers (Lean, Dafny, Z3) and PRMs are intentionally absent from this table. A verifier is not a *representation* of the world; it is a grounding oracle over candidate artifacts. A PRM is a backward-looking critic, not a forward predictor. Both belong in §5.4 below.

**Three white spaces.** The Dreamer-style GLV, the object-centric DOR, and the spatial-grid SLG representations have not been instantiated for code, despite being mature for vision. §18 lists these as open problems, with the caveat that not all three look equally promising. The Dreamer-style gap is contestable (§17.3), while the object-centric and structural-grid gaps look more genuine.

### 5.4 Grounding mode (orthogonal to representation)

A second classification asks how each system's predictions are validated. This analog of Li et al.'s reality column addresses the decoupling between WM-head accuracy and downstream task success that DyMo [@arxiv2506_02918] and §17.7 develop.

| Grounding mode | Definition | Code exemplars |
|---|---|---|
| None / self-report | Predictions never validated against ground truth | RAP [@arxiv2305_14992], basic LLM-as-WM planners |
| Execution-grounded | Predictions checked against real interpreter / runtime | CWM [@arxiv2510_02387], TRACED [@arxiv2306_07487], NExT [@arxiv2404_14662], SemCoder [@arxiv2406_01006], RLEF [@arxiv2410_02089] |
| Verifier-grounded | Outputs checked by Lean / Dafny / Verus / Rocq / Z3 | ATLAS [@arxiv2512_10173], Re:Form [@arxiv2507_16331], CLEVER [@arxiv2505_13938], VeriStruct [@arxiv2510_25015], AutoRocq [@arxiv2511_17330] |
| Synthesized-simulator-checked | Synthesized world model checked against held-out transitions | GIF-MCTS [@arxiv2405_15383], Executable WMs for ARC-AGI-3 [@arxiv2605_05138] |
| Critic-grounded (not a WM) | Backward-looking value/quality score, no rollout | ExecVerify [@arxiv2603_11226], SWE-PRM [@arxiv2509_02360], ThinkPRM [@arxiv2504_16828] — listed for contrast; these are critics, not WMs (§17.4) |

Grounding mode is orthogonal to the representation axis: a token-sequence representation can be execution-grounded (CWM) or self-report (RAP); an N3 synthesized-simulator can be checked against transitions (GIF-MCTS) or never validated. The WM-fidelity question of §17.7 structurally asks whether a system's grounding mode is strong enough to falsify a bad WM at training time.

---

## 6. Foundations: Neural Execution as Implicit World Modeling

Learning to Execute (Zaremba & Sutskever, [@arxiv1410_4615]) established both feasibility and brittleness. Show Your Work — Scratchpads [@arxiv2112_00114] provided the pivotal contribution: by training a Transformer to emit intermediate computation states, the authors recovered much of the LSTM-era execution-prediction performance at scale, presaging the trace-pretraining lineage of §6. CRUXEval [@arxiv2401_03065] and REval [@arxiv2403_16437] provide the canonical execution-reasoning benchmarks. The lesson the field absorbed: *replacing* the interpreter with a neural network is harder than *augmenting* a transformer with interpreter-style supervision. Modern systems all take the latter path.

---

## 7. The Trace-Pretraining and CWM Lineage

### 7.1 Trace-pretraining as a recipe

CodeExecutor [@arxiv2305_05383] trains a Transformer to simulate Python execution token-by-token. TRACED [@arxiv2306_07487] adds dynamic-state supervision to a code-LLM pretraining mix. NExT [@arxiv2404_14662] formats traces as natural-language rationales, letting a chat-style LLM reason about runtime behavior via chain-of-thought. SemCoder [@arxiv2406_01006] generalizes to monologue reasoning linking source-text to execution state.

The 2025 wave consolidated and stress-tested the approach. What I cannot execute, I do not understand [@arxiv2503_05703] trains and evaluates LLMs explicitly on traces with dynamic scratchpads, pushing Llama-3.1-8B from 37.8% to ~80% on CRUXEval-O. Code Execution as Grounded Supervision [@arxiv2506_10343] repurposes line-by-line traces as verifiable CoT. Self-Execution Simulation [@arxiv2604_03253] lets the model train on its own execution predictions. Demystifying Errors in LLM Reasoning Traces [@arxiv2512_00215] audits where trace-trained LLMs fail. Do Code Semantics Help? [@arxiv2509_11686] provides the most damaging paper in the lineage: a comprehensive ablation across DeepSeek-Coder, LLaMA-3, and Gemma-2 with five trace representations found that no single representation consistently improved code generation, and in 7 of 9 synthesis settings the no-trace baseline won or tied.

### 7.2 TRACED [@arxiv2306_07487]

TRACED augments a RoBERTa/UnixCoder pre-training mix with two execution-grounded heads on top of standard MLM: per-line program-state classification (variable type and quantized value over 30 bins) and per-line execution coverage. Trained on ~121k C traces from CodeNet collected via gdb, it showed that quantized variable-value prediction works as an auxiliary signal; concrete values lose to discretized bins. On static execution estimation, full-path accuracy rose from UnixCoder's 63.7% to 71.6%, and downstream clone retrieval and defect detection improved modestly. The contribution: trace prediction as a pre-training side objective, not a separate model.


### 7.3 NExT [@arxiv2404_14662]

NExT inlines execution traces into source as Python-style comments (`# (k) varA=...; varB=...`) and trains PaLM 2-L on (rationale, fix) candidates via STaR-style self-training: sample 32 candidates per problem, accept those that passed unit tests, SFT on the accepted set, repeat. After ten iterations Mbpp-R pass@1 climbed from 23.2% to 49.3% (+26.1 absolute). The result that matters most for the rest of the survey: NExT retains a +17 absolute gain (23 → 40.8) on Mbpp-R when traces are removed at inference, which makes it the clearest example of trace pretraining transferring to non-trace inference on a repair task.


### 7.4 SemCoder [@arxiv2406_01006]

SemCoder formalizes monologue reasoning linking four code modalities — natural-language description, source, operational trace, and abstract input-invariant constraints — under a single NTP objective with rejection-sampled training data (the PYX corpus). Distinctive features: forward and backward monologues (NExT is forward-only), abstract-semantics constraints rather than concrete state at every step, and entirely static inference. SemCoder-1.3B reached CRUXEval-I/O 63.6/65.1 vs GPT-3.5-turbo's 50.3/59.0, and a monologue-format ablation beat Scratchpad and NExT.


### 7.5 CWM [@arxiv2510_02387]

CWM is a 32B dense decoder-only Transformer with grouped-query attention, sliding-window blocks, and RoPE — architecturally Llama-class. What earns it the world-model name is the mid-training datamix: 5T tokens of Python observation-action traces (120M traced functions, 262k CodeContests traces, 70k repo-level traced commits, 75M natural-language rewrites) plus 3M ForagerAgent SWE trajectories from 10.2k Dockerized repositories. Tokens are formatted so next-token prediction *is* next-state prediction at line granularity. CWM reached 65.8% on SWE-bench Verified with test-time scaling (best@16 over 40 verifier-reranked samples) and 94.3% on CRUXEval-Output. Its second technical contribution is Activ, which uses GitHub Actions CI to scale executable repository images. CWM is behaviorally explicit (emits stack frames) but architecturally implicit (no separate dynamics head).


Important caveat (developed further in §17): the 65.8% headline is not pure pass@1 but best-of-16 with verifier reranking. Pure pass@1 is approximately 53–55%. The trace-mid-training contribution is not causally isolated from the ForagerAgent-trajectory contribution and from the joint-RL contribution. Without an ablation removing one while holding the others fixed, the world-model component's causal role remains unfalsifiable.



### 7.7 GIF-MCTS / Generating Code World Models via MCTS [@arxiv2405_15383]

GIF-MCTS treats the world model itself as a Python program: an `Environment.step(s,a) → (s', r, done)` class synthesized by an LLM to match a small batch of pre-collected `(s, a, r, s', d)` transitions. MCTS over partial programs uses three action types (*generate* lines, *improve* full program given a failing transition, *fix* runtime/syntax errors), with reward equal to the fraction of transitions reproduced correctly. The synthesized world model, once compiled, runs 4–6 orders of magnitude faster than calling an LLM as world model. On APPS-Competition it reached 28.3% strict pass@20 (Llama-3-70B), beating WorldCoder's 25.1%. The conceptual contribution: search over candidate Python world-model programs rather than train a neural one.


---

## 8. World Models for Code Agents

Once an LLM acts as an agent in a non-trivial environment, the world-model question becomes whether the agent simulates the environment's response. Three sub-environments dominate.

### 8.1 Web agents

Web Agents with World Models [@arxiv2410_13232] systematizes the thread. DyMo / World Modeling Improves LM Agents [@arxiv2506_02918] adds a next-state prediction head to function-calling agents and reports gains on BFCL-V2, though with a caveat (§17): the WM head reached 90–94% state-prediction accuracy while the underlying policy reached only 72.8% task success, which illustrates that WM-head accuracy and agent accuracy can decouple.

WebDreamer [@arxiv2411_06559] treats the web as a POMDP in which the LLM imagines natural-language state-change descriptions for each candidate click, type, or select. A specialist Dreamer-7B (Qwen2-VL-7B fine-tuned on 3.1M synthesized (initial visual state, action, state-change) tuples from random walks over Common Crawl URLs) provides cheap rollouts. At inference, model-predictive control samples actions, scores simulated trajectories with GPT-4o on a 3-scale rubric, and executes the argmax. On VisualWebArena, Online-Mind2Web, and Mind2Web-Live, this beat the reactive baseline by +34/+42/+24% relative (≈+6–11 absolute) while running 4–5× faster than tree search. The bet: when actions are irreversible (forms, purchases), one-step MPC over an LLM-as-WM beats backtracking search.


### 8.2 OS / computer-use agents

Reinforcement World Model Learning for LLM-based Agents [@arxiv2602_05842] and World Models as an Intermediary between Agents and the Real World [@arxiv2602_00785] generalize the lens: a learned WM mediates between LLM and expensive environment.

Dyna-Think [@arxiv2506_00320] trains a single Qwen2.5-32B to internalize world-model simulation inside its `<think>` block for OSWorld and WindowsAgentArena. Two stages: DIT (imitation learning on R1 traces cleaned to keep only WM-simulation text) and DDT (Dyna-Q-style joint training over three WM heads — next state, state-diff, critic-prediction — with rejection-sampled policy updates). On OSWorld BoN the 32B model reached 43.1, essentially matching DeepSeek-R1 at 685B with half the tokens. World-model accuracy correlated with task success at r=0.32 across models. Dyna-Think is the corpus's leading instance of policy and learned world model hosted in the same LLM.


### 8.3 SWE agents

SWE-bench [@arxiv2310_06770] and SWE-Gym [@arxiv2412_21139] defined the eval and training environment respectively. CodeAct [@arxiv2402_01030] made the Python interpreter the unified action space. Reflexion [@arxiv2303_11366] provided the earliest entry with episodic verbal RL. Nanbeige SWE-World [@arxiv2602_03419] trains a learned Docker-free execution surrogate. Understanding by Reconstruction [@arxiv2603_11103] reverses the development process to harvest agentic pretraining traces. SWE-TRACE [@arxiv2604_14820] provides process-level reward modeling over trajectories. Self-Play SWE-RL [@arxiv2512_18552] introduces adversarial bug-injection/repair self-play. Bootstrapping Coding Agents — The Specification Is the Program [@arxiv2603_17399] reframes the SWE task itself as a programmatic spec.

The §16 empirical synthesis separates three regimes: execution-grounded open-weight model training (CWM, SWE-RL), execution-grounded agents with learned simulators (Nanbeige SWE-World), and scaffold evolution around closed-model executors (Darwin GM, Huxley GM). Under best-of-k or verifier-reranked protocols, several systems report 60–68% on SWE-bench Verified, but those numbers are not directly comparable to pass@1 model-training results, and the scaffold-evolved systems are not 32B open-weight world-model-trained — they run frontier closed models inside an evolved harness.

---

## 9. RL with Execution as the World Signal

The model-based-RL framing — the world model is what the policy plans over — has produced a clean lineage.

### 9.1 RLEF [@arxiv2410_02089]

RLEF formulates iterative code synthesis as a POMDP. Actions are full code responses, observations are formatted public-test execution feedback, and rewards come from held-out private tests. Standard PPO with KL regularization and a 3-turn limit. Llama-3.1-70B+RLEF reached 37.5/40.1 pass@1 valid/test on CodeContests at budget 1@3 (vs 25.9/27.5 baseline), matching AlphaCodium-GPT-4 with 5 samples; at 10@100 it reached 54.5/54.5, surpassing the AlphaCode 41B+clustering baseline. Critically, a random-feedback ablation removed the entire gain, which isolates that the model learns to *use* execution feedback rather than just sample more.


### 9.2 SWE-RL [@arxiv2502_18449]

SWE-RL applies GRPO to 273k high-quality PR seeds with a rule-based, continuous reward (`difflib.SequenceMatcher` similarity between predicted and oracle patch); no code execution at training time. Llama-3.3-70B fine-tuned this way (Llama3-SWE-RL-70B) hit 41.0% pass@1 on SWE-bench Verified with the Agentless Mini scaffold. The surprising result was OOD transfer: HumanEval+ 76.2→79.9, CRUXEval-O 61.9→75.5, MATH 70.9→73.7, while SFT on the same data *degraded* on these. Continuous reward beat discrete in ablation (34.8 vs 29.0 oracle-repair). The thesis: partial-credit similarity rewards on real PR patches induce reasoning patterns that transfer beyond the training distribution.


### 9.3 Process Reward Models

ExecVerify [@arxiv2603_11226], SWE-PRM [@arxiv2509_02360], DataPRM [@arxiv2604_24198], and ThinkPRM [@arxiv2504_16828] form a cluster where the WM is a learned evaluator of partial trajectories. As §17 develops critically, this is not the same object as a forward world model: PRMs are critics with execution grounding. They cannot roll out, cannot simulate counterfactuals. Survey hygiene argues for keeping the distinction.

---

## 10. Planning and Search with Code World Models

### 10.1 RAP [@arxiv2305_14992]

RAP frames reasoning as MCTS in a self-consistent MDP where the same frozen LLM serves as both policy and transition model. A state is a textual configuration (blocks layout, intermediate variables, current fact), an action is a step proposed by the LLM, and the transition is obtained by re-prompting. Rewards combine action likelihood, state confidence (majority voting), self-evaluation, and task heuristics. On Blocksworld 4-step, RAP@10 reached 0.86 with LLaMA-33B, surpassing GPT-4+CoT's 0.63 by 33% relative. The conceptual template — repurpose the LLM as both policy and transition model under MCTS — is what every later LLM-as-WM paper extends.


Tree of Thoughts [@arxiv2305_10601], AlphaZero-like Tree Search for LLM Decoding [@arxiv2309_17179], Tree Search for LM Agents [@arxiv2407_01476], and Mastering Board Games by External/Internal Planning with LMs [@arxiv2412_12119] develop the search frame. The last gives the most direct contemporary recipe for learned tree-search with LLM-as-WM, straightforwardly transferable to code.

### 10.2 Execution-conditioned generation

Execution Guided Line-by-Line Code Generation [@arxiv2506_10948] uses classifier-free guidance to condition next-token prediction on candidate-runtime outcomes. Jupiter [@arxiv2509_09245] formulates notebook state as MCTS nodes. REPL-Plan [@arxiv2411_13826] reuses a REPL state pool across tasks. The substrate is well-developed for short-horizon code-gen, less so for long-horizon multi-file SWE.

---

## 11. JEPA, Dreamer, and the Latent-Action Gap

LeCun's Joint Embedding Predictive Architecture (I-JEPA, [@arxiv2301_08243]) predicts in embedding space rather than pixel space. The Dreamer family — Hafner et al.'s DreamerV1 [@arxiv1912_01603], DreamerV2 [@arxiv2010_02193], and DreamerV3 [@arxiv2301_04104], built around the Recurrent State-Space Model — has near-zero direct application to code. Two papers occupy the gap.

### 11.1 LLM-JEPA [@arxiv2509_14252]

LLM-JEPA adds a joint-embedding predictive objective to standard NTP training, using (text, code) as the two JEPA views with the LLM's last-layer last-token hidden state as encoder and a tied-weights `[PRED]` token as predictor. The loss is `L_NTP(text) + λ · d(Pred(Enc(Text)), Enc(Code))` with cosine distance. On Llama-3.2-1B fine-tuned on NL-RX-SYNTH the gain was 57.3 → 71.5 (+14.2 absolute); on Spider, GSM8K, and HellaSwag the wins were smaller. The top-100 singular values of `Enc(Text) − Enc(Code)` collapsed by orders of magnitude, which indicates a low-rank text↔code mapping. Whether this counts as JEPA in the LeCun sense or as a regularizer on top of NTP remains open and is discussed in §17.


### 11.2 CoLA [@arxiv2503_21383]

CoLA replaces the 128k-token action space of an LLM with a small learned latent-action codebook. Three modules: a VQ-VAE-style inverse-dynamics model that infers latent action `aₜ` from `(x₁:t, xₜ₊₁)`; a language world model that inserts the chosen latent action into the LLM embedding stream and decodes the next token; and a policy `π(aₜ | x₁:t)` behavior-cloned from inverse-dynamics labels then RL-tuned. Action-level MCTS over the learned codebook (with a Double-DQN Q-function) reached Math-500 68.2 vs 63.0 baseline MCTS-Q. CoLA is the corpus's most direct Dreamer-for-LLMs instance: the action space is genuinely compressed, and rollout and search operate in that compressed space.


### 11.3 The gap

Despite CWM and dozens of LLM-as-world-model papers, no public Dreamer/RSSM-style latent-imagination world model has been trained for SWE agents. CWM rolls out in token space. CoLA is the closest concrete instance. UniZero [@arxiv2406_10667] generalizes MuZero with transformers but is rarely instantiated on code. Genie [@arxiv2402_15391] gives the vision-side template. JEPA for RL [@arxiv2504_16591] extends the energy-based objective to RL.

Whether the gap matters remains open and is developed critically in §17. The vision-domain pressure that motivated Dreamer's RSSM design (pixel-space rollout cost) does not exist for code, where state is small and the simulator is available. The argument *for* latent imagination rests on inference-time speed and the action-space compression CoLA demonstrates, not on rollout cost per se.

---

## 12. Specialized Domains

**Diffusion code models.** DiffuCoder [@arxiv2506_20639], Dream-Coder 7B [@arxiv2509_01142]. Iterative denoising accommodates plan-then-refine generation.

**Decompilation and cross-language.** SK2Decompile [@arxiv2509_22114], SALT4Decompile [@arxiv2509_14646]. Translation as semantic-simulation task. EquiBench [@arxiv2502_12466] supplies the equivalence eval.

**Hardware / RTL.** VeriRL [@arxiv2508_18462], ChipSeek [@arxiv2507_04736], and VeriCoder [@arxiv2504_15659] form a cluster where the simulator is the world model. Hardware suits this approach because simulators are precise, fast, and deterministic, closer to Atari than to Python.

**ARC and abstract synthesis.** Executable World Models for ARC-AGI-3 [@arxiv2605_05138] instantiates literal-WM-per-task: synthesize a Python world model verified against observations. SOAR [@arxiv2507_14172] evolves programs over ARC. Darwin and Huxley Godel Machines ([@arxiv2505_22954], [@arxiv2510_21614]) close the self-improvement loop.

---

## 13. Reasoning, Process Rewards, Memory

**Long-CoT reasoning for code.** o1-Coder [@arxiv2412_00154] replicates o1 with MCTS+RL. R1-Code-Interpreter [@arxiv2505_21668] supplies the open SFT+RL recipe across 144 tasks. Scaling Test-Time Compute to Achieve IOI Gold Medal [@arxiv2510_14232] shows open-weight gpt-oss-120b matching closed reasoning models via inference-time scaling.

Long-CoT reasoning amounts to mental execution: the chain-of-thought simulates the world model the network never explicitly trained. CWM-style explicit world modeling and R1-style reasoning are partial substitutes. Whether they compose multiplicatively remains open.

**Memory.** Episodic Memory is the Missing Piece for Long-Term LLM Agents [@arxiv2502_06975] frames the gap. Memory as Action [@arxiv2510_12635] treats memory operations as RL-learnable actions. RepoGraph [@arxiv2410_14684] provides a durable repo-level dependency graph.

---

## 14. Verification, Probing, Safety

### 14.1 Formal verification

The verifier-grounded lineage is the only research direction in the corpus that does not rely on LLM self-report for correctness; the verifier provides ground truth.

ATLAS [@arxiv2512_10173] provides the most thorough end-to-end pipeline in the corpus for scaling verified-code data. From TACO-verified (12.8k LeetCode-style problems with Python references and tests), ATLAS produced 2,751 verified Dafny programs decomposed into 19,385 training examples across six tasks (NL-to-Code, NL-to-Spec, Spec-to-Code, Spec-Repair, Impl-Repair, Proof-Infilling). Spec quality was filtered by three SMT-discharged lemma types: soundness, completeness-contradiction, and completeness-perturbation. Qwen-2.5-Coder-7B fine-tuned this way reached DafnyBench Pass@1 of 55.8% (from 32.4%) and DafnySynthesis Pass@5 of 65.8% (from 15.8%, surpassing GPT-4's 53.4). ATLAS does for verified Dafny what auto-formalization did for Lean theorems.


The cluster also includes Re:Form ([@arxiv2507_16331], Dafny+RL), CLEVER ([@arxiv2505_13938], Lean), VeriStruct ([@arxiv2510_25015], Verus), AutoRocq ([@arxiv2511_17330], Rocq), and Semantic Equivalence Self-Play with Formal Verification ([@arxiv2604_17010], Liquid Haskell).

CLEVER's ≤1/161 end-to-end Lean result is the most sobering number in the corpus: frontier models, with Lean type-checker access for self-verification, still fail on >99% of HumanEval-derived problems requiring joint spec and implementation verification. Understanding Formal Reasoning Failures in LLMs as Abstract Interpreters [@arxiv2503_12686] supplies the diagnostic: when asked to reason in the style of formal abstract interpretation over 22 SV-COMP programs, all frontier reasoning models made systematic errors in widening, fixpoint termination, and join operations.

### 14.2 Symbolic execution and LLMs

AutoBug [@arxiv2505_13452], SESpec [@arxiv2506_09550], LLM-Sym [@arxiv2409_09271], and Loop Invariant Generation via Reasoning LLMs + SMT [@arxiv2508_00419] combine LLMs with concrete or symbolic engines. The unifying pattern: the LLM hypothesizes the world model; symbolic execution verifies or extends it.

### 14.3 Probing and mechanistic interpretability

Mechanistic Interpretability of Code Correctness via SAEs [@arxiv2510_02917] and On LLMs' Internal Representation of Code Correctness [@arxiv2512_07404] ask what code LLMs actually represent. Findings: partial, brittle internal execution representations, which supports explicit trace pretraining.

### 14.4 Repair and debugging as world-model probing

Self-Debug [@arxiv2304_05128], InspectCoder [@arxiv2510_18327], Agent That Debugs — Dynamic State-Guided Vulnerability Repair [@arxiv2504_07634], and Agentic Code Reasoning ([@arxiv2603_01896], semi-formal execution-path reasoning without running code) share a pattern: maintain a belief over program state, query the runtime to update the belief, act on the posterior — Bayesian world-modeling in everything but name.

### 14.5 Safety and malicious code

The Double Life of Code World Models [@arxiv2512_13821] repurposes CWM-style trace predictions for malicious-behavior detection. CodeBreaker [@arxiv2406_06822] provides the offensive analogue. Concolic Execution + LLM for Zero-Day Malware Detection [@arxiv2603_09044] pairs path-prioritization with concrete execution.

---

## 15. Benchmarks and the Evaluation Gap

Benchmarks split cleanly by what they measure.
- **Static code quality.** HumanEval, MBPP, and LiveCodeBench [@arxiv2403_07974] measure code-LLM output without exercising the world-model claim.
- **Execution reasoning.** CRUXEval [@arxiv2401_03065], REval [@arxiv2403_16437], CRUXEval-X [@arxiv2408_13001], TraceEval [@arxiv2605_11006], and PLSemanticsBench [@arxiv2510_03415]. The canonical WM evals.
- **Semantic equivalence.** EquiBench [@arxiv2502_12466], CodeARC [@arxiv2503_23145].
- **Agentic.** SWE-bench, SWE-Gym, WebArena [@arxiv2307_13854], Mind2Web [@arxiv2306_06070], PyBench [@arxiv2407_16732], OSWorld, WindowsAgentArena.

**The eval gap.** No widely adopted benchmark directly measures world-model fidelity by holding the policy fixed and varying the WM. Every measurement of WM capability is mediated through downstream task performance, so the field cannot distinguish *the model has internalized program semantics* from *the model is exploiting trace-token shortcuts in the test distribution*. Demystifying Errors in LLM Reasoning Traces [@arxiv2512_00215] supplies the diagnostic: even DeepSeek-R1, o4-mini, Gemini 2.5 Flash, and Claude 4, when asked to simulate execution and explain their reasoning, produced traces with errors clustering into nine categories (Computation, Indexing, Control Flow, Skip Statements, Misvaluation of Native API, Hallucination, Input Misread, etc.). Models with 85–98% final-answer accuracy on output prediction produced traces with systematic errors throughout. The decoupling — high outcome accuracy, low process fidelity — is the signature of a system that has learned to predict outcomes without faithfully simulating dynamics.

---

## 16. Empirical Landscape

### 16.1 SWE-bench scoreboard

Protocols mix in SWE-bench reporting and are non-comparable across the obvious axes. The table below splits into three protocol classes; readers should compare within, not across, classes. **Training / Evaluation regime**: *Frozen-model scaffold* = no model training (agent loop around a frozen closed model); *EG-LLM SFT* = supervised fine-tune on agent trajectories; *EG-LLM + RL* = RL with execution rewards; *EG-agent + learned simulator* = SFT+RL plus a learned execution surrogate; *EG-LLM + trace mid-train + RL* = the CWM lineage; *Scaffold-evolved* = recursive scaffold/agent self-improvement around a frozen closed model. **WM-Arch** is reserved for systems with explicit transition/rollout machinery (N1/N2/N3 from §3); no row in this table qualifies.

**Table 16.1a — Single-sample resolution (pass@1 on Verified unless noted)**

|System|Base model|Bench|Pass@1|Regime|Source|
|---|---|---|---|---|---|
|SWE-agent|GPT-4 Turbo|full|12.5%|Frozen-model scaffold|[@arxiv2405_15793]|
|AutoCodeRover|GPT-4|Lite|19.0%|Frozen-model scaffold|[@arxiv2404_05427]|
|Agentless|GPT-4o|Lite|32.0%|Frozen-model scaffold|[@arxiv2407_01489]|
|SWE-Gym|Qwen-2.5-Coder-32B|Verified|20.6%|EG-LLM SFT|[@arxiv2412_21139]|
|Agent-RLVR (no RM)|Qwen-2.5-72B|Verified|22.4%|EG-LLM + RL|[@arxiv2506_11425]|
|Long-Context Multi-Turn RL|Qwen-2.5-72B|Verified|39.0%|EG-LLM + RL|[@arxiv2508_03501]|
|SWE-RL (Llama3-SWE-RL-70B)|Llama-3.3-70B|Verified|**41.0%**|EG-LLM + RL|[@arxiv2502_18449]|
|Nanbeige SWE-World (RL)|Qwen-2.5-Coder-32B|Verified|55.0%|EG-agent + learned simulator|[@arxiv2602_03419]|
|CWM|CWM-32B|Verified|*not directly reported* †|EG-LLM + trace mid-train + RL|[@arxiv2510_02387]|

† The CWM paper does not report a pure pass@1 number under the standard protocol. The headline 65.8% in Table 16.1b is best@16 with verifier reranking. Inferred pass@1 from the paper's reported figures is approximately 53–55%, but this is an estimate from the survey authors, not a directly reported number, and is not placed in the main row.

**Table 16.1b — Best-of-k with verifier reranking / TTS**

|System|Base|Bench|Score|Sample budget|Source|
|---|---|---|---|---|---|
|Agent-RLVR + RM rerank|Qwen-2.5-72B|Verified|27.8%|rerank over multi-sample|[@arxiv2506_11425]|
|Nanbeige SWE-World (TTS@8)|Qwen-2.5-Coder-32B|Verified|**68.2%**|best@8|[@arxiv2602_03419]|
|CWM (TTS)|CWM-32B|Verified|**65.8%**|best@16 over 40 reranked|[@arxiv2510_02387]|

**Table 16.1c — Scaffold-evolution and self-play around closed-model executors**

|System|Backbone executor|Bench|Score (start → end)|Note|Source|
|---|---|---|---|---|---|
|Darwin Godel Machine|Claude-3.5-Sonnet|Verified|20% → 50%|Scaffold evolves over 80 iterations|[@arxiv2505_22954]|
|Huxley Godel Machine|GPT-5-mini|Verified (500)|— → 61.4%|Scaffold optimized for Verified-60|[@arxiv2510_21614]|
|SICA|Claude-3.5-Sonnet + o3-mini|Verified (subset)|17% → 53%|Scaffold evolves; not a model-training method|[@arxiv2504_15228]|

Citations that quote CWM at 65.8% on SWE-bench Verified without disclosing the best@16/TTS protocol misreport the result rather than reporting direct pass@1 numbers.

**What can and cannot be compared.** Within Table 16.1a the comparable axis is pass@1. SWE-RL's 41.0%, Long-Context-MT-RL's 39.0%, and Nanbeige SWE-World's 55.0% are roughly comparable as open-weight WM-trained pass@1 on Verified. Table 16.1c sits in a different category: these are scaffold-evolution methods over closed models, and treating them as evidence for world-model training conflates scaffold search with model improvement. Reading them inside Table 16.1a alongside model-trained pass@1 numbers is apples-to-oranges.

**Two empirical claims, separately defensible.** (i) On *pass@1*, open-weight WM-trained 32B systems (Nanbeige 55.0%, Long-Context-MT-RL 39.0%, SWE-RL 41.0%) outperform frozen open-weight baselines (Qwen-2.5-Coder-32B raw 6.2%) by 30–50 absolute points. This gain is the strongest case for training on agent trajectories with execution feedback. (ii) On *best@k with verifier reranking* (Table 16.1b), the same models reach 65–68%, but the additional 13–15 points are attributable to TTS reranking infrastructure, not to the WM training. Conflating (i) and (ii) by quoting CWM's 65.8% alongside SWE-RL's 41.0% as both world-model-trained pass@1 SOTA is exactly the misreporting the protocol split is designed to prevent.

### 16.2 Trace pretraining gains on execution-reasoning

|Paper|Backbone|Baseline|After trace pretrain/FT|Delta|Benchmark|
|---|---|---|---|---|---|
|TRACED|UnixCoder|—|+12.4% rel branch-coverage; +25.2% rel variable-value|rel|CodeNet exec|
|NExT|PaLM 2-L|23.2|49.3|**+26.1 abs**|MBPP-R|
|NExT|PaLM 2-L|32.2|42.5|+10.3 abs|HumanEvalFix-Plus|
|SemCoder (1.3B)|DS-Coder 1.3B|base|63.6 / 63.9|+23 abs|CRUXEval-I / O|
|What I cannot execute|Llama-3.1-8B|37.8%|~80%|**+42 abs**|CRUXEval-O|
|Do Code Semantics Help?|DSCoder, Llama-3, Gemma-2|various|≤ a few abs; some regressions|mixed|comprehensive|

For under-trained ≤8B open-weights, trace pretraining delivered +15 to +42 absolute on CRUXEval-O. The Do Code Semantics Help? ablation [@arxiv2509_11686] supplied the disconfirming evidence: across multiple backbones and five trace representations, no single representation consistently outperformed others, and several downstream tasks regressed under trace augmentation. The gain shrinks rapidly with base-model quality. Trace pretraining functions as a remedial intervention for weak code models. Whether frontier models still benefit remains unsettled.

### 16.3 Web/OS agents from WMs

|Paper|Benchmark|Base|With WM|Delta|Mechanism|
|---|---|---|---|---|---|
|WebDreamer (GPT-4o WM)|VisualWebArena|17.6%|23.6%|+34.1% rel (≈+6 abs)|LLM-as-WM + MPC|
|WebDreamer|Online-Mind2Web|26.0%|37.0%|+42.3% rel (≈+11 abs)|same|
|Dreamer-7B (trained WM)|VisualWebArena|base|+4.7 abs|—|trained WM|
|WMA [@arxiv2410_13232]|WebArena|base|action-selection 52→70%|—|trained transition WM|
|Dyna-Think DDT (32B)|OSWorld BoN|RFT~28%|43.1%|≈+15 abs|Dyna-Q + WM head|
|Dyna-Think DDT|WindowsAgentArena|28.4%|34.9%|+6.5 abs|same|

WM gains on web/OS are real but quantitatively small (≤+5–10 absolute task success rate on most benchmarks), and partly confounded with the extra synthetic data the WM generates. DyMo's 90%+ state-prediction accuracy versus 72.8% task success rate exemplifies the decoupling: WM heads can be accurate without the agent being accurate.

### 16.4 Formal verification vs LLM-only

|System|Language|Benchmark|Baseline|With system|Source|
|---|---|---|---|---|---|
|ATLAS|Dafny|DafnyBench Pass@1|32.4%|**55.8%**|[@arxiv2512_10173]|
|ATLAS|Dafny|DafnySynthesis Pass@5|15.8%|**65.8%** (>GPT-4 53.4)|[@arxiv2512_10173]|
|CLEVER|Lean 4|161 problems end-to-end|best frontier|**≤1/161**|[@arxiv2505_13938]|
|VeriStruct|Verus / Rust|11 modules|—|**99.2%** (128/129 fns)|[@arxiv2510_25015]|
|AutoRocq|Rocq|math + verif lemmas|5 baselines|48.0% math / 30.9% verif|[@arxiv2511_17330]|
|Semantic Equiv Self-Play|Liquid Haskell|EquiBench|base|+13.3 pp|[@arxiv2604_17010]|

Verified codegen shows the steepest training-data sensitivity in the survey: small synthetic datasets (2.7K verified Dafny programs in ATLAS) produce +25–50 absolute gains because LLM-only baselines start near zero. CLEVER's ≤1/161 shows that without explicit data or scaffolding, frontier models cannot reliably produce verified code. VeriStruct shows that on curated targets, near-perfect performance is reachable.

### 16.5 Reasoning-model competitive programming

|Model|Codeforces|IOI / ICPC|
|---|---|---|
|gpt-4o|808 (11th pct)|—|
|o1-preview|1258 (62nd pct)|—|
|o1|1673 (89th pct)|—|
|o1-ioi|1807 (~93rd pct)|IOI 2024 49th pct live|
|o3|elite-human-class|IOI 2024 gold|
|gpt-oss-120b + GenCluster|—|IOI 2025 gold (open-weight)|
|Gemini 2.5 Pro Exp|—|ICPC-Eval Pass@1 22.0%|
|DeepSeek-R1|—|ICPC-Eval Pass@1 14.4%|
|Claude 3.7 Sonnet|—|ICPC-Eval Pass@1 11.8%|
|GPT-4o|—|ICPC-Eval Pass@1 5.9%|

Codeforces ratings rose by 999 points in 14 months on the o-series. The same line shows that frontier reasoning models gain almost everything from RL scaling, not from domain-specialized scaffolds, which complicates the case that trace-style world models do causal work for frontier systems.

---

## 17. Critical Perspectives

This section examines where consensus is fragile and where evidence does not yet support common framings. Seven theses follow.

### 17.1 Most current code WMs make data choices, not architectural choices

The empirical center of the field has converged on a particular design: a standard decoder-only LLM trained on an enriched corpus that includes execution traces or agent trajectories. CWM [@arxiv2510_02387] is the largest instance — a 32B Llama-class Transformer with GQA, sliding-window blocks, RoPE, mid-trained on 5T tokens of Python observation-action traces plus 3M ForagerAgent SWE trajectories. There is no separate dynamics head, no inverse model, no recurrent latent. TRACED, NExT, SemCoder, and LLM-JEPA share the pattern: data-side innovation, architecturally standard.

This is a substantive empirical finding, not a complaint. It says that current code-WM gains are achievable without architectural commitment to forward-prediction machinery. Whether deeper commitments (the N1/N2/N3 forms in §3.1) would yield gains beyond what enriched data already provides is the central open question. CoLA [@arxiv2503_21383] is the only system in the corpus that goes further architecturally; its gains are positive but modest. The architectural-commitment question is the one §17.3 and §18 develop.

### 17.2 Trace pretraining has a causal-isolation problem the surface numbers obscure

Do Code Semantics Help? [@arxiv2509_11686] supplies the most damaging paper for the prevailing optimism. It ran a comprehensive ablation across DeepSeek-Coder, LLaMA-3, and Gemma-2 with five representations (Scratchpad, NExT, CodeExecutor, Concise, SemCoder) on program repair, code synthesis, BigCodeBench, LiveCodeBench, and CRUXEval. Its headline: integrating trace-based semantic information into SFT does not significantly enhance code-generation ability. In 7 of 9 synthesis settings the no-trace baseline won or tied. At inference, in 36 of 56 test-scaling configurations, trace prompts hurt.

What I cannot execute, I do not understand [@arxiv2503_05703] is gentler: Execution Tuning reached ~80% CRUXEval-O. But the same paper's downstream evaluations on HumanEval, MBPP, and GSM8K showed negligible gains from trace data in the SFT mix.

The strongest counterexample to barely-transfers is NExT [@arxiv2404_14662], which pushed PaLM 2-L on Mbpp-R from 23.2% to 40.8% with traces removed at test time: a +17.6 absolute gain on the no-trace-at-inference setting, exactly the transfer pattern the skeptical reading says should not happen. The narrower version of the thesis is therefore: trace pretraining transfers to program-repair tasks where the model needs to reason about a buggy program's behavior (where NExT and TraceFixer-style work shines), and barely transfers to fresh code synthesis on benchmarks like HumanEval and MBPP that sit closer to the model's prior. The Do Code Semantics Help? disconfirmation is on synthesis; NExT's transfer is on repair. Both can hold.

The interpretation that survives: trace pretraining helps execution prediction (the thing trained on), transfers to runtime-reasoning-heavy downstream tasks like repair, and barely transfers to fresh code synthesis. This matches the pattern expected if dense execution supervision teaches a runtime-tracking skill rather than a generative model of program intent.

CWM's 65.8% on SWE-bench looks like a counterexample, but the Meta team reports it after trace mid-training *and* 3M ForagerAgent SWE trajectories *and* multi-task RL with verifiable rewards — three interventions stacked. The world-model component is not causally isolated from the SWE-trajectory and RL components. Without an ablation that removes trace mid-training while holding ForagerAgent and RL fixed, the headline remains unfalsifiable. The field has agreed to call CWM a world-model success because the name appears on the model card, not because the experimental design demonstrates it.

### 17.3 The Dreamer-for-code gap may be a non-problem

The conventional framing treats the absence of latent-imagination world models for SWE as the field's largest architectural gap. The empirical record argues the opposite. CWM in token space reaches 65.8% SWE-bench. CoLA produces respectable but not field-shifting results, and even there the WM is fine-tuned on top of a standard LLM rather than replacing it.

Vision world models needed latent rollouts because pixel-space rollouts were too expensive: a frame is ~10^6 dimensions, dynamics are partially observed. Program execution is the opposite: a Python frame is small, dynamics are observable, and the simulator (CPython) is available for free at training time. The pressure that drove Dreamer's RSSM design does not exist for code.

Debugging Code World Models [@arxiv2602_07672] showed that CWM's long-horizon failures are dominated by action hallucination, not state-propagation error. Under teacher forcing CWM tracked state correctly for 128 steps. A latent rollout would compress states but not fix the action policy, which is the actual bottleneck.

The counterargument is fair: latent rollouts permit faster planning at inference, and for multi-agent or population-scale search the speedup is asymptotically meaningful. The survey should retire the *single largest architectural gap* framing and replace it with *an open question whose payoff is not yet demonstrated*.

### 17.4 PRMs and forward WMs solve complementary problems

Process reward models — ExecVerify [@arxiv2603_11226], SWE-PRM [@arxiv2509_02360], ThinkPRM [@arxiv2504_16828], FunPRM [@arxiv2601_22249], DataPRM [@arxiv2604_24198] — score partial trajectories. Forward world models predict `(state, action) → next_state`. In classical model-based RL these play different roles: Dreamer has both a world model (RSSM) and a critic (value function), and the two interact during planning.

In code, the same complementarity holds. A PRM trained on execution traces can score whether a candidate next step looks promising; a forward WM can simulate what that step would actually produce. Current code-WM systems mostly do one or the other, and the design space for combining them is largely unexplored. The cleanest path forward would integrate an execution-grounded PRM as the critic, with a forward predictor (token-space, latent, or synthesized) supplying the candidate rollouts the critic scores.

### 17.5 General Agents Contain World Models is much weaker than its title suggests

Richens et al. [@arxiv2506_01622] prove that any goal-conditioned policy satisfying a regret bound `δ` for sufficiently deep composite goals (depth `n ≫ 1`) must encode an extractable approximation of the transition function with bounded error. The result is genuine and elegant.

But read the assumptions: fully observed environment, finite communicating stationary controlled MDP, goal-conditioned policy satisfying a regret bound for a specific class of LTL composite goals of depth n. Theorem 2 of the same paper explicitly shows that for myopic agents (depth-1 goals), no world model is needed. Real SWE agents are myopic-ish over short turns and approximately competent over longer ones; their environments are partially observed (rarely full filesystem state); they violate stationarity (the repository changes under their actions); and their regret bound for arbitrary composite goals is unknown and almost certainly not satisfied. The authors caveat this in §6 (Limitations) of their paper.

The theorem provides an existence proof for an idealized agent class. It is not an empirical statement that SWE coding agents have learned world models, and it provides no guidance about the fidelity of any world model they may have learned.

### 17.6 The verifier-grounded lineage leads under a narrow scope

ATLAS, Re:Form, CLEVER, VeriStruct, AutoRocq, and the Liquid Haskell self-play paper [@arxiv2604_17010] share a property no LLM-only system possesses: code whose correctness is machine-checked against a formal specification. Compare to the SWE-bench paradigm, where correctness means hidden unit tests pass — a weaker guarantee, because unit tests cover specific inputs and a system can pass them while being wrong on adjacent inputs.

The abstract-interpreter paper [@arxiv2503_12686] provides the diagnostic: when frontier reasoning LLMs were asked to reason in the style of formal abstract interpretation over 22 SV-COMP programs, they made systematic errors in widening, fixpoint termination, control-flow propagation, and meet/join operations. They generated unsound invariants on programs as small as `count_by_2.c`. If LLMs cannot reliably perform interval-domain abstract interpretation on toy C programs, claims that they have learned faithful internal world models of program semantics demand a lot of inferential work.

The verifier-grounded line is the only research direction that does not rely on LLM self-report for correctness. Scoped carefully, it leads on synthesis-from-spec (ATLAS reached 65.8% Pass@5 on DafnySynthesis at 7B, surpassing GPT-4) and on near-perfect verified completion of curated targets (VeriStruct 99.2% on 11 Verus modules). It does not lead on end-to-end verified codegen from natural language: CLEVER reported ≤1/161 on Lean problems requiring joint spec and implementation verification. The future of correct code is plausibly hybrid — neural proposal, symbolic verification, with the verifier providing ground truth that learned world models cannot — but the hybrid is not yet a finished pillar. The verifier line is cataloged in §14.1 alongside symbolic execution and abstract-interpretation probing; readers who accept this thesis should weight that subsection more heavily than its sequence position suggests.

### 17.7 The evaluation gap is structural

Across CRUXEval, REval, CRUXEval-X, PLSemanticsBench, TraceEval, and EquiBench, no benchmark holds policy fixed and varies world-model quality. Every measurement of world-modeling capability is mediated through downstream task performance, so the field cannot distinguish *the model has internalized program semantics* from *the model is exploiting trace-token shortcuts in the test distribution*.

Demystifying Errors in LLM Reasoning Traces [@arxiv2512_00215] provides the diagnostic: even DeepSeek-R1, o4-mini, Gemini 2.5 Flash, and Claude 4, when asked to simulate execution, produced traces with errors in nine systematic categories. Models with 85–98% final-answer accuracy on output prediction produced traces with systematic errors throughout. High outcome accuracy, low process fidelity: the signature of a system that predicts outcomes without faithfully simulating dynamics.

Self-repair literature exhibits the same pathology. Olausson et al. [@arxiv2306_09896] showed that GPT-4 self-repair on APPS and HumanEval, normalized by compute, often performs worse than i.i.d. resampling. The bottleneck is the model's feedback quality, not its repair capability. Human-written feedback boosts repair success by 1.58×. The model can generate code, can sometimes recognize bugs, but cannot reliably simulate why its code is wrong, which is exactly what a faithful world model would let it do. The empirical bound on LLM self-repair is, in effect, an empirical bound on the fidelity of the implicit world model the LLM is running. Calling that world model internal is fine; calling it good is not.

Until benchmarks measure process fidelity independently of outcome, *is this system actually building a world model?* remains scientifically undecidable.

---

## 18. Open Problems

The critical perspectives of §17 reshape the conventional open-problems list. Six problems where the literature is thinnest and the upside is largest:

**1. Causal isolation of trace-pretraining contributions.** Every claim of the form *this WM-trained model achieves X* should be paired with an ablation removing the WM component while holding training data and RL fixed. CWM in particular needs this. Without it, the headline numbers underdetermine whether the WM did the work.

**2. World-model fidelity as a first-class metric.** §15's eval gap is concrete: build a benchmark where holding policy fixed and varying WM quality causes measurable variation in planning quality, independent of downstream task. This benchmark would clarify the field more than any single new model.

**3. Hybrid neural-symbolic systems.** §17.6 argues the verifier-grounded line leads on its scope. The natural integration is neural proposal, symbolic verification, with the verifier providing gradient-free correctness signal and the neural component providing proposals at scale. Differentiable surrogates of symbolic verifiers (Lean, Dafny, Rocq) that pass verifier-style gradients during training remain open.

**4. Multi-modal WMs for coding.** GUI agents need pixel-level WMs (Neural Computers, [@arxiv2604_06425], provides a first attempt). Tying pixel WMs to code-state WMs through a shared latent remains essentially unsolved.

**5. Long-horizon credit assignment with execution-grounded rewards.** PRMs (§9.3) are early, and §17.4 argues they should be conceptually separated from world models. The right structure for rewarding an agent across hundreds of execution-grounded steps remains open.

**6. World models of the developer, not just the program.** All current WMs model the machine. Few model the developer intent with comparable fidelity. ATLAS and Re:Form gesture in this direction by treating the spec as the WM. A full developer-intent WM would close the agentic loop.

Dreamer-for-SWE-agents is not listed as the field's largest gap. §17.3 argues the pressure motivating that direction in vision does not transfer to code. It remains an interesting research question, not the highest-leverage one.

**Three under-explored representations.** The §5.3 taxonomy table flags three classes of representation, mature in vision-WM, that have no code-WM exemplar:

- *Global Latent Vector (Dreamer-style RSSM)* — discussed and contested above. The Hafner et al. DreamerV1–V3 line proves the design space exists; whether it pays off for code is the question §17.3 leaves open.
- *Spatial / Structural Grid* — the analog of OccWorld / BEV for code would be a learned predictive grid over AST nodes, call-graph edges, or CFG states. RepoGraph [@arxiv2410_14684] shows the static version is useful as agent state; the predictive version remains unexplored.
- *Decomposed Object / Slot (object-centric WMs)* — the analog for code would model variables, scopes, or classes as discrete persistent slots whose state propagates independently. No paper in the corpus instantiates this, despite obvious mappings (each variable is an object, each frame is a scene).

The object-centric and structural-grid gaps look more genuine than the Dreamer one, because they exploit structure that code already has (objects = variables, grids = AST/CFG) rather than borrowing pressure from a domain (vision) where the structural assumptions differ.

---

## 19. Conclusion

Across the literature surveyed here, a single trajectory is visible: from neural execution (modeling the machine), through trace pretraining (modeling execution implicitly), to CWM and its descendants (modeling execution explicitly with a named artifact), to agentic SWE and RL (modeling the environment), to JEPA and latent-action models (modeling in compressed space), and on toward formal verification, probing, and safety (modeling reliably). What was a scattered set of insights in 2014 has by 2026 cohered into a recognizable research program with a recognizable artifact: the code world model.

The remaining work splits into two halves. The first is empirical: close the eval gap, isolate the causal contribution of WM-training, build hybrid neural-symbolic systems whose correctness is verifier-checkable rather than test-checkable. The second is rhetorical: hold the term *world model* to a strict definition so the literature can distinguish architectural commitments from training-data choices, and resist the temptation to oversell extractability theorems and latent-imagination analogies whose premises do not transfer to code.

The opportunity is large precisely because the framework is now clear enough to identify what is missing. The work to do is the work this survey has tried to make visible.

---

---

## Appendix A · References

All citations in this survey use arxiv identifiers inline (e.g. `[@arxiv2510_02387]`). Each cited identifier resolves to one entry below.

- **[@arxiv1410_4615]** — Learning to Execute. https://arxiv.org/abs/[@arxiv1410_4615]
- **[@arxiv1511_06279]** — Neural Programmer-Interpreters. https://arxiv.org/abs/[@arxiv1511_06279]
- **[@arxiv1711_07163]** — Dynamic Neural Program Embedding for Program Repair. https://arxiv.org/abs/[@arxiv1711_07163]
- **[@arxiv1803_10122]** — World Models. https://arxiv.org/abs/[@arxiv1803_10122]
- **[@arxiv1906_07181]** — Learning Execution through Neural Code Fusion. https://arxiv.org/abs/[@arxiv1906_07181]
- **[@arxiv1912_01603]** — Dream to Control - Learning Behaviors by Latent Imagination (DreamerV1). https://arxiv.org/abs/[@arxiv1912_01603]
- **[@arxiv2010_02193]** — Mastering Atari with Discrete World Models (DreamerV2). https://arxiv.org/abs/[@arxiv2010_02193]
- **[@arxiv2010_12621]** — Learning to Execute Programs with Instruction Pointer Attention Graph Neural Networks. https://arxiv.org/abs/[@arxiv2010_12621]
- **[@arxiv2107_03374]** — Evaluating Large Language Models Trained on Code. https://arxiv.org/abs/[@arxiv2107_03374]
- **[@arxiv2108_07732]** — Program Synthesis with Large Language Models. https://arxiv.org/abs/[@arxiv2108_07732]
- **[@arxiv2112_00114]** — Show Your Work - Scratchpads for Intermediate Computation with Language Models. https://arxiv.org/abs/[@arxiv2112_00114]
- **[@arxiv2207_01780]** — CodeRL - Mastering Code Generation through Pretrained Models and Deep Reinforcement Learning. https://arxiv.org/abs/[@arxiv2207_01780]
- **[@arxiv2301_04104]** — Mastering Diverse Domains through World Models (DreamerV3). https://arxiv.org/abs/[@arxiv2301_04104]
- **[@arxiv2301_08243]** — I-JEPA - Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture. https://arxiv.org/abs/[@arxiv2301_08243]
- **[@arxiv2302_08468]** — LEVER - Learning to Verify Language-to-Code Generation with Execution. https://arxiv.org/abs/[@arxiv2302_08468]
- **[@arxiv2303_11366]** — Reflexion - Language Agents with Verbal Reinforcement Learning. https://arxiv.org/abs/[@arxiv2303_11366]
- **[@arxiv2304_05128]** — Teaching Large Language Models to Self-Debug. https://arxiv.org/abs/[@arxiv2304_05128]
- **[@arxiv2305_05383]** — Code Execution with Pre-trained Language Models. https://arxiv.org/abs/[@arxiv2305_05383]
- **[@arxiv2305_10601]** — Tree of Thoughts - Deliberate Problem Solving with Large Language Models. https://arxiv.org/abs/[@arxiv2305_10601]
- **[@arxiv2305_14992]** — Reasoning with Language Model is Planning with World Model - RAP. https://arxiv.org/abs/[@arxiv2305_14992]
- **[@arxiv2306_06070]** — Mind2Web - Towards a Generalist Agent for the Web. https://arxiv.org/abs/[@arxiv2306_06070]
- **[@arxiv2306_07487]** — TRACED - Execution-aware Pre-training for Source Code. https://arxiv.org/abs/[@arxiv2306_07487]
- **[@arxiv2306_09896]** — Is Self-Repair a Silver Bullet for Code Generation. https://arxiv.org/abs/[@arxiv2306_09896]
- **[@arxiv2307_13854]** — WebArena - A Realistic Web Environment for Building Autonomous Agents. https://arxiv.org/abs/[@arxiv2307_13854]
- **[@arxiv2309_17179]** — AlphaZero-like Tree-Search can Guide Large Language Model Decoding and Training. https://arxiv.org/abs/[@arxiv2309_17179]
- **[@arxiv2310_06770]** — SWE-bench - Can Language Models Resolve Real-World GitHub Issues. https://arxiv.org/abs/[@arxiv2310_06770]
- **[@arxiv2401_03065]** — CRUXEval - A Benchmark for Code Reasoning, Understanding and Execution. https://arxiv.org/abs/[@arxiv2401_03065]
- **[@arxiv2402_01030]** — Executable Code Actions Elicit Better LLM Agents. https://arxiv.org/abs/[@arxiv2402_01030]
- **[@arxiv2402_15391]** — Genie - Generative Interactive Environments. https://arxiv.org/abs/[@arxiv2402_15391]
- **[@arxiv2403_07974]** — LiveCodeBench - Holistic and Contamination Free Evaluation of Large Language Models for Code. https://arxiv.org/abs/[@arxiv2403_07974]
- **[@arxiv2403_16437]** — Evaluating Large Language Models with Runtime Behavior of Program Execution. https://arxiv.org/abs/[@arxiv2403_16437]
- **[@arxiv2404_05427]** — AutoCodeRover - Autonomous Program Improvement. https://arxiv.org/abs/[@arxiv2404_05427]
- **[@arxiv2404_14662]** — NExT - Teaching Large Language Models to Reason about Code Execution. https://arxiv.org/abs/[@arxiv2404_14662]
- **[@arxiv2405_15383]** — Generating Code World Models with Large Language Models Guided by Monte Carlo Tree Search. https://arxiv.org/abs/[@arxiv2405_15383]
- **[@arxiv2405_15793]** — SWE-agent - Agent-Computer Interfaces Enable Automated Software Engineering. https://arxiv.org/abs/[@arxiv2405_15793]
- **[@arxiv2406_00515]** — A Survey on Large Language Models for Code Generation. https://arxiv.org/abs/[@arxiv2406_00515]
- **[@arxiv2406_01006]** — SemCoder - Training Code Language Models with Comprehensive Semantics Reasoning. https://arxiv.org/abs/[@arxiv2406_01006]
- **[@arxiv2406_06822]** — An LLM-Assisted Easy-to-Trigger Backdoor Attack on Code Completion Models. https://arxiv.org/abs/[@arxiv2406_06822]
- **[@arxiv2406_10667]** — UniZero - Generalized and Efficient Planning with Scalable Latent World Models. https://arxiv.org/abs/[@arxiv2406_10667]
- **[@arxiv2407_01476]** — Tree Search for Language Model Agents. https://arxiv.org/abs/[@arxiv2407_01476]
- **[@arxiv2407_01489]** — Agentless - Demystifying LLM-based Software Engineering Agents. https://arxiv.org/abs/[@arxiv2407_01489]
- **[@arxiv2407_16732]** — PyBench - Evaluating LLM Agent on Various Real-World Coding Tasks. https://arxiv.org/abs/[@arxiv2407_16732]
- **[@arxiv2408_13001]** — CRUXEval-X - A Benchmark for Multilingual Code Reasoning Understanding and Execution. https://arxiv.org/abs/[@arxiv2408_13001]
- **[@arxiv2409_09271]** — Python Symbolic Execution with LLM-powered Code Generation. https://arxiv.org/abs/[@arxiv2409_09271]
- **[@arxiv2410_02089]** — RLEF - Grounding Code LLMs in Execution Feedback with Reinforcement Learning. https://arxiv.org/abs/[@arxiv2410_02089]
- **[@arxiv2410_13232]** — Web Agents with World Models - Learning and Leveraging Environment Dynamics in Web Navigation. https://arxiv.org/abs/[@arxiv2410_13232]
- **[@arxiv2410_14684]** — RepoGraph - Enhancing AI Software Engineering with Repository-level Code Graph. https://arxiv.org/abs/[@arxiv2410_14684]
- **[@arxiv2411_06559]** — Is Your LLM Secretly a World Model of the Internet - WebDreamer. https://arxiv.org/abs/[@arxiv2411_06559]
- **[@arxiv2411_13826]** — REPL-Plan - Interactive and Expressive Code-Augmented Planning with Large Language Models. https://arxiv.org/abs/[@arxiv2411_13826]
- **[@arxiv2411_14499]** — Understanding World or Predicting Future - A Comprehensive Survey of World Models. https://arxiv.org/abs/[@arxiv2411_14499]
- **[@arxiv2412_00154]** — o1-Coder - an o1 Replication for Coding. https://arxiv.org/abs/[@arxiv2412_00154]
- **[@arxiv2412_12119]** — Mastering Board Games by External and Internal Planning with Language Models. https://arxiv.org/abs/[@arxiv2412_12119]
- **[@arxiv2412_21139]** — Training Software Engineering Agents and Verifiers with SWE-Gym. https://arxiv.org/abs/[@arxiv2412_21139]
- **[@arxiv2501_12948]** — DeepSeek-R1 incentivizes reasoning in LLMs through reinforcement learning. https://arxiv.org/abs/[@arxiv2501_12948]
- **[@arxiv2502_06975]** — Position - Episodic Memory is the Missing Piece for Long-Term LLM Agents. https://arxiv.org/abs/[@arxiv2502_06975]
- **[@arxiv2502_12466]** — EquiBench - Benchmarking LLMs' Reasoning about Program Semantics via Equivalence Checking. https://arxiv.org/abs/[@arxiv2502_12466]
- **[@arxiv2502_18449]** — SWE-RL - Advancing LLM Reasoning via Reinforcement Learning on Open Software Evolution. https://arxiv.org/abs/[@arxiv2502_18449]
- **[@arxiv2503_05703]** — What I cannot execute, I do not understand - Training and Evaluating LLMs on Program Execution Traces. https://arxiv.org/abs/[@arxiv2503_05703]
- **[@arxiv2503_12686]** — Understanding Formal Reasoning Failures in LLMs as Abstract Interpreters. https://arxiv.org/abs/[@arxiv2503_12686]
- **[@arxiv2503_21383]** — CoLA - Controlling Large Language Models with Latent Actions. https://arxiv.org/abs/[@arxiv2503_21383]
- **[@arxiv2503_23145]** — CodeARC - Benchmarking Reasoning Capabilities of LLM Agents for Inductive Program Synthesis. https://arxiv.org/abs/[@arxiv2503_23145]
- **[@arxiv2504_07634]** — Agent That Debugs - Dynamic State-Guided Vulnerability Repair. https://arxiv.org/abs/[@arxiv2504_07634]
- **[@arxiv2504_15228]** — A Self-Improving Coding Agent. https://arxiv.org/abs/[@arxiv2504_15228]
- **[@arxiv2504_15659]** — VeriCoder - Enhancing LLM-Based RTL Code Generation through Functional Correctness Validation. https://arxiv.org/abs/[@arxiv2504_15659]
- **[@arxiv2504_16591]** — JEPA for RL - Investigating Joint-Embedding Predictive Architectures for Reinforcement Learning. https://arxiv.org/abs/[@arxiv2504_16591]
- **[@arxiv2504_16828]** — Process Reward Models That Think. https://arxiv.org/abs/[@arxiv2504_16828]
- **[@arxiv2505_13452]** — Large Language Model Powered Symbolic Execution. https://arxiv.org/abs/[@arxiv2505_13452]
- **[@arxiv2505_13938]** — CLEVER - A Curated Benchmark for Formally Verified Code Generation. https://arxiv.org/abs/[@arxiv2505_13938]
- **[@arxiv2505_21668]** — R1-Code-Interpreter - LLMs Reason with Code via Supervised and Multi-stage Reinforcement Learning. https://arxiv.org/abs/[@arxiv2505_21668]
- **[@arxiv2505_22954]** — Darwin Godel Machine - Open-Ended Evolution of Self-Improving Agents. https://arxiv.org/abs/[@arxiv2505_22954]
- **[@arxiv2506_00320]** — Dyna-Think - Synergizing Reasoning, Acting, and World Model Simulation in AI Agents. https://arxiv.org/abs/[@arxiv2506_00320]
- **[@arxiv2506_01622]** — General Agents Contain World Models. https://arxiv.org/abs/[@arxiv2506_01622]
- **[@arxiv2506_02918]** — World Modeling Improves Language Model Agents. https://arxiv.org/abs/[@arxiv2506_02918]
- **[@arxiv2506_09550]** — Integrating Symbolic Execution with LLMs for Automated Generation of Program Specifications. https://arxiv.org/abs/[@arxiv2506_09550]
- **[@arxiv2506_10343]** — Code Execution as Grounded Supervision for LLM Reasoning. https://arxiv.org/abs/[@arxiv2506_10343]
- **[@arxiv2506_10948]** — Execution Guided Line-by-Line Code Generation. https://arxiv.org/abs/[@arxiv2506_10948]
- **[@arxiv2506_11425]** — Agent-RLVR - Training Software Engineering Agents via Guidance and Environment Rewards. https://arxiv.org/abs/[@arxiv2506_11425]
- **[@arxiv2506_20639]** — DiffuCoder - Understanding and Improving Masked Diffusion Models for Code Generation. https://arxiv.org/abs/[@arxiv2506_20639]
- **[@arxiv2507_04736]** — ChipSeek - Optimizing Verilog Generation via EDA-Integrated Reinforcement Learning. https://arxiv.org/abs/[@arxiv2507_04736]
- **[@arxiv2507_14172]** — SOAR - Self-Improving Language Models for Evolutionary Program Synthesis on ARC-AGI. https://arxiv.org/abs/[@arxiv2507_14172]
- **[@arxiv2507_16331]** — Re-Form - Reducing Human Priors in Scalable Formal Software Verification with RL in LLMs on Dafny. https://arxiv.org/abs/[@arxiv2507_16331]
- **[@arxiv2508_00419]** — Loop Invariant Generation - A Hybrid Framework of Reasoning Optimised LLMs and SMT Solvers. https://arxiv.org/abs/[@arxiv2508_00419]
- **[@arxiv2508_03501]** — Training Long-Context, Multi-Turn Software Engineering Agents with Reinforcement Learning. https://arxiv.org/abs/[@arxiv2508_03501]
- **[@arxiv2508_18462]** — VeriRL - Boosting LLM-based Verilog Code Generation via Reinforcement Learning. https://arxiv.org/abs/[@arxiv2508_18462]
- **[@arxiv2509_01142]** — Dream-Coder 7B - An Open Diffusion Language Model for Code. https://arxiv.org/abs/[@arxiv2509_01142]
- **[@arxiv2509_02360]** — Act Like You're Paying for This - Course-Correcting Code Agents with PRMs. https://arxiv.org/abs/[@arxiv2509_02360]
- **[@arxiv2509_09245]** — Jupiter - Enhancing LLM Data Analysis Capabilities via Notebook and Inference-Time Value-Guided Search. https://arxiv.org/abs/[@arxiv2509_09245]
- **[@arxiv2509_11686]** — Do Code Semantics Help - A Comprehensive Study on Execution Trace-Based Information for Code LLMs. https://arxiv.org/abs/[@arxiv2509_11686]
- **[@arxiv2509_14252]** — LLM-JEPA - Large Language Models Meet Joint Embedding Predictive Architectures. https://arxiv.org/abs/[@arxiv2509_14252]
- **[@arxiv2509_14646]** — SALT4Decompile - Inferring Source-level Abstract Logic Tree for LLM-Based Binary Decompilation. https://arxiv.org/abs/[@arxiv2509_14646]
- **[@arxiv2509_22114]** — SK2Decompile - LLM-Based Two-Phase Binary Decompilation. https://arxiv.org/abs/[@arxiv2509_22114]
- **[@arxiv2510_02387]** — CWM - An Open-Weights LLM for Research on Code Generation with World Models. https://arxiv.org/abs/[@arxiv2510_02387]
- **[@arxiv2510_02917]** — Mechanistic Interpretability of Code Correctness in LLMs via Sparse Autoencoders. https://arxiv.org/abs/[@arxiv2510_02917]
- **[@arxiv2510_03415]** — PLSemanticsBench - LLMs as Programming Language Interpreters. https://arxiv.org/abs/[@arxiv2510_03415]
- **[@arxiv2510_12635]** — Memory as Action - Autonomous Context Curation for Long-Horizon Agentic Tasks. https://arxiv.org/abs/[@arxiv2510_12635]
- **[@arxiv2510_14232]** — Scaling Test-Time Compute to Achieve IOI Gold Medal with Open-Weight Models. https://arxiv.org/abs/[@arxiv2510_14232]
- **[@arxiv2510_16732]** — A Comprehensive Survey on World Models for Embodied AI. https://arxiv.org/abs/[@arxiv2510_16732]
- **[@arxiv2510_18327]** — InspectCoder - Dynamic Analysis-Enabled Self Repair through Interactive LLM-Debugger Collaboration. https://arxiv.org/abs/[@arxiv2510_18327]
- **[@arxiv2510_21614]** — Huxley-Godel Machine - Human-Level Coding Agent Development. https://arxiv.org/abs/[@arxiv2510_21614]
- **[@arxiv2510_25015]** — VeriStruct - AI-assisted Automated Verification of Data-Structure Modules in Verus. https://arxiv.org/abs/[@arxiv2510_25015]
- **[@arxiv2511_17330]** — Agentic Program Verification. https://arxiv.org/abs/[@arxiv2511_17330]
- **[@arxiv2512_00215]** — Demystifying Errors in LLM Reasoning Traces - An Empirical Study of Code Execution Simulation. https://arxiv.org/abs/[@arxiv2512_00215]
- **[@arxiv2512_07404]** — On LLMs' Internal Representation of Code Correctness. https://arxiv.org/abs/[@arxiv2512_07404]
- **[@arxiv2512_10173]** — ATLAS - Automated Toolkit for Large-Scale Verified Code Synthesis. https://arxiv.org/abs/[@arxiv2512_10173]
- **[@arxiv2512_13821]** — The Double Life of Code World Models - Provably Unmasking Malicious Behavior Through Execution Traces. https://arxiv.org/abs/[@arxiv2512_13821]
- **[@arxiv2512_18552]** — Toward Training Superintelligent Software Agents through Self-Play SWE-RL. https://arxiv.org/abs/[@arxiv2512_18552]
- **[@arxiv2601_22249]** — FunPRM - Function-as-Step Process Reward Model with Meta Reward Correction for Code Generation. https://arxiv.org/abs/[@arxiv2601_22249]
- **[@arxiv2602_00785]** — World Models as an Intermediary between Agents and the Real World. https://arxiv.org/abs/[@arxiv2602_00785]
- **[@arxiv2602_03419]** — Nanbeige SWE-World - Building Software Engineering Agents in Docker-Free Environments. https://arxiv.org/abs/[@arxiv2602_03419]
- **[@arxiv2602_05842]** — Reinforcement World Model Learning for LLM-based Agents. https://arxiv.org/abs/[@arxiv2602_05842]
- **[@arxiv2602_07672]** — Debugging Code World Models. https://arxiv.org/abs/[@arxiv2602_07672]
- **[@arxiv2603_01896]** — Agentic Code Reasoning. https://arxiv.org/abs/[@arxiv2603_01896]
- **[@arxiv2603_09044]** — Synergistic Directed Execution and LLM-Driven Analysis for Zero-Day AI-Generated Malware Detection. https://arxiv.org/abs/[@arxiv2603_09044]
- **[@arxiv2603_09951]** — Towards a Neural Debugger for Python. https://arxiv.org/abs/[@arxiv2603_09951]
- **[@arxiv2603_11103]** — Understanding by Reconstruction - Reversing the Software Development Process for LLM Pretraining. https://arxiv.org/abs/[@arxiv2603_11103]
- **[@arxiv2603_11226]** — ExecVerify - White-Box RL with Verifiable Stepwise Rewards for Code Execution Reasoning. https://arxiv.org/abs/[@arxiv2603_11226]
- **[@arxiv2603_17399]** — Bootstrapping Coding Agents - The Specification Is the Program. https://arxiv.org/abs/[@arxiv2603_17399]
- **[@arxiv2604_03144]** — InCoder-32B-Thinking - Industrial Code World Model for Thinking. https://arxiv.org/abs/[@arxiv2604_03144]
- **[@arxiv2604_03253]** — Self-Execution Simulation. https://arxiv.org/abs/[@arxiv2604_03253]
- **[@arxiv2604_06425]** — Neural Computers. https://arxiv.org/abs/[@arxiv2604_06425]
- **[@arxiv2604_14820]** — SWE-TRACE - Optimizing Long-Horizon SWE Agents Through Rubric Process Reward Models and Heuristic Test-Time Scaling. https://arxiv.org/abs/[@arxiv2604_14820]
- **[@arxiv2604_17010]** — Improving LLM Code Reasoning via Semantic Equivalence Self-Play with Formal Verification. https://arxiv.org/abs/[@arxiv2604_17010]
- **[@arxiv2604_20926]** — Learning Reasoning World Models for Parallel Code. https://arxiv.org/abs/[@arxiv2604_20926]
- **[@arxiv2604_24198]** — DataPRM - Process-Level Reward Modeling for Agentic Data Analysis. https://arxiv.org/abs/[@arxiv2604_24198]
- **[@arxiv2605_05138]** — Executable World Models for ARC-AGI-3 in the Era of Coding Agents. https://arxiv.org/abs/[@arxiv2605_05138]
- **[@arxiv2605_11006]** — TraceEval - An Execution-Verified Multi-Language Benchmark for Code Semantic Reasoning. https://arxiv.org/abs/[@arxiv2605_11006]

---
