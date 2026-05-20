# A Comprehensive Survey of World Models for Coding

---

## Abstract

A *world model* is an internal predictor over environment dynamics. In coding, the environment is the program: its runtime state, execution trace, filesystem, tests, and developer task. The first attempt to learn such a predictor came from Zaremba and Sutskever (1410.4615), who trained an LSTM to predict Python execution output in 2014. Twelve years later, Meta FAIR released CWM (2510.02387), the first open-weights LLM branded a Code World Model.

This survey synthesizes nearly 200 papers spanning four research lineages: neural execution, trace pretraining and the CWM line, agentic software engineering with execution feedback, and verifier-grounded code generation. It traces a progression from static code representation (CodeBERT), to execution prediction, to agentic simulation, and argues that the next step is not merely more traces but latent, decision-relevant models of semantic consequences. The survey builds a taxonomy by functionality, temporal modeling, representation, grounding mode, and agentic capability level; assembles protocol-stratified empirical tables; and closes with open problems around causal isolation, world-model fidelity, Code-JEPA-style latent prediction, and self-revising agentic WMs.


---

## 1. Introduction

Autoregressive code LLMs generate tokens conditioned on syntactic context. Correct programs are objects in two domains: source tokens, and the values, control flow, side effects, and developer intent those tokens encode. The world-model framing comes from model-based reinforcement learning, where it names an internal predictor of environment dynamics. The hypothesis examined here: training on execution rather than only on source-token prediction reduces the gap between code that compiles and code that runs.

Two adjacent surveys cover non-overlapping ground. A Survey on LLMs for Code Generation (2406.00515) maps the code-LLM space without the world-model lens. Understanding World or Predicting Future (2411.14499) maps world models in general without the code lens. A Comprehensive Survey on World Models for Embodied AI (2510.16732) maps embodied world models but excludes the coding domain. The intersection, the subject of this document, has cohered only recently into a recognizable program.

Two additional precedents clarify what is new. CodeBERT (2002.08155) learned joint natural-language/programming-language representations before the field had a world-model vocabulary; it belongs to the *static representation* prehistory of code WMs. V-JEPA's lesson is complementary: useful world models need not reconstruct observations, but can predict abstract latent targets that omit irrelevant detail [@meta_vjepa_blog_2024]. Agentic World Modeling (2604.22748) generalizes the agent view into three capability levels — local predictors, multi-step simulators, and self-revising evolvers — which this survey adapts to code. Together these sources sharpen the thesis: code world modeling is moving from representing code, to predicting execution, to simulating and revising the semantic consequences of actions.

The broader question of whether language itself constitutes a world model has its own theoretical literature. From Word Models to World Models (2306.12672, MIT) argues that natural language can serve as a probabilistic language of thought from which world models are induced. LAW (2312.05230, UCSD) offers a position-paper unification of language models, agent models, and world models. Generative EmCom (2501.00226) takes the stronger view that LLMs decode society's collective world model. This survey treats these contributions as ambient theoretical context: code is a particularly clean test case for the language-as-world-model hypothesis, since code's execution provides ground truth that natural-language reasoning lacks.

---

## 2. Scope and Corpus

The survey covers 196 arxiv preprints at the intersection of world-model or state-tracking architectures and code generation, debugging, repair, or agentic coding. Pure vision world models (DreamerV1–V3, V-JEPA, Genie) appear only as cited precedent; pure code-LLM papers without a world-model angle are excluded except when they anchor the representation prehistory (CodeBERT). Date range: 2014 (Learning to Execute) through May 2026. The majority of the corpus dates from 2025 or later, reflecting the field's recent crystallization around the Code World Model framing.

Cross-tabulation across the two primary taxonomic axes:

| | What is modeled | | | |
|---|---:|---:|---:|---:|
| **Architectural form (§3.1)** | Variable values / traces | Env / repo state | Spec / intent | Adversarial |
| Definition D (data-side) | ~70 | ~30 | ~12 | ~6 |
| N1 (neural dynamics) | 0 | 0 | 0 | 0 |
| N2 (latent action) | 2 | 1 | 0 | 0 |
| N3 (synthesized simulator) | 4 | 2 | 1 | 0 |
| Verifier / PRM (related) | ~15 | ~10 | ~10 | ~5 |

Two facts dominate the table. First, the descriptive bucket (D) holds the majority of the corpus and concentrates on variable values and traces. Second, the N1 row contains zero code exemplars: no system in the corpus instantiates a Dreamer-style learned dynamics model for code. Reinforcement World Model Learning for LLM-based Agents (2602.05842) trains the N1 *objective* — action-conditioned next-state prediction with a semantic-alignment RL reward — but does so without an N1 *architecture* (no separate dynamics head, no latent recurrent state); we classify it as D-with-RL. §17 lists the architectural gap as an open problem.

---

## 3. Defining a World Model for Coding

Three properties distinguish a *code* world model from a generic one and explain why the design space for coding diverges from the vision-WM design space.

- **Executable ground truth.** The environment ships with a precise simulator: CPython, the Java VM, an SMT solver, a hardware verifier. The WM can be evaluated against this oracle at training time, which is rare for vision and impossible for natural-language reasoning.
- **Compact, observable state.** A program frame at a given line is a small structured object: local variables, the call stack, file handles. Pixel-space WMs needed compression because a frame is high-dimensional. Code WMs face the opposite question — whether to predict full state or to abstract it.
- **Source–trace duality.** Every executed trace corresponds to a piece of source, and every piece of source admits many traces. The two views are linked by the interpreter, so a WM for coding can be trained on either side or on their alignment.

These three properties explain why most current code WMs are token-space predictors over execution traces rather than latent-space rollouts: the simulator is free, state is small, and source–trace alignment supplies plentiful supervised pairs. They also explain why verifier-grounded systems form a distinct cluster: the ground-truth oracle replaces the learned WM entirely.

The literature uses *world model* in two distinct senses, which this survey separates.

### 3.1 Two definitions

**Definition D (descriptive, permissive).** A *world model for coding* is any code LLM whose training objective concretely encodes program semantics — execution traces, runtime state, environment feedback, or simulated outcomes — in addition to or instead of source-token prediction. This matches the field's current usage. Under D, CWM, TRACED, SemCoder, LLM-JEPA, DyMo, RLEF, and most papers in the corpus qualify as world models.

**Definition N (normative, strict).** A *world model for coding* is a system with an explicit, separable forward-prediction mechanism. N splits into three sub-types:

- **N1 — Neural dynamics model.** A learned `W : (state, action) → next_state` instantiated as a distinct architectural component with latent recurrent state, separate dynamics head, or inverse model. Dreamer-class. No code exemplar in the corpus.
- **N2 — Latent-action model.** A learned action abstraction over a base LLM, with the LLM serving as transition model in compressed action space, supporting rollout or tree search over latent actions. CoLA (2503.21383) provides the canonical example.
- **N3 — Synthesized executable simulator.** The world model is an executable program (Python, DSL, HTML) synthesized by an LLM and run against ground-truth transitions during planning. GIF-MCTS (2405.15383), WorldCoder, Executable WMs for ARC-AGI-3 (2605.05138). The GUI variant predicts the next mobile or desktop screen by emitting renderable web code rather than pixels — Code2World (2602.01576) and gWorld (2602.09856) instantiate this for Android and web interfaces respectively.

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

Definition D matches field usage; definition N captures architectural commitment. The two-definition framework keeps both readings available.

### 3.2 What is modeled

Orthogonal to D-vs-N, *what* a system models varies: variable values and stack frames (CWM, CodeExecutor); execution traces (NExT, SemCoder, TRACED); test outcomes (LEVER, RLEF); OS or web environment state (WebDreamer, Dyna-Think); repository state (RepoGraph); spec or developer intent (ATLAS, Re:Form); adversarial behavior (Double Life of CWMs). A system typically commits strongly to one or two of these.

CWM occupies an instructive position: behaviorally explicit (it emits stack frames) but architecturally implicit (a 32B Llama-class decoder with no separate dynamics head). SemCoder, NExT, and TRACED follow the same pattern.

### 3.3 Capability levels for code WMs

Agentic World Modeling (2604.22748) separates world models by capability level: **L1 Predictor**, **L2 Simulator**, and **L3 Evolver**. This hierarchy is useful because the D/N split asks *what architecture counts*, while the level split asks *what the model can do for an agent*.

| Level | General meaning | Code-WM specialization | Representative systems |
|---|---|---|---|
| **L1 Predictor** | Learns local one-step transitions | Predict next variable state, branch, line trace, test result, or screen diff | CodeExecutor, TRACED, CWM trace prediction, DyMo |
| **L2 Simulator** | Composes transitions into multi-step action-conditioned rollouts | Roll out candidate edits, commands, clicks, or synthesized simulators before acting | RAP, WebDreamer, GIF-MCTS, Dyna-Think |
| **L3 Evolver** | Revises its own model after prediction failure | Updates the scaffold, environment theory, memory, or learned simulator after execution falsifies it | Self-Execution Simulation, self-play SWE-RL, Darwin/Huxley-style agents |

This level taxonomy sharpens the empirical landscape. Most code WMs are **L1**: they predict traces or outcomes locally. A smaller set reaches **L2** by using predictions for planning. True **L3** systems are rare and usually revise the agent scaffold or training distribution rather than a cleanly separable world model. The frontier problem is therefore not simply "train a larger CWM"; it is to make execution failures update the model's future predictions.

---

## 4. Twelve Years of Code World Models

The lineage reads as a sequence of inheriting questions. Each era's answer dissolved the previous era's bottleneck and exposed the next.

```
                    LINEAGE 1                    LINEAGE 2                  LINEAGE 3
                    Neural execution             World models / RL          Code LLMs
                    ─────────────────            ─────────────────          ──────────

2014   ─┬─ Learning to Execute (1410.4615)
        │   LSTM seq2seq predicts program output
2015    │  Neural Programmer-Interpreters (1511.06279)
2017    │  Dynamic Neural Program Embedding (1711.07163)
2018    │                                    Ha & Schmidhuber (1803.10122)
2019    │  Neural Code Fusion (1906.07181)
2020   ─┴─ IPA-GNN (2010.12621) — interpreter-architectures stall
                ▼                                                              ▼
2021                                                              Codex (2107.03374)
              Show Your Work / Scratchpads (2112.00114) — intermediate compute
2022                                                              CodeRL (2207.01780)
2023      CodeExecutor (2305.05383) — first trace pretraining
          TRACED (2306.07487) — trace as auxiliary objective
          RAP (2305.14992) — LLM-as-world-model + MCTS                SWE-bench (2310.06770)
2024      NExT (2404.14662), SemCoder (2406.01006)                   SWE-agent (2405.15793)
          Gen. Code World Models via MCTS (2405.15383) ◆── name appears
          WebDreamer (2411.06559) ◆── Dreamer-for-web-agents          RLEF (2410.02089)
2025      DeepSeek-R1 (2501.12948) — reasoning-RL pivot               SWE-RL (2502.18449)
          CoLA (2503.21383) ◆── Dreamer-for-LLMs first concrete       LLM-JEPA (2509.14252)
          General Agents Contain WMs (2506.01622)                     CLEVER (2505.13938)
          CWM (2510.02387) ◆◆── the named open-weights artifact       ATLAS (2512.10173)
2026      Debugging CWMs (2602.07672) — follow-up era
          Industrial / Parallel CWMs (2604.03144, 2604.20926)
          Demystifying Errors in Traces (2512.00215)
          Executable WMs for ARC-AGI-3 (2605.05138)
                                                                ▼
                                                  the WM is now an artifact, not a hope
```

Diamond markers in the figure tag the moments where *world model* enters the name of the contribution.

**Pre-2020: can a network execute code?** Learning to Execute (1410.4615) trained an LSTM to predict Python output on bounded-loop programs. Neural Programmer-Interpreters (1511.06279) and Differentiable Forth built differentiable program counters. Dynamic Neural Program Embedding (1711.07163) embedded real interpreter traces. Neural Code Fusion (1906.07181) and IPA-GNN (2010.12621) used GNN attention as a program counter. By 2020 the answer was yes, but only with the interpreter encoded into architecture, which did not scale to real languages. Ha & Schmidhuber (1803.10122) had named the pattern for vision-RL; the coding community had not yet borrowed it.

**2020–2022: from static representation to execution supervision.** CodeBERT (2002.08155) marks the static-representation precursor: a bimodal NL–PL encoder trained to align source code and natural language, but not to predict runtime transitions. Codex (2107.03374) and MBPP (2108.07732) then made code generation a target. Scratchpads (2112.00114) showed a Transformer could predict program output when allowed to emit intermediate computation first, the Dynamic-NPE move at LLM scale, without architectural surgery. The transition from CodeBERT to Scratchpads is the transition from *representing* code to *mentally executing* it.

**2023: trace pretraining as a named recipe.** CodeExecutor (2305.05383) trained a Transformer to emit per-line state traces from source. TRACED (2306.07487) generalized this to a pretraining auxiliary. CRUXEval (2401.03065) provided the eval that became standard. In parallel, Reflexion (2303.11366) and Self-Debug (2304.05128) used execution feedback in-context, LEVER (2302.08468) used it during decoding, and RAP (2305.14992) ran MCTS over an LLM-as-world-model.

**2024: from models that simulate to agents that act.** SWE-bench (2310.06770) shifted the task to real GitHub repos. CodeAct (2402.01030), SWE-agent (2405.15793), NExT (2404.14662), RLEF (2410.02089), WebDreamer (2411.06559), and Generating Code World Models via MCTS (2405.15383, source of the name) define the agentic turn. The WM moved from weights to loop.

**2025: the CWM artifact.** DeepSeek-R1 (2501.12948) and SWE-RL (2502.18449) scaled reasoning-RL. CoLA (2503.21383) and LLM-JEPA (2509.14252) ported Dreamer- and JEPA-style ideas to LLMs. General Agents Contain World Models (2506.01622) provided the existence theorem. CWM (2510.02387), 32B open-weights, mid-trained on 5T tokens of Python traces plus 3M ForagerAgent trajectories, made the artifact downloadable.

**2026: stress-testing and broadening.** Debugging CWMs (2602.07672) and Demystifying Errors in LLM Reasoning Traces (2512.00215) catalog failures. Industrial CWM (2604.03144), Parallel-Code WMs (2604.20926), and Executable WMs for ARC-AGI-3 (2605.05138) generalize the recipe. Reinforcement World Model Learning (2602.05842) trains the WM rather than the policy.


---

## 5. Taxonomy: Three Axes of Code World Models

Three cuts at the taxonomy prove useful, and they complement each other. The first, a *lineage* cut, asks which research thread produced the system, and structures §§6–13. The second, more durable cut adapts the three-axis framework of Li et al. (2510.16732) to the code domain. The third imports the L1/L2/L3 capability hierarchy from Agentic World Modeling (2604.22748) and asks whether a system merely predicts, actually simulates, or revises itself after failed predictions. The lineage map follows; the three representation/temporal/functionality axes appear in §§5.1–5.3, and the capability levels appear in §3.3.

```
                        World Models for Coding
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
  Modeling Code             Modeling Agents          Modeling Tasks
        │                         │                         │
 §6 Foundations          §8 Web/OS/SWE agents       §13 Reasoning + memory
 §7 Trace pretraining    §9 Execution-grounded RL   §14 Verification + safety
 §7 CWM proper           §10 Planning & search       §14 Probing + interp
        │                         │                         │
        └─────────────── §11 JEPA / Dreamer ──────────────────┘
                          (latent-action gap)
                                  │
                       §12 Specialized domains
              (diffusion, decompilation, hardware, ARC)
                                  │
                          §15 Benchmarks
                                  │
                   §16 Empirical Landscape
                                  │

                                  │
                       §17 Open problems
```

Adjacent WM surveys converge on overlapping splits that the three-axis framework subsumes as projections. Ding et al. (2411.14499) split top-level by *implicit representation* vs *future prediction*. Agentic World Modeling (2604.22748) adds the orthogonal levels × laws view: L1/L2/L3 capabilities crossed with physical, digital, social, and scientific law regimes. JiahuaDong's awesome-list organizes by *paradigm*: RL-based, observation-generative, latent-space, object-centric. knightnemo's list surfaces *pixel vs mesh vs latent* as cross-cutting tags. The three axes — functionality, temporal modeling, and representation — capture the choices a system makes regardless of lineage; the L1/L2/L3 overlay captures how much of the agent loop the model can support.

### 5.1 Axis 1 — Functionality

- **Decision-coupled WMs** model only the slice of the world relevant to acting on it. CWM (2510.02387), RLEF (2410.02089), and WebDreamer (2411.06559) are decision-coupled. Their WMs exist to enable code generation, RL planning, or web navigation respectively. CWM does not predict global filesystem state; it predicts the next Python frame because the next action depends on it.
- **General-purpose WMs** model the environment without reference to a particular task. The general-agents-contain-world-models theorem (2506.01622) provides the abstract limit. In the corpus, only the largest CWM-class models with broad mid-training approach generality; most code world models are decision-coupled to a sub-task (repair, completion, agent control).

### 5.2 Axis 2 — Temporal Modeling

- **Sequential simulation/inference.** Step-by-step autoregressive rollout. CWM, NExT, SemCoder, all the trace-pretraining systems, and most LLM-as-WM planners (RAP, WebDreamer in its MPC loop) live here. The state updates one timestep at a time. The vision analog is RSSM (Hafner et al., DreamerV1–V3).
- **Global difference prediction.** Predict the entire future state at once, in parallel. The vision analog is video-diffusion or masked-JEPA. V-JEPA's important lesson is negative: the target need not be a pixel-perfect reconstruction; it can be a latent representation of what matters for future action [@meta_vjepa_blog_2024]. In code, this fits diffusion code models (DiffuCoder, 2506.20639; Dream-Coder 7B, 2509.01142), where the next state is sampled jointly rather than autoregressively, the specification-is-the-program framing (2603.17399), where the entire trace is the spec, and a still-missing Code-JEPA objective that masks traces, tests, or repository states and predicts latent semantic consequences rather than exact token strings.
- **Static, no-trace.** Some systems (SemCoder's static mode, the trace-free baselines in Do Code Semantics Help?) explicitly drop temporal modeling at inference, reducing to single-shot prediction.

### 5.3 Axis 3 — Representation

The WM literature has converged most strongly on this axis, and the code-WM literature remains most uneven on it. Adapting Li et al.'s four-category split (GLV / TFS / SLG / DRR) to code yields five classes, of which only two are well-populated.

| Class | Encodes the world as | Vision analog | Code exemplars |
|---|---|---|---|
| **Token Sequence (TS)** | Discrete or continuous token streams with execution traces, variable bindings, or rationales interleaved with source | Token-as-pixel (IRIS, TWM, Genie, Sora) | CWM (2510.02387), CodeExecutor (2305.05383), TRACED (2306.07487), NExT (2404.14662), SemCoder (2406.01006) — the dominant code-WM mode |
| **Global Latent Vector (GLV)** | A compact vector updated recurrently, encoding the entire program/agent state | RSSM (Hafner et al., DreamerV1–V3) | No clean exemplar. CoLA (2503.21383) introduces a learned action codebook but is otherwise a standard LLM, not RSSM-style |
| **Spatial / Structural Grid (SLG)** | A geometric or structural grid (BEV/voxel in vision; AST, call-graph, CFG in code) | OccWorld, DriveWorld | No exemplar. RepoGraph (2410.14684) uses a static dependency graph but does not predict over it as a WM |
| **Decomposed Object / Slot (DOR)** | Distinct persistent latent slots for objects in the world | SlotFormer and object-centric WMs | No exemplar. No code-WM models variables, scopes, or classes as discrete persistent slots |
| **Synthesized executable (N3)** | The world model *is* an executable program, synthesized rather than learned | (orthogonal to vision) | GIF-MCTS (2405.15383), WorldCoder, Executable WMs for ARC-AGI-3 (2605.05138) |

Verifiers (Lean, Dafny, Z3) and PRMs are intentionally absent from this table. A verifier is not a *representation* of the world; it is a grounding oracle over candidate artifacts. A PRM is a backward-looking critic, not a forward predictor. Both belong in §5.4 below.

**Three white spaces.** The Dreamer-style GLV, the object-centric DOR, and the spatial-grid SLG representations have not been instantiated for code, despite being mature for vision. §17 lists these as open problems. The object-centric and structural-grid gaps look more directly tractable than the Dreamer-style gap, because code's compact observable state (§3) reduces the pressure for latent compression that motivated RSSM in vision.

### 5.4 Grounding mode (orthogonal to representation)

A second classification asks how each system's predictions are validated. This analog of Li et al.'s reality column addresses the decoupling between WM-head accuracy and downstream task success that DyMo (2506.02918) exhibits (§8.1).

| Grounding mode | Definition | Code exemplars |
|---|---|---|
| None / self-report | Predictions never validated against ground truth | RAP (2305.14992), basic LLM-as-WM planners |
| Execution-grounded | Predictions checked against real interpreter / runtime | CWM (2510.02387), TRACED (2306.07487), NExT (2404.14662), SemCoder (2406.01006), RLEF (2410.02089) |
| Verifier-grounded | Outputs checked by Lean / Dafny / Verus / Rocq / Z3 | ATLAS (2512.10173), Re:Form (2507.16331), CLEVER (2505.13938), VeriStruct (2510.25015), AutoRocq (2511.17330) |
| Synthesized-simulator-checked | Synthesized world model checked against held-out transitions | GIF-MCTS (2405.15383), Executable WMs for ARC-AGI-3 (2605.05138) |
| Critic-grounded (not a WM) | Backward-looking value/quality score, no rollout | ExecVerify (2603.11226), SWE-PRM (2509.02360), ThinkPRM (2504.16828) — listed for contrast; these are critics, not forward predictors |

Grounding mode is orthogonal to the representation axis: a token-sequence representation can be execution-grounded (CWM) or self-report (RAP); an N3 synthesized-simulator can be checked against transitions (GIF-MCTS) or never validated.

---

## 6. Foundations: Neural Execution as Implicit World Modeling

CodeBERT (2002.08155) is the useful contrast case. It learned joint representations of natural language and programming language with masked-language modeling and replaced-token detection, and it made code search and code documentation tasks central. But it did not model execution dynamics: the program was a semantic artifact to embed, not an environment to roll forward. In hindsight, CodeBERT is the static representation prehistory of code world models.

Learning to Execute (Zaremba & Sutskever, 1410.4615) established both feasibility and brittleness. Show Your Work — Scratchpads (2112.00114) provided the pivotal contribution: by training a Transformer to emit intermediate computation states, the authors recovered much of the LSTM-era execution-prediction performance at scale, presaging the trace-pretraining lineage of §6. CRUXEval (2401.03065) and REval (2403.16437) provide the canonical execution-reasoning benchmarks. The lesson the field absorbed: *replacing* the interpreter with a neural network is harder than *augmenting* a transformer with interpreter-style supervision. Modern systems all take the latter path.

---

## 7. The Trace-Pretraining and CWM Lineage

### 7.1 Trace-pretraining as a recipe

CodeExecutor (2305.05383) trains a Transformer to simulate Python execution token-by-token. TRACED (2306.07487) adds dynamic-state supervision to a code-LLM pretraining mix. NExT (2404.14662) formats traces as natural-language rationales, letting a chat-style LLM reason about runtime behavior via chain-of-thought. SemCoder (2406.01006) generalizes to monologue reasoning linking source-text to execution state.

The 2025 wave consolidated and stress-tested the approach. What I cannot execute, I do not understand (2503.05703) trains and evaluates LLMs explicitly on traces with dynamic scratchpads, pushing Llama-3.1-8B from 37.8% to ~80% on CRUXEval-O. Code Execution as Grounded Supervision (2506.10343) repurposes line-by-line traces as verifiable CoT. Self-Execution Simulation (2604.03253) lets the model train on its own execution predictions. Demystifying Errors in LLM Reasoning Traces (2512.00215) audits where trace-trained LLMs fail. Do Code Semantics Help? (2509.11686) provides the most damaging paper in the lineage: a comprehensive ablation across DeepSeek-Coder, LLaMA-3, and Gemma-2 with five trace representations found that no single representation consistently improved code generation, and in 7 of 9 synthesis settings the no-trace baseline won or tied.

### 7.2 TRACED (2306.07487)

TRACED augments a RoBERTa/UnixCoder pre-training mix with two execution-grounded heads on top of standard MLM: per-line program-state classification (variable type and quantized value over 30 bins) and per-line execution coverage. Trained on ~121k C traces from CodeNet collected via gdb, it showed that quantized variable-value prediction works as an auxiliary signal; concrete values lose to discretized bins. On static execution estimation, full-path accuracy rose from UnixCoder's 63.7% to 71.6%, and downstream clone retrieval and defect detection improved modestly. The contribution: trace prediction as a pre-training side objective, not a separate model.


### 7.3 NExT (2404.14662)

NExT inlines execution traces into source as Python-style comments (`# (k) varA=...; varB=...`) and trains PaLM 2-L on (rationale, fix) candidates via STaR-style self-training: sample 32 candidates per problem, accept those that passed unit tests, SFT on the accepted set, repeat. After ten iterations Mbpp-R pass@1 climbed from 23.2% to 49.3% (+26.1 absolute). The result that matters most for the rest of the survey: NExT retains a +17 absolute gain (23 → 40.8) on Mbpp-R when traces are removed at inference, which makes it the clearest example of trace pretraining transferring to non-trace inference on a repair task.


### 7.4 SemCoder (2406.01006)

SemCoder formalizes monologue reasoning linking four code modalities — natural-language description, source, operational trace, and abstract input-invariant constraints — under a single NTP objective with rejection-sampled training data (the PYX corpus). Distinctive features: forward and backward monologues (NExT is forward-only), abstract-semantics constraints rather than concrete state at every step, and entirely static inference. SemCoder-1.3B reached CRUXEval-I/O 63.6/65.1 vs GPT-3.5-turbo's 50.3/59.0, and a monologue-format ablation beat Scratchpad and NExT.


### 7.5 CWM (2510.02387)

CWM is a 32B dense decoder-only Transformer with grouped-query attention, sliding-window blocks, and RoPE — architecturally Llama-class. What earns it the world-model name is the mid-training datamix: 5T tokens of Python observation-action traces (120M traced functions, 262k CodeContests traces, 70k repo-level traced commits, 75M natural-language rewrites) plus 3M ForagerAgent SWE trajectories from 10.2k Dockerized repositories. Tokens are formatted so next-token prediction *is* next-state prediction at line granularity. CWM reached 65.8% on SWE-bench Verified with test-time scaling (best@16 over 40 verifier-reranked samples) and 94.3% on CRUXEval-Output. Its second technical contribution is Activ, which uses GitHub Actions CI to scale executable repository images. CWM is behaviorally explicit (emits stack frames) but architecturally implicit (no separate dynamics head).


The 65.8% headline is not pure pass@1 but best-of-16 with verifier reranking. Pure pass@1 sits at approximately 53–55%. The trace-mid-training contribution is not causally isolated from the ForagerAgent-trajectory contribution or from the joint-RL contribution.



### 7.7 GIF-MCTS / Generating Code World Models via MCTS (2405.15383)

GIF-MCTS treats the world model itself as a Python program: an `Environment.step(s,a) → (s', r, done)` class synthesized by an LLM to match a small batch of pre-collected `(s, a, r, s', d)` transitions. MCTS over partial programs uses three action types (*generate* lines, *improve* full program given a failing transition, *fix* runtime/syntax errors), with reward equal to the fraction of transitions reproduced correctly. The synthesized world model, once compiled, runs 4–6 orders of magnitude faster than calling an LLM as world model. On APPS-Competition it reached 28.3% strict pass@20 (Llama-3-70B), beating WorldCoder's 25.1%. The conceptual contribution: search over candidate Python world-model programs rather than train a neural one.


---

## 8. World Models for Code Agents

Once an LLM acts as an agent in a non-trivial environment, the world-model question becomes whether the agent simulates the environment's response. Agentic World Modeling (2604.22748) calls software a **digital-law** regime: transitions are rule-governed, inspectable, and often exactly replayable, but the state space spans filesystems, GUIs, APIs, tests, and other agents. Three sub-environments dominate.

### 8.1 Web agents

Web Agents with World Models (2410.13232) systematizes the thread. DyMo / World Modeling Improves LM Agents (2506.02918) adds a next-state prediction head to function-calling agents and reports gains on BFCL-V2. The DyMo WM head reached 90–94% state-prediction accuracy while the underlying policy reached only 72.8% task success, which illustrates that WM-head accuracy and agent accuracy can decouple.

WebDreamer (2411.06559) treats the web as a POMDP in which the LLM imagines natural-language state-change descriptions for each candidate click, type, or select. A specialist Dreamer-7B (Qwen2-VL-7B fine-tuned on 3.1M synthesized (initial visual state, action, state-change) tuples from random walks over Common Crawl URLs) provides cheap rollouts. At inference, model-predictive control samples actions, scores simulated trajectories with GPT-4o on a 3-scale rubric, and executes the argmax. On VisualWebArena, Online-Mind2Web, and Mind2Web-Live, this beat the reactive baseline by +34/+42/+24% relative (≈+6–11 absolute) while running 4–5× faster than tree search. The bet: when actions are irreversible (forms, purchases), one-step MPC over an LLM-as-WM beats backtracking search.


### 8.2 OS / computer-use agents

Reinforcement World Model Learning for LLM-based Agents (2602.05842) and World Models as an Intermediary between Agents and the Real World (2602.00785) generalize the lens: a learned WM mediates between LLM and expensive environment.

Dyna-Think (2506.00320) trains a single Qwen2.5-32B to internalize world-model simulation inside its `<think>` block for OSWorld and WindowsAgentArena. Two stages: DIT (imitation learning on R1 traces cleaned to keep only WM-simulation text) and DDT (Dyna-Q-style joint training over three WM heads — next state, state-diff, critic-prediction — with rejection-sampled policy updates). On OSWorld BoN the 32B model reached 43.1, essentially matching DeepSeek-R1 at 685B with half the tokens. World-model accuracy correlated with task success at r=0.32 across models. Dyna-Think is the corpus's leading instance of policy and learned world model hosted in the same LLM.


### 8.3 SWE agents

SWE-bench (2310.06770) and SWE-Gym (2412.21139) defined the eval and training environment respectively. CodeAct (2402.01030) made the Python interpreter the unified action space. Reflexion (2303.11366) provided the earliest entry with episodic verbal RL. Nanbeige SWE-World (2602.03419) trains a learned Docker-free execution surrogate. Understanding by Reconstruction (2603.11103) reverses the development process to harvest agentic pretraining traces. SWE-TRACE (2604.14820) provides process-level reward modeling over trajectories. Self-Play SWE-RL (2512.18552) introduces adversarial bug-injection/repair self-play. Bootstrapping Coding Agents — The Specification Is the Program (2603.17399) reframes the SWE task itself as a programmatic spec.

The 2026 wave extended the environment side. Agent World Model (2602.10090, Snowflake AI Research) generates synthetic environments with executable transition dynamics, treating environment construction itself as a learned capability. CLI-Gym (2602.10999, Huawei) scales CLI-task generation by inverting environment histories rather than scripting tasks by hand. Self-Improving Error Diagnosis (2604.17658, Amazon Alexa AI) builds verified episodic memory from executable evidence without expert labels. These three target the agent's *training distribution*, not its policy or its WM directly.

The §16 empirical synthesis separates three regimes: execution-grounded open-weight model training (CWM, SWE-RL), execution-grounded agents with learned simulators (Nanbeige SWE-World), and scaffold evolution around closed-model executors (Darwin GM, Huxley GM). Under best-of-k or verifier-reranked protocols, several systems report 60–68% on SWE-bench Verified, but those numbers are not directly comparable to pass@1 model-training results, and the scaffold-evolved systems are not 32B open-weight world-model-trained — they run frontier closed models inside an evolved harness.

### 8.4 SDLC phase predicts which WM form pays off

The SWE-agent literature aggregates many phases of software development under one benchmark score. Decomposing by phase clarifies which world-model form each phase actually exercises.

- **Localization and plan** (pre-edit): predominantly retrieval and code-graph reasoning. RepoGraph (2410.14684) and Agentless (2407.01489) exemplify the phase. WM benefit is small because the agent does not yet simulate execution; retrieval quality dominates.
- **Edit generation**: where token-space trace-pretrained models help most. CWM, SWE-RL, and the entire §7 lineage land here.
- **Debug and test**: the phase where forward state prediction would matter most. The agent forms hypotheses about runtime behavior, queries the program to falsify them, and edits the candidate. NExT (2404.14662), InspectCoder (2510.18327), and Agentic Code Reasoning (2603.01896) cluster here. This phase is also where probe-style evaluation (§15.2) would be most informative, because the agent's belief state about runtime is observable.
- **Verify and deploy**: the verifier-grounded line (ATLAS, Re:Form, CLEVER) replaces the WM with a deterministic oracle.

Most SWE-bench gains over the past year accrued to edit-generation; debug-and-test remains the phase where forward-prediction commitments (§3.1 N1–N3) have the clearest mechanism to help and the weakest current evidence.

---

## 9. RL with Execution as the World Signal

The model-based-RL framing — the world model is what the policy plans over — has produced a clean lineage.

### 9.1 RLEF (2410.02089)

RLEF formulates iterative code synthesis as a POMDP. Actions are full code responses, observations are formatted public-test execution feedback, and rewards come from held-out private tests. Standard PPO with KL regularization and a 3-turn limit. Llama-3.1-70B+RLEF reached 37.5/40.1 pass@1 valid/test on CodeContests at budget 1@3 (vs 25.9/27.5 baseline), matching AlphaCodium-GPT-4 with 5 samples; at 10@100 it reached 54.5/54.5, surpassing the AlphaCode 41B+clustering baseline. Critically, a random-feedback ablation removed the entire gain, which isolates that the model learns to *use* execution feedback rather than just sample more.


### 9.2 SWE-RL (2502.18449)

SWE-RL applies GRPO to 273k high-quality PR seeds with a rule-based, continuous reward (`difflib.SequenceMatcher` similarity between predicted and oracle patch); no code execution at training time. Llama-3.3-70B fine-tuned this way (Llama3-SWE-RL-70B) hit 41.0% pass@1 on SWE-bench Verified with the Agentless Mini scaffold. The surprising result was OOD transfer: HumanEval+ 76.2→79.9, CRUXEval-O 61.9→75.5, MATH 70.9→73.7, while SFT on the same data *degraded* on these. Continuous reward beat discrete in ablation (34.8 vs 29.0 oracle-repair). The thesis: partial-credit similarity rewards on real PR patches induce reasoning patterns that transfer beyond the training distribution.


### 9.3 Process Reward Models

ExecVerify (2603.11226), SWE-PRM (2509.02360), DataPRM (2604.24198), and ThinkPRM (2504.16828) form a cluster where a critic over partial trajectories supplies the training signal. PRMs are not forward predictors; they complement WMs rather than replace them.

The 2026 wave scaled the verifier idea. Scaling Agentic Verifier (2602.04254, Qwen Team) trained a verifier that reasons about candidate-program behaviors and discovers counterexamples rather than just scoring tokens. V1 (2603.04304, Berkeley + Together AI + Mila) unifies generation and self-verification so the same model produces candidates and pairwise verification judgments. Both move PRMs closer to forward-prediction territory: the verifier now reasons about what the program *would do*, not only about whether a step *looks right*.

---

## 10. Planning and Search with Code World Models

### 10.1 RAP (2305.14992)

RAP frames reasoning as MCTS in a self-consistent MDP where the same frozen LLM serves as both policy and transition model. A state is a textual configuration (blocks layout, intermediate variables, current fact), an action is a step proposed by the LLM, and the transition is obtained by re-prompting. Rewards combine action likelihood, state confidence (majority voting), self-evaluation, and task heuristics. On Blocksworld 4-step, RAP@10 reached 0.86 with LLaMA-33B, surpassing GPT-4+CoT's 0.63 by 33% relative. The conceptual template — repurpose the LLM as both policy and transition model under MCTS — is what every later LLM-as-WM paper extends.


Tree of Thoughts (2305.10601), AlphaZero-like Tree Search for LLM Decoding (2309.17179), Tree Search for LM Agents (2407.01476), and Mastering Board Games by External/Internal Planning with LMs (2412.12119) develop the search frame. The last gives the most direct contemporary recipe for learned tree-search with LLM-as-WM, straightforwardly transferable to code.

The LLM-as-WM-for-planning line broadens further in 2024–2026. WALL-E (2410.07484) and its successor WALL-E 2.0 (2504.15785) align an LLM-based world model with environment dynamics through neurosymbolic rule learning and scene-graph augmentation, enabling MPC over text-described transitions. Agent Planning with World Knowledge Model (2405.14205) introduces a parametric world-knowledge model for global and local planning. Making LLMs into World Models (2409.12278) fine-tunes the LLM as a precondition and effect predictor over PDDL-style action schemas. Code World Models for General Game Playing (2510.04542, DeepMind) translates natural-language game rules into executable Python world models for MCTS, generalizing GIF-MCTS beyond fixed RL benchmarks. PriorZero (2605.12289) bridges LLM semantic priors and learned world models on Jericho and BabyAI. World Reasoning Arena (2603.25887) benchmarks action simulation, long-horizon forecasting, and simulative planning across LLM-as-WM systems.

### 10.2 Execution-conditioned generation

Execution Guided Line-by-Line Code Generation (2506.10948) uses classifier-free guidance to condition next-token prediction on candidate-runtime outcomes. Jupiter (2509.09245) formulates notebook state as MCTS nodes. REPL-Plan (2411.13826) reuses a REPL state pool across tasks. The substrate is well-developed for short-horizon code-gen, less so for long-horizon multi-file SWE.

---

## 11. JEPA, V-JEPA, Dreamer, and the Latent-Action Gap

LeCun's Joint Embedding Predictive Architecture (I-JEPA, 2301.08243) predicts in embedding space rather than pixel space. V-JEPA extends the same principle to video: predict abstract future representations, not every observation detail [@meta_vjepa_blog_2024]. The Dreamer family — Hafner et al.'s DreamerV1 (1912.01603), DreamerV2 (2010.02193), and DreamerV3 (2301.04104), built around the Recurrent State-Space Model — learns latent dynamics for control. Direct code analogues remain rare. Three ideas occupy the gap: LLM-JEPA, a proposed Code-JEPA objective, and CoLA's latent action search.

### 11.1 LLM-JEPA (2509.14252)

LLM-JEPA adds a joint-embedding predictive objective to standard NTP training, using (text, code) as the two JEPA views with the LLM's last-layer last-token hidden state as encoder and a tied-weights `[PRED]` token as predictor. The loss is `L_NTP(text) + λ · d(Pred(Enc(Text)), Enc(Code))` with cosine distance. On Llama-3.2-1B fine-tuned on NL-RX-SYNTH the gain was 57.3 → 71.5 (+14.2 absolute); on Spider, GSM8K, and HellaSwag the wins were smaller. The top-100 singular values of `Enc(Text) − Enc(Code)` collapsed by orders of magnitude, which indicates a low-rank text↔code mapping.


### 11.2 Code-JEPA as the missing bridge

The V-JEPA lesson transfers cleanly to code if "observation" is interpreted broadly. Exact trace reconstruction asks the model to predict every local variable value, call-stack detail, and string literal. A Code-JEPA objective would instead predict latent semantic targets: whether a branch condition flips, which invariant changes, which tests become newly reachable, which file-level dependency is affected, or which failure mode a patch introduces. The training recipe is straightforward: mask a slice of an execution trace, patch trajectory, repository graph, or test log; encode the visible program state and action; predict the hidden semantic embedding; and train the predictor against interpreter-, test-, or verifier-grounded targets. The evaluation should not ask "did the model reconstruct the trace verbatim?" but "does the latent prediction improve repair, localization, or planning under a fixed policy?"

This reframes the main CWM ablation question. If CWM-style trace training helps only because it teaches the model to copy detailed traces, the benefit should disappear under latent targets. If it helps because it teaches semantic consequence prediction, Code-JEPA should preserve or improve downstream gains while reducing irrelevant reconstruction burden.


### 11.3 CoLA (2503.21383)

CoLA replaces the 128k-token action space of an LLM with a small learned latent-action codebook. Three modules: a VQ-VAE-style inverse-dynamics model that infers latent action `aₜ` from `(x₁:t, xₜ₊₁)`; a language world model that inserts the chosen latent action into the LLM embedding stream and decodes the next token; and a policy `π(aₜ | x₁:t)` behavior-cloned from inverse-dynamics labels then RL-tuned. Action-level MCTS over the learned codebook (with a Double-DQN Q-function) reached Math-500 68.2 vs 63.0 baseline MCTS-Q. CoLA is the corpus's most direct Dreamer-for-LLMs instance: the action space is genuinely compressed, and rollout and search operate in that compressed space.


### 11.4 The gap

Despite CWM and dozens of LLM-as-world-model papers, no public Dreamer/RSSM-style latent-imagination world model has been trained for SWE agents. CWM rolls out in token space. CoLA is the closest concrete instance. UniZero (2406.10667) generalizes MuZero with transformers but is rarely instantiated on code. Genie (2402.15391) gives the vision-side template. JEPA for RL (2504.16591) extends the energy-based objective to RL.

Whether the gap matters is itself an open question. The vision-domain pressure that motivated Dreamer's RSSM design (pixel-space rollout cost) does not exist for code, where state is small and the simulator is available. The argument *for* latent imagination rests on inference-time speed and the action-space compression CoLA demonstrates, not on rollout cost per se.

---

## 12. Specialized Domains

**Diffusion code models.** DiffuCoder (2506.20639), Dream-Coder 7B (2509.01142). Iterative denoising accommodates plan-then-refine generation.

**Decompilation and cross-language.** SK2Decompile (2509.22114), SALT4Decompile (2509.14646). Translation as semantic-simulation task. EquiBench (2502.12466) supplies the equivalence eval.

**Hardware / RTL.** VeriRL (2508.18462), ChipSeek (2507.04736), and VeriCoder (2504.15659) form a cluster where the simulator is the world model. Hardware suits this approach because simulators are precise, fast, and deterministic, closer to Atari than to Python.

**ARC and abstract synthesis.** Executable World Models for ARC-AGI-3 (2605.05138) instantiates literal-WM-per-task: synthesize a Python world model verified against observations. SOAR (2507.14172) evolves programs over ARC. Darwin and Huxley Godel Machines (2505.22954, 2510.21614) close the self-improvement loop.

---

## 13. Reasoning, Process Rewards, Memory

**Long-CoT reasoning for code.** o1-Coder (2412.00154) replicates o1 with MCTS+RL. R1-Code-Interpreter (2505.21668) supplies the open SFT+RL recipe across 144 tasks. Scaling Test-Time Compute to Achieve IOI Gold Medal (2510.14232) shows open-weight gpt-oss-120b matching closed reasoning models via inference-time scaling.

Long-CoT reasoning amounts to mental execution: the chain-of-thought simulates the world model the network never explicitly trained. CWM-style explicit world modeling and R1-style reasoning are partial substitutes. Whether they compose multiplicatively remains open.

**Memory.** Episodic Memory is the Missing Piece for Long-Term LLM Agents (2502.06975) frames the gap. Memory as Action (2510.12635) treats memory operations as RL-learnable actions. RepoGraph (2410.14684) provides a durable repo-level dependency graph.

---

## 14. Verification, Probing, Safety

### 14.1 Formal verification

The verifier-grounded lineage is the only research direction in the corpus that does not rely on LLM self-report for correctness; the verifier provides ground truth.

ATLAS (2512.10173) provides the most thorough end-to-end pipeline in the corpus for scaling verified-code data. From TACO-verified (12.8k LeetCode-style problems with Python references and tests), ATLAS produced 2,751 verified Dafny programs decomposed into 19,385 training examples across six tasks (NL-to-Code, NL-to-Spec, Spec-to-Code, Spec-Repair, Impl-Repair, Proof-Infilling). Spec quality was filtered by three SMT-discharged lemma types: soundness, completeness-contradiction, and completeness-perturbation. Qwen-2.5-Coder-7B fine-tuned this way reached DafnyBench Pass@1 of 55.8% (from 32.4%) and DafnySynthesis Pass@5 of 65.8% (from 15.8%, surpassing GPT-4's 53.4). ATLAS does for verified Dafny what auto-formalization did for Lean theorems.


The cluster also includes Re:Form (2507.16331, Dafny+RL), CLEVER (2505.13938, Lean), VeriStruct (2510.25015, Verus), AutoRocq (2511.17330, Rocq), and Semantic Equivalence Self-Play with Formal Verification (2604.17010, Liquid Haskell).

CLEVER's ≤1/161 end-to-end Lean result is the most sobering number in the corpus: frontier models, with Lean type-checker access for self-verification, still fail on >99% of HumanEval-derived problems requiring joint spec and implementation verification. Understanding Formal Reasoning Failures in LLMs as Abstract Interpreters (2503.12686) supplies the diagnostic: when asked to reason in the style of formal abstract interpretation over 22 SV-COMP programs, all frontier reasoning models made systematic errors in widening, fixpoint termination, and join operations.

### 14.2 Symbolic execution and LLMs

AutoBug (2505.13452), SESpec (2506.09550), LLM-Sym (2409.09271), and Loop Invariant Generation via Reasoning LLMs + SMT (2508.00419) combine LLMs with concrete or symbolic engines. The unifying pattern: the LLM hypothesizes the world model; symbolic execution verifies or extends it.

### 14.3 Probing and mechanistic interpretability

Two questions drive this subsection: what do code LLMs internally represent about program state, and how do those representations relate to the older question of whether LLMs implicitly contain world models at all.

For code specifically, Mechanistic Interpretability of Code Correctness via SAEs (2510.02917) and On LLMs' Internal Representation of Code Correctness (2512.07404) find partial, brittle internal execution representations. The general-language probing literature reaches a similar conclusion across non-code domains. Revisiting the Othello World Model Hypothesis (2503.04421) re-evaluates emergent board representations across seven LMs and finds the effect smaller and more fragile than originally reported. Scaling Laws for State Dynamics in LLMs (2505.14892) measures how state-tracking accuracy degrades with state-space size. Do LLMs Build Spatial World Models? (2604.10690, IBM) probes Gemini, GPT-5, Claude, and DeepSeek on grid-maze navigation and finds spatial representations weaker than the models' surface fluency suggests. The Depth Ceiling (2604.06427, UCL) identifies a similar ceiling on latent planning depth in GPT-4o, Qwen3-32B, and GPT-5.4. Extracting Search Trees from LLM Reasoning Traces Reveals Myopic Planning (2605.06840, NYU) shows that LLM Connect-4 reasoning trees stay shallow even when prompted to plan deeply. Emergent Structured Representations (2602.07794, Fudan) localizes a conceptual subspace in middle layers that functions as an implicit world model.

Across these studies the pattern is consistent: LLMs hold useful but bounded internal representations of state and dynamics, and those representations break down at modest depth or state-space size.

### 14.4 Repair and debugging as world-model probing

Self-Debug (2304.05128), InspectCoder (2510.18327), Agent That Debugs — Dynamic State-Guided Vulnerability Repair (2504.07634), and Agentic Code Reasoning (2603.01896, semi-formal execution-path reasoning without running code) share a pattern: maintain a belief over program state, query the runtime to update the belief, act on the posterior — Bayesian world-modeling in everything but name.

### 14.5 Safety and malicious code

The Double Life of Code World Models (2512.13821) repurposes CWM-style trace predictions for malicious-behavior detection. CodeBreaker (2406.06822) provides the offensive analogue. Concolic Execution + LLM for Zero-Day Malware Detection (2603.09044) pairs path-prioritization with concrete execution.

---

## 15. Three Regimes of Evaluation for Code World Models

Benchmarks for code world models fall into three regimes that differ in what they actually measure. The distinction matters because most current evaluation conflates them, and the missing third regime is what would allow direct measurement of WM quality.

### 15.1 Endpoint evaluations (what the system produces)

Endpoint benchmarks score the system's final output against a held-out test. SWE-bench (2310.06770), HumanEval, MBPP, LiveCodeBench (2403.07974), and PyBench (2407.16732) all fit here. They measure end-to-end task success without isolating any internal capability. A system can score well on endpoint benchmarks by exploiting test-distribution shortcuts, by retrieving similar solutions, or by genuinely simulating program semantics; the score alone cannot distinguish these mechanisms. Current SWE-bench leaders all use endpoint evaluation, which is why §16.1 stratifies by protocol rather than ranking by score.

### 15.2 Process probes (what the system internally simulates)

Process probes hold the task fixed but require the system to surface intermediate state — execution traces, variable bindings, branch coverage. CRUXEval (2401.03065), REval (2403.16437), CRUXEval-X (2408.13001), TraceEval (2605.11006), and PLSemanticsBench (2510.03415) all fit here. EquiBench (2502.12466) and CodeARC (2503.23145) extend the regime to semantic equivalence. Process probes are the closest existing measurement of WM quality: they ask whether the model can simulate execution rather than just produce a final answer.

Demystifying Errors in LLM Reasoning Traces (2512.00215) exposed the limit of this regime. When DeepSeek-R1, o4-mini, Gemini 2.5 Flash, and Claude 4 were prompted to simulate execution and explain their reasoning, the produced traces contained errors clustered into nine categories: computation, indexing, control flow, skipped statements, native-API misvaluation, hallucination, input misreads, and others. Models with 85–98% accuracy on final-output prediction produced traces with systematic intermediate errors. Outcome accuracy decouples from process fidelity, which is the signature of a system that learned to predict outputs without faithfully simulating dynamics.

**ProgramBench (2605.03546)** sits between regimes. Meta FAIR and Princeton (the SWE-bench team) released it in May 2026; it asks whether language models can rebuild whole programs from scratch given only natural-language specifications, evaluated by behavioral equivalence. The behavioral-equivalence rubric is closer to a process probe than an endpoint score, because two programs can pass the same unit tests by accident but rebuilding implies semantic reconstruction.

### 15.3 Counterfactual probes (missing)

The third regime would hold the policy fixed and vary the world model. Concretely: take a fixed coding policy, swap in different trace-pretraining recipes or different forward-prediction heads, and measure the delta on both process and endpoint metrics. No current benchmark supports this protocol. CWM, TRACED, NExT, and SemCoder each report endpoint and process gains, but none isolates the WM contribution from the policy contribution, because the policy and the WM live in the same weights.

Closing the counterfactual regime requires either explicit forward-prediction modules (§3.1, N1–N3) that can be ablated independently of the policy, or matched-harness re-runs across the trace-pretraining lineage. A concrete experimental design: fix the Qwen-2.5-Coder-32B base, vary the trace-pretraining mixture across the recipes used by TRACED, NExT, SemCoder, and CWM, and measure CRUXEval and SWE-bench separately. The resulting two-dimensional table would allow a regression of process fidelity onto endpoint success.

---

## 16. Empirical Landscape

### 16.1 SWE-bench scoreboard

Protocols mix in SWE-bench reporting and are non-comparable across the obvious axes. The table below splits into three protocol classes; readers should compare within, not across, classes. **Training / Evaluation regime**: *Frozen-model scaffold* = no model training (agent loop around a frozen closed model); *EG-LLM SFT* = supervised fine-tune on agent trajectories; *EG-LLM + RL* = RL with execution rewards; *EG-agent + learned simulator* = SFT+RL plus a learned execution surrogate; *EG-LLM + trace mid-train + RL* = the CWM lineage; *Scaffold-evolved* = recursive scaffold/agent self-improvement around a frozen closed model. **WM-Arch** is reserved for systems with explicit transition/rollout machinery (N1/N2/N3 from §3); no row in this table qualifies.

**Table 16.1a — Single-sample resolution (pass@1 on Verified unless noted)**

|System|Base model|Bench|Pass@1|Regime|Source|
|---|---|---|---|---|---|
|SWE-agent|GPT-4 Turbo|full|12.5%|Frozen-model scaffold|2405.15793|
|AutoCodeRover|GPT-4|Lite|19.0%|Frozen-model scaffold|2404.05427|
|Agentless|GPT-4o|Lite|32.0%|Frozen-model scaffold|2407.01489|
|SWE-Gym|Qwen-2.5-Coder-32B|Verified|20.6%|EG-LLM SFT|2412.21139|
|Agent-RLVR (no RM)|Qwen-2.5-72B|Verified|22.4%|EG-LLM + RL|2506.11425|
|Long-Context Multi-Turn RL|Qwen-2.5-72B|Verified|39.0%|EG-LLM + RL|2508.03501|
|SWE-RL (Llama3-SWE-RL-70B)|Llama-3.3-70B|Verified|**41.0%**|EG-LLM + RL|2502.18449|
|Nanbeige SWE-World (RL)|Qwen-2.5-Coder-32B|Verified|55.0%|EG-agent + learned simulator|2602.03419|
|CWM|CWM-32B|Verified|*not directly reported* †|EG-LLM + trace mid-train + RL|2510.02387|

† The CWM paper does not report a pure pass@1 number under the standard protocol. The headline 65.8% in Table 16.1b is best@16 with verifier reranking. Inferred pass@1 from the paper's reported figures is approximately 53–55%, but this is an estimate from the survey authors, not a directly reported number, and is not placed in the main row.

**Table 16.1b — Best-of-k with verifier reranking / TTS**

|System|Base|Bench|Score|Sample budget|Source|
|---|---|---|---|---|---|
|Agent-RLVR + RM rerank|Qwen-2.5-72B|Verified|27.8%|rerank over multi-sample|2506.11425|
|Nanbeige SWE-World (TTS@8)|Qwen-2.5-Coder-32B|Verified|**68.2%**|best@8|2602.03419|
|CWM (TTS)|CWM-32B|Verified|**65.8%**|best@16 over 40 reranked|2510.02387|

**Table 16.1c — Scaffold-evolution and self-play around closed-model executors**

|System|Backbone executor|Bench|Score (start → end)|Note|Source|
|---|---|---|---|---|---|
|Darwin Godel Machine|Claude-3.5-Sonnet|Verified|20% → 50%|Scaffold evolves over 80 iterations|2505.22954|
|Huxley Godel Machine|GPT-5-mini|Verified (500)|— → 61.4%|Scaffold optimized for Verified-60|2510.21614|
|SICA|Claude-3.5-Sonnet + o3-mini|Verified (subset)|17% → 53%|Scaffold evolves; not a model-training method|2504.15228|

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

For under-trained ≤8B open-weights, trace pretraining delivered +15 to +42 absolute on CRUXEval-O. The Do Code Semantics Help? ablation (2509.11686) supplied the disconfirming evidence: across multiple backbones and five trace representations, no single representation consistently outperformed others, and several downstream tasks regressed under trace augmentation. The gain shrinks rapidly with base-model quality. Trace pretraining functions as a remedial intervention for weak code models. Whether frontier models still benefit remains unsettled.

### 16.3 Web/OS agents from WMs

|Paper|Benchmark|Base|With WM|Delta|Mechanism|
|---|---|---|---|---|---|
|WebDreamer (GPT-4o WM)|VisualWebArena|17.6%|23.6%|+34.1% rel (≈+6 abs)|LLM-as-WM + MPC|
|WebDreamer|Online-Mind2Web|26.0%|37.0%|+42.3% rel (≈+11 abs)|same|
|Dreamer-7B (trained WM)|VisualWebArena|base|+4.7 abs|—|trained WM|
|WMA (2410.13232)|WebArena|base|action-selection 52→70%|—|trained transition WM|
|Dyna-Think DDT (32B)|OSWorld BoN|RFT~28%|43.1%|≈+15 abs|Dyna-Q + WM head|
|Dyna-Think DDT|WindowsAgentArena|28.4%|34.9%|+6.5 abs|same|

WM gains on web/OS are real but quantitatively small (≤+5–10 absolute task success rate on most benchmarks), and partly confounded with the extra synthetic data the WM generates. DyMo's 90%+ state-prediction accuracy versus 72.8% task success rate exemplifies the decoupling: WM heads can be accurate without the agent being accurate.

### 16.4 Formal verification vs LLM-only

|System|Language|Benchmark|Baseline|With system|Source|
|---|---|---|---|---|---|
|ATLAS|Dafny|DafnyBench Pass@1|32.4%|**55.8%**|2512.10173|
|ATLAS|Dafny|DafnySynthesis Pass@5|15.8%|**65.8%** (>GPT-4 53.4)|2512.10173|
|CLEVER|Lean 4|161 problems end-to-end|best frontier|**≤1/161**|2505.13938|
|VeriStruct|Verus / Rust|11 modules|—|**99.2%** (128/129 fns)|2510.25015|
|AutoRocq|Rocq|math + verif lemmas|5 baselines|48.0% math / 30.9% verif|2511.17330|
|Semantic Equiv Self-Play|Liquid Haskell|EquiBench|base|+13.3 pp|2604.17010|

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

## 17. Open Problems

Seven problems where the literature is thinnest and the upside is largest:

**1. Causal isolation of trace-pretraining contributions.** Every claim of the form *this WM-trained model achieves X* should be paired with an ablation removing the WM component while holding training data and RL fixed. CWM in particular needs this. Without it, the headline numbers underdetermine whether the WM did the work.

**2. World-model fidelity as a first-class metric.** §15's eval gap is concrete: build a benchmark where holding policy fixed and varying WM quality causes measurable variation in planning quality, independent of downstream task. This benchmark would clarify the field more than any single new model.

**3. Hybrid neural-symbolic systems.** The verifier-grounded line (§14.1) leads on synthesis-from-spec but does not yet scale to end-to-end verified codegen from natural language. The natural integration is neural proposal, symbolic verification, with the verifier providing gradient-free correctness signal and the neural component providing proposals at scale. Differentiable surrogates of symbolic verifiers (Lean, Dafny, Rocq) that pass verifier-style gradients during training remain open.

**4. Code-JEPA: latent semantic prediction instead of trace reconstruction.** Current trace pretraining often asks the model to reproduce detailed observations. The V-JEPA analogy suggests a different target: predict the latent semantic consequence of an edit, command, or input while ignoring irrelevant trace detail. A concrete benchmark would mask test logs, execution slices, or repo-state deltas, train latent predictors, and measure whether they improve repair or planning under a fixed policy.

**5. Multi-modal WMs for coding.** GUI agents need pixel-level WMs (Neural Computers, 2604.06425, provides a first attempt). Tying pixel WMs to code-state WMs through a shared latent remains essentially unsolved.

**6. Long-horizon credit assignment with execution-grounded rewards.** PRMs (§9.3) provide trajectory-level critics but operate independently of forward prediction. The right structure for rewarding an agent across hundreds of execution-grounded steps remains open.

**7. World models of the developer, not just the program.** All current WMs model the machine. Few model the developer intent with comparable fidelity. ATLAS and Re:Form gesture in this direction by treating the spec as the WM. A full developer-intent WM would close the agentic loop.

Dreamer-for-SWE-agents is not listed as the field's largest gap. The pressure motivating that direction in vision — pixel-space rollout cost — does not transfer to code, where state is small and the simulator is free.

**Three under-explored representations.** The §5.3 taxonomy table flags three classes of representation, mature in vision-WM, that have no code-WM exemplar:

- *Global Latent Vector (Dreamer-style RSSM)* — discussed in §11. The Hafner et al. DreamerV1–V3 line proves the design space exists; whether it pays off for code is unsettled. Two existing systems supply the recipe components: LLM-JEPA (2509.14252) demonstrates a predictor head on top of an LLM trunk, and Reinforcement World Model Learning (2602.05842) demonstrates the action-conditioned next-state-prediction objective trained via semantic-alignment RL. Combining them — a JEPA predictor over execution-state embeddings, trained with RWML-style rewards against CPython ground truth — is the most concrete proposal for a code-N1.
- *Spatial / Structural Grid* — the analog of OccWorld / BEV for code would be a learned predictive grid over AST nodes, call-graph edges, or CFG states. RepoGraph (2410.14684) shows the static version is useful as agent state; the predictive version remains unexplored.
- *Decomposed Object / Slot (object-centric WMs)* — the analog for code would model variables, scopes, or classes as discrete persistent slots whose state propagates independently. No paper in the corpus instantiates this, despite obvious mappings (each variable is an object, each frame is a scene).

**From L1 to L3.** The Agentic World Modeling levels make the maturity gap explicit. CodeExecutor/TRACED/CWM-style models are mostly L1 predictors; WebDreamer, RAP, Dyna-Think, and GIF-MCTS are closer to L2 simulators; L3 evolvers remain mostly scaffold- or data-distribution self-improvers rather than self-revising world models. A decisive L3 code-WM benchmark would require persistent model revision after execution falsifies a prediction, followed by improved predictions on related future tasks.

The object-centric and structural-grid gaps look more genuine than the Dreamer one, because they exploit structure that code already has (objects = variables, grids = AST/CFG) rather than borrowing pressure from a domain (vision) where the structural assumptions differ.

---

## 18. Conclusion

Across the literature surveyed here, a single trajectory is visible: from static representation (CodeBERT), through neural execution (modeling the machine), through trace pretraining (modeling execution implicitly), to CWM and its descendants (modeling execution explicitly with a named artifact), to agentic SWE and RL (modeling the environment), to JEPA and latent-action models (modeling in compressed space), and on toward formal verification, probing, and safety (modeling reliably). What was a scattered set of insights in 2014 has by 2026 cohered into a recognizable research program with a recognizable artifact: the code world model.

The remaining work splits into three parts. The first is empirical: close the eval gap, isolate the causal contribution of WM-training, build hybrid neural-symbolic systems whose correctness is verifier-checkable rather than test-checkable. The second is architectural: move beyond observation reconstruction toward Code-JEPA-style latent semantic prediction and beyond L1 predictors toward L2/L3 simulators that update after execution falsifies them. The third is rhetorical: hold the term *world model* to a strict definition so the literature can distinguish architectural commitments from training-data choices, and resist the temptation to oversell extractability theorems and latent-imagination analogies whose premises do not transfer to code.

The opportunity is large precisely because the framework is now clear enough to identify what is missing. The work to do is the work this survey has tried to make visible.

---
