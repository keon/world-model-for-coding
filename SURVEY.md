# A Comprehensive Survey on World Models for Coding

*Synthesis draft · last updated 2026-05*

---

## Abstract

A *world model* is an internal predictor an agent maintains over the dynamics of its environment, used to imagine the consequences of actions. In coding, the environment is the program itself — its runtime state, its execution trace, the filesystem it manipulates, the tests it must satisfy, the developer task it is solving. Twelve years after Zaremba & Sutskever asked whether a network could execute code (1410.4615), and seven months after Meta FAIR released CWM (2510.02387) as the first openly-released LLM explicitly branded a Code World Model, the question has changed. It is no longer whether internal models of execution are necessary or learnable — both are settled — but whether the *named artifact* "code world model" is a structural commitment or a marketing label, whether trace pretraining buys what it claims, and whether the field's Dreamer-shaped vocabulary will survive when the empirical evidence comes in.

This survey synthesizes 183 papers around the world-model lens. We define the object of study; trace its twelve-year arc; build a four-axis taxonomy; produce technical system cards for thirteen representative systems; assemble cross-paper benchmark tables for SWE-bench, CRUXEval, web agents, and formal verification; develop seven critical theses where the field overclaims; and identify the open problems where new work would matter most. The single most defensible empirical claim is that *execution-grounded supervision improves code agents*; the single most defensible critical claim is that almost everything else the field says about world models for coding is, at this date, underdetermined by the evidence.

---

## 1. Introduction

Autoregressive code LLMs generate tokens conditioned on syntactic context. Correct programs, however, live in two worlds simultaneously: a *syntactic* world of tokens and a *semantic* world of values, control flow, side effects, and developer intent. A model that has learned only the first is a stylist; a model that has learned the second is a programmer. The world-model framing — imported from model-based reinforcement learning, where it names an internal predictor of environment dynamics used to imagine action outcomes — is the field's bet that the gap between stylist and programmer closes when the network has been trained on what code does rather than only on what code looks like.

Two adjacent surveys cover non-overlapping ground. **A Survey on LLMs for Code Generation** (2406.00515) maps the code-LLM space without the world-model lens. **Understanding World or Predicting Future** (2411.14499) maps world models in general without the code lens. The intersection — the subject of this document — has cohered only recently into a recognizable program.

We aim for three things at once: comprehensive coverage of the corpus, technical depth on the canonical systems, and an honest accounting of where the prevailing rhetoric outruns the evidence. The first two are owed to readers entering the field; the third is owed to those already in it.

---

## 2. Defining a World Model for Coding

> A **world model for coding** is a learned function `W : (state, action) → (next_state, observation)` whose state and action are drawn from a coding environment — program runtime state, source code, repository state, agent action history, or some structured abstraction thereof.

This admits four architecturally distinct flavors:

- **Explicit symbolic WMs** emit actual stack frames, variable bindings, or runtime values. CWM (2510.02387), CodeExecutor (2305.05383), NExT (2404.14662).
- **Latent WMs** predict environment dynamics in compressed embedding space without surfacing state tokens. CoLA (2503.21383), LLM-JEPA (2509.14252).
- **Generative environment WMs** synthesize an executable simulator of the task — the WM *is* the code it emits. Generating Code World Models with LLMs (2405.15383), Executable World Models for ARC-AGI-3 (2605.05138).
- **Implicit WMs in token policies** arise when a standard LLM is trained on objectives that indirectly encode semantics — execution-trace pretraining (TRACED, 2306.07487; SemCoder, 2406.01006) or execution-feedback RL (RLEF, 2410.02089). The world model lives in the weights rather than in any nameable head.

A pure code-LLM trained only on source-token prediction is **not** a world model under this definition; the same transformer trained additionally to predict execution traces *is*. The distinction is objective, not architecture. (We return to this distinction critically in §16: most "code world models" published in 2025–2026 are architecturally identical to standard LLMs, with the WM badge resting entirely on the training-data composition.)

A second axis — orthogonal to the four flavors — asks *what* is modeled. The corpus splits across variable values and stack frames; linear or branching traces; test outcomes; environment/OS/web state; repository state; developer task or specification; adversarial behavior. A given system typically commits strongly to one or two of these.

---

## 3. Twelve Years of Code World Models

The lineage is best understood as a sequence of inheriting questions. Each era's answer dissolved the previous era's bottleneck and exposed the next.

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
2026      Debugging CWMs (2602.07672) — critique era
          Industrial / Parallel CWMs (2604.03144, 2604.20926)
          Demystifying Errors in Traces (2512.00215)
          Executable WMs for ARC-AGI-3 (2605.05138)
                                                                ▼
                                                  the WM is now an artifact, not a hope
```

Diamonds (◆) mark moments where "world model" enters the *name* of the contribution.

**Pre-2020 — Can a network execute code?** Zaremba & Sutskever's **Learning to Execute** (1410.4615) handed an LSTM character-level Python and asked it to predict output. The model worked on straight-line programs with bounded loops, but only with a curated curriculum, and only because the LSTM's constant memory was just enough to simulate the interpreter when the interpreter ran in constant memory too. Everything that followed in this lineage tried to escape that curse. **Neural Programmer-Interpreters** (1511.06279) and the **Differentiable Forth Interpreter** built differentiable program counters and call stacks — the bet that the right architecture would close the gap. **Dynamic Neural Program Embedding** (1711.07163) made the inverse move: run the real interpreter, embed the resulting state traces. **Neural Code Fusion** (1906.07181) and **IPA-GNN** (2010.12621) extended the GNN-over-execution playbook to the point where attention played the role of the program counter. By 2020 the lineage had answered its question — yes, a neural network can play interpreter, but only when the interpreter is encoded into its architecture, and these architectures did not transfer to Python, C, or assembly at corpus scale. Ha & Schmidhuber's **World Models** paper (1803.10122) had already named for vision and RL exactly the pattern this lineage was reaching for. The vocabulary existed; the coding community had not yet borrowed it.

**2020–2022 — Can the network's training include execution?** The era's reframing was simple: instead of *can the network execute*, ask *can we train a normally-shaped Transformer on enough execution evidence that semantics seep into its weights*. **Codex** (2107.03374) and **MBPP** (2108.07732) made code generation a real engineering target. **Show Your Work / Scratchpads** (2112.00114) made the decisive move: a Transformer that could not predict a program's output could predict it perfectly if it was allowed to emit the intermediate computation first. Same trick Dynamic Neural Program Embedding had pulled, now at LLM scale, in token space, without architectural surgery. The dream of 2014–2020 was a cul-de-sac; the right move was to bake execution into training data, not architecture.

**2023 — Trace pretraining as a named recipe.** **CodeExecutor** (2305.05383) made the recipe explicit: mutate competitive-programming submissions, run them in a sandbox, capture per-line state tokens, train a transformer to emit the trace from source. **TRACED** (2306.07487) generalized this to a pretraining auxiliary that any code-LLM could absorb. **CRUXEval** (2401.03065) provided the canonical input/output-prediction benchmark and suddenly there was a number that captured "does this model understand what code does, as opposed to what code looks like." In parallel, **Reflexion** (2303.11366) and **Self-Debug** (2304.05128) showed that an LLM's mistakes could be fed back to itself as natural-language critiques, **LEVER** (2302.08468) used execution to verify candidate generations during decoding, and **RAP** (2305.14992) framed the LLM itself as a world model and ran MCTS over its imagined rollouts. The year's unifying insight: execution traces are an auxiliary objective, not a separate model.

**2024 — From models that simulate to agents that act.** **SWE-bench** (2310.06770) replaced "write a function that passes a unit test" with "fix a real GitHub issue in a real repository." **CodeAct** (2402.01030) claimed the agent's action space should be Python code itself. **SWE-agent** (2405.15793) shipped the harness. **NExT** (2404.14662) inlined traces into the agent loop. **RLEF** (2410.02089) fed execution outcomes back as RL rewards. **WebDreamer** (2411.06559) transplanted Dreamer-style imagination to digital agents. **Generating Code World Models via MCTS** (2405.15383) introduced the literal phrase "Code World Models." What unified the year was a structural shift in *where* the world model lives: in 2023 it lived in the weights, surfaced through trace prediction; in 2024 it lived in the loop, in the agent's behavior under environmental feedback.

**2025 — The CWM moment.** **DeepSeek-R1** (2501.12948) opened the year by showing that pure reasoning-RL on verifiable rewards could reach the frontier on math and code. **SWE-RL** (2502.18449) applied the same recipe to full SWE traces. **CoLA** (2503.21383) made the first concrete attempt at a Dreamer-for-LLMs: inverse-dynamics over latent actions, then RL over a learned codebook. **LLM-JEPA** (2509.14252) ported LeCun's joint-embedding predictive objective to language. **General Agents Contain World Models** (2506.01622) supplied a theorem: any agent satisfying a regret bound on goal-conditioned tasks must have learned a predictive model of its environment. Then in October, Meta FAIR released **CWM** (2510.02387) — a 32B open-weights model mid-trained on 5T tokens of Python execution traces and ForagerAgent trajectories from Dockerized repositories. The thing the 2014 LSTM was trying to be was now a downloadable checkpoint.

**2026 — Stress-testing and broadening.** With the artifact in hand, the field pivoted to critique and generalization. **Debugging Code World Models** (2602.07672) catalogs CWM's failures on long traces and string-state representation. **Demystifying Errors in LLM Reasoning Traces** (2512.00215) audits where trace-trained models hallucinate. **Industrial CWM** (2604.03144) and **Parallel-Code WMs** (2604.20926) generalize the recipe to Verilog/GPU and parallelism semantics. **Executable World Models for ARC-AGI-3** (2605.05138) brings the generative-environment flavor to abstract visual reasoning. **Reinforcement World Model Learning for LLM Agents** (2602.05842) flips the standard recipe by training the WM rather than the policy.

**The arc.** Across twelve years: *can a network execute code?* → *can a network's training include execution?* → *can an LLM agent simulate its environment?* → *is the world model a named artifact rather than a metaphor?* Each era's answer dissolved the previous bottleneck and exposed the next. Architecture gave way to data; data gave way to agency; agency gave way to artifacts. What was a half-philosophical question in 2014 — *does this network understand what code does* — became, in 2025, an operational one with an open-weights baseline. The field has not finished. The 2026 critique wave shows the artifact is brittle in ways the 2014 LSTM was never asked to be. But the trajectory is now legible.

---

## 4. Taxonomy

```
                        World Models for Coding
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
  Modeling Code             Modeling Agents          Modeling Tasks
        │                         │                         │
 §5 Foundations          §7 Web/OS/SWE agents       §12 Reasoning + memory
 §6 Trace pretraining    §8 Execution-grounded RL   §13 Verification + safety
 §6 CWM proper           §9 Planning & search       §13 Probing + interp
        │                         │                         │
        └─────────────── §10 JEPA / Dreamer ──────────────────┘
                          (latent-action gap)
                                  │
                       §11 Specialized domains
              (diffusion, decompilation, hardware, ARC)
                                  │
                          §14 Benchmarks
                                  │
                   §15 Empirical Landscape
                                  │
                  §16 Critical Perspectives
                                  │
                       §17 Open problems
```

---

## 5. Foundations: Neural Execution as Implicit World Modeling

Zaremba & Sutskever's **Learning to Execute** (1410.4615) established both feasibility and brittleness. **Show Your Work — Scratchpads** (2112.00114) is the hinge moment: by training a Transformer to emit intermediate computation states, the authors recovered much of the LSTM-era execution-prediction performance at scale, presaging the trace-pretraining lineage of §6. **CRUXEval** (2401.03065) and **REval** (2403.16437) provide the canonical execution-reasoning benchmarks. The lesson the field absorbed: *replacing* the interpreter with a neural network is harder than *augmenting* a transformer with interpreter-style supervision. Modern systems all take the latter path.

---

## 6. The Trace-Pretraining and CWM Lineage

### 6.1 Trace-pretraining as a recipe

**CodeExecutor** (2305.05383) trains a Transformer to simulate Python execution token-by-token. **TRACED** (2306.07487) adds dynamic-state supervision to a code-LLM pretraining mix. **NExT** (2404.14662) formats traces as natural-language rationales, letting a chat-style LLM reason about runtime behavior via chain-of-thought. **SemCoder** (2406.01006) generalizes to "monologue reasoning" linking source-text to execution state.

The 2025 wave consolidated and stress-tested the approach. **"What I cannot execute, I do not understand"** (2503.05703) trains and evaluates LLMs explicitly on traces with dynamic scratchpads, pushing Llama-3.1-8B from 37.8% to ~80% on CRUXEval-O. **Code Execution as Grounded Supervision** (2506.10343) repurposes line-by-line traces as verifiable CoT. **Self-Execution Simulation** (2604.03253) lets the model train on its own execution predictions. **Demystifying Errors in LLM Reasoning Traces** (2512.00215) audits where trace-trained LLMs fail. **"Do Code Semantics Help?"** (2509.11686) is the most damaging paper in the lineage: a comprehensive ablation across DeepSeek-Coder, LLaMA-3, and Gemma-2 with five trace representations finds that *no single representation consistently improves code generation*, and in 7 of 9 synthesis settings the no-trace baseline wins or ties.

### 6.2 Deep dive — TRACED (2306.07487)

| | |
|---|---|
| **What it models** | Per-line program state (concrete variable values quantized into 30 bins crossing data-type × value-range) and per-line execution coverage of a C program, statically predicted from source. |
| **Data** | CodeNet C subset: 1,805/1,900 problems, 121,319 training traces collected via `gdb` stepping through `-g -O0` builds. |
| **Architecture / objective** | RoBERTa-base initialized from UnixCoder. Three jointly-optimized heads on input `[CLS] e₁..eᵢ [SEP][SEP] c₁..cⱼ [SEP]`: MLM, per-variable program-state classification `(data_type, value_type, quantized_value)`, per-variable binary coverage. |
| **Headline results** | Static execution full-path accuracy 71.6% vs UnixCoder 63.7% (+12.4% relative); variable-value accuracy 89.2% vs 87.8%; POJ-104 clone-retrieval MAP@R 91.2 vs 89.5. |
| **Distinctive contribution** | First demonstration that *quantized* variable-value prediction is a viable pretraining signal — concrete values lose to discretized bins. |

### 6.3 Deep dive — NExT (2404.14662)

| | |
|---|---|
| **What it models** | Program execution as **inline-comment trace** appended to source: each statement annotated `# (k) varA=...; varB=...` capturing changed variables in execution order. |
| **Data** | Mbpp-R (10,047 train / 1,468 dev repair tasks built from incorrect LLM outputs on MBPP) and HumanEvalFix-Plus. Base model: PaLM 2-L. |
| **Training objective** | STaR-style self-training. Sample 32 (rationale, fix) candidates at T=0.8 from current model; filter by unit-test pass; SFT on accepted. Always restart from initial checkpoint each iteration. 10 iterations. |
| **Headline results** | Mbpp-R pass@1 23.2 → **49.3 (+26.1 abs)**; HumanEvalFix-Plus 32.2 → 42.5 (+10.3). Crucially, generalizes when traces are removed at test time (40.8 vs 23.2). |
| **Distinctive contribution** | Inline-comment trace format fits ~95% of MBPP into 2K window (vs ~60% for Scratchpad), and the trained model retains benefit even without traces at inference. |

### 6.4 Deep dive — SemCoder (2406.01006)

| | |
|---|---|
| **What it models** | Four jointly-trained semantics modalities: Approximate (NL docstring), Symbolic (source), Operational (execution effects), Abstract (input-invariant properties). |
| **Data** | PYX — synthetically curated, retried by generator until each sample executes; 4.3k decontaminated CodeContest problems for SemCoder-S. Base: DeepSeekCoder-6.7B-base. |
| **Training objective** | Standard NTP with loss on code + monologue tokens. **Forward monologue** verbalizes execution step-by-step (summarizing loop iterations rather than dumping every state). **Backward monologue** characterizes possible prior states given output (abstract constraints + concrete witness). Both rejection-sampled against ground-truth execution. |
| **Headline results** | HumanEval+ 79.3% / MBPP+ 79.9% / LCB-Lite 27.5% at 6.7B — beats GPT-3.5-turbo. CRUXEval-I 63.6 / CRUXEval-O 65.1 vs GPT-3.5-turbo 50.3 / 59.0. Monologue beats Scratchpad (48.8) and NExT (49.4) on CRUXEval-I: 61.8. |
| **Distinctive contribution** | Forward AND backward monologues (NExT is forward-only); abstract semantics constraints rather than concrete state at every step; entirely static at inference. |

### 6.5 Deep dive — CWM (2510.02387)

| | |
|---|---|
| **What it models** | Python interpreter state at the granularity of an *interpreter stack frame* (one observation–action pair per executed line), plus agentic SWE trajectories where actions are shell tool calls and observations are environment responses. |
| **Architecture** | 32B dense decoder-only Transformer with GQA, sliding-window blocks, RoPE — Llama-class. No separate dynamics head, no inverse model, no recurrent latent. |
| **Data composition** | Four-stage train: (i) 8T-token general pretraining at 8k ctx; (ii) **5T-token code-world-modeling mid-training at 131k ctx**: 120M traced Python functions, 262k CodeContests traces, ~70k repo-level traced commits, 75M natural-language trace rewrites, and **3M ForagerAgent trajectories from 10.2k Docker images / 3.15k repos** (55% issue-fix, 45% synthetic mutate-fix); (iii) 100B-token SFT at 32k; (iv) 172B-token joint RL at 131k. |
| **Trace format** | Per-line `<\|frame_sep\|>{locals JSON}<\|action_sep\|>{source line}` so that next-token prediction *is* next-state prediction at line granularity. |
| **Headline results** | **65.8% SWE-bench Verified with TTS** (best@16 over 40 verifier-reranked samples); 68.6% LiveCodeBench-v5; 94.3% CRUXEval-Output; competitive with much larger closed models. |
| **Distinctive contribution** | First open-weights model where line-level Python execution traces and large-scale (3M) agent–environment trajectories are mid-training data, not post-training data. Introduces *Activ* (using GitHub Actions CI for local image builds) to scale executable repository images. |

Important caveat (developed further in §16): the 65.8% headline is *not* pure pass@1 but best-of-16 with verifier reranking. Pure pass@1 is approximately 53–55%. The trace-mid-training contribution is not causally isolated from the ForagerAgent-trajectory contribution and from the joint-RL contribution. Without an ablation removing one while holding the others fixed, the "world model" component's causal role is unfalsifiable.

### 6.6 Direct descendants of CWM

- **Debugging Code World Models** (2602.07672) — probes where CWM fails on long traces and string state; finds long-horizon failures are dominated by *action hallucination*, not state-propagation error.
- **Learning Reasoning World Models for Parallel Code** (2604.20926) — predicts race conditions and profiling artifacts from parallel source.
- **Industrial CWM / InCoder-32B-Thinking** (2604.03144) — CWM recipe on Verilog and GPU execution traces.
- **The Double Life of Code World Models** (2512.13821) — CWM trace predictions repurposed for malicious-behavior detection.
- **Towards a Neural Debugger for Python** (2603.09951) — neural debugger as forward/inverse world model.
- **Neural Computers** (2604.06425) — video-model-style WMs of CLI/GUI runtime from I/O traces.
- **Generating Code World Models with LLMs Guided by MCTS** (2405.15383) — the WM is *the code itself*, synthesized by an LLM.
- **General Agents Contain World Models** (2506.01622) — proves that sufficiently competent goal-conditioned agents must contain extractable world models, under restrictive conditions discussed critically in §16.

### 6.7 Deep dive — GIF-MCTS / Generating Code World Models via MCTS (2405.15383)

| | |
|---|---|
| **What it models** | The world model itself is *Python code* — an `Environment.step(s,a) → (s', r, done)` class synthesized by an LLM to match a small set of pre-collected `(s, a, r, s', d)` transitions. |
| **Data** | **CWMB** benchmark — 18 RL environments (classic control, PyGame, MuJoCo) with NL descriptions and 5 random + 5 above-threshold demonstrations each. Plus APPS-Competition and RTFM. |
| **Algorithm** | Inference-time MCTS over partial programs with three action types: **generate** (append L=2 lines), **improve** (rewrite full program given failing transition), **fix** (repair runtime/syntax error). Reward = fraction of transitions correctly reproduced. |
| **Headline results** | APPS-Competition 28.3% pass@20 (Llama-3-70B), beating WorldCoder 25.1%. CWMB normalized return 0.76 vs WorldCoder 0.60. RTFM: GPT-4 reaches 1.00 accuracy. |
| **Distinctive contribution** | The world model *as code to be searched over*, not as a neural net to be trained. Once compiled and validated, runs 4–6 orders of magnitude faster than calling the LLM as WM. |

---

## 7. World Models for Code Agents

Once an LLM is an *agent* taking actions in a non-trivial environment, the world-model question becomes whether the agent simulates the environment's response. Three sub-environments dominate.

### 7.1 Web agents

**Web Agents with World Models** (2410.13232) systematizes the thread. **DyMo / World Modeling Improves LM Agents** (2506.02918) adds a next-state prediction head to function-calling agents and reports gains on BFCL-V2 — though with a caveat (§16): the WM head reaches 90–94% state-prediction accuracy while the underlying policy reaches only 72.8% task success, illustrating that WM-head accuracy and agent accuracy can decouple.

#### Deep dive — WebDreamer (2411.06559)

| | |
|---|---|
| **What it models** | Web environment as a POMDP where the LLM imagines natural-language state-change descriptions for each candidate action. |
| **Data** | **3.1M synthesized web-interaction instances** from Common Crawl URLs via biased random walking; state changes captured as before/after VLM screenshots described by Qwen2-VL-72B. |
| **Training** | Dreamer-7B trained from Qwen2-VL-7B on `(initial state, action) → state-change description`. Horizon H=1 empirically optimal. |
| **Planning** | Model Predictive Control — simulate each candidate action, GPT-4o scores trajectories on a 3-scale rubric, argmax executes. |
| **Headline results** | VisualWebArena 23.6 vs reactive 17.6 (+34.1% rel); Online-Mind2Web 37.0 vs 26.0 (+42.3% rel); Mind2Web-Live 25.0 vs 20.2 (+23.8% rel). **4-5× more efficient than tree search**. Dreamer-7B specialist ≈ GPT-4o on online benchmarks. |
| **Distinctive contribution** | First open demonstration that LLM-as-WM + 1-step MPC beats tree search on web tasks where irreversibility makes backtracking infeasible. |

### 7.2 OS / computer-use agents

**Reinforcement World Model Learning for LLM-based Agents** (2602.05842) and **World Models as an Intermediary between Agents and the Real World** (2602.00785) generalize the lens: a learned WM mediates between LLM and expensive environment.

#### Deep dive — Dyna-Think (2506.00320)

| | |
|---|---|
| **What it models** | A single Qwen2.5-32B that internalizes world-model simulation inside its `<think>` block — predicting next observation, action critique, or state-difference — for computer-use agents. |
| **Training** | **DIT** (imitation learning): few-shot prompt GPT-4o to reconstruct DeepSeek-R1's CoT keeping only WM-simulation-related text; SFT on cleaned trace. **DDT** (Dyna-style RL): online rollouts feed three WM objectives — next-state, state-diff, critic — jointly with rejection-sampled policy training. |
| **Headline results** | OSWorld BoN All 43.1 (DDT, 32B) vs R1-685B 44.8 — **matches 685B model at 5% of parameters and 2× fewer tokens**. WindowsAgentArena 34.9 vs Qwen2.5-32B 23.9 / R1 26.9. World-model accuracy correlates with task success at r=0.32 across models. |
| **Distinctive contribution** | First Dyna-Q-style integration where a single LLM hosts both policy and world model with critique-prediction as the WM objective. |

### 7.3 SWE agents

**SWE-bench** (2310.06770) and **SWE-Gym** (2412.21139) defined the eval and training environment respectively. **CodeAct** (2402.01030) made the Python interpreter the unified action space. **Reflexion** (2303.11366) was the earliest entry with episodic verbal RL. **Nanbeige SWE-World** (2602.03419) trains a learned Docker-free execution surrogate. **Understanding by Reconstruction** (2603.11103) reverses the development process to harvest agentic pretraining traces. **SWE-TRACE** (2604.14820) provides process-level reward modeling over trajectories. **Self-Play SWE-RL** (2512.18552) introduces adversarial bug-injection/repair self-play. **Bootstrapping Coding Agents — The Specification Is the Program** (2603.17399) reframes the SWE task itself as a programmatic spec.

The §15 empirical synthesis assembles a cross-cutting SWE-bench scoreboard. Headline: open-weight world-model-trained 32B systems (CWM, Nanbeige SWE-World, Huxley GM) now reach 60–68% on SWE-bench Verified, competitive with frontier closed-model scaffold-only systems at far smaller parameter counts.

---

## 8. RL with Execution as the World Signal

The model-based-RL framing — world model is what the policy plans over — has produced a clean lineage.

### 8.1 Deep dive — RLEF (2410.02089)

| | |
|---|---|
| **What it models** | Iterative code synthesis as a POMDP — actions are full code responses, observations are formatted public-test execution feedback, rewards come from held-out private tests. |
| **Data** | CodeContests train (13,328 problems, 669 discarded for missing tests). Initial policies Llama-3.0/3.1-Instruct 8B / 70B. |
| **Objective** | PPO with `R(s,a) = r(s,a) − β · log π(aₜ|cₜ)/ρ(aₜ|cₜ)`. r = +1 if all tests pass, −1 if any fail, −0.2 for malformed output. Turn limit 3. Geometric-mean response probability for KL bias correction. |
| **Headline results** | Llama-3.1-70B + RLEF: **37.5 / 40.1 valid/test pass@1 with budget 1@3** (vs 25.9 / 27.5 baseline). 54.5 / 54.5 at 10@100, surpassing AlphaCode 41B+clustering. Transfers to HumanEval+ (78.6 → 80.4) and MBPP+. Random-feedback ablation removes all gain. |
| **Distinctive contribution** | First clean demonstration that standard PPO on multi-turn execution feedback beats both SFT and few-shot for code agents; isolates that the model learns to *use* feedback, not just sample more. |

### 8.2 Deep dive — SWE-RL (2502.18449)

| | |
|---|---|
| **What it models** | Bug-fix as single-shot search/replace edit conditioned on issue + full file context. *No execution at training time*. |
| **Data** | 273k high-quality PR seeds extracted from a raw GitHub PR corpus. Trained on Llama-3.3-70B-Instruct. |
| **Objective** | **GRPO** with rule-based reward `R(o) = compare(patch_pred, patch_gt)` via `difflib.SequenceMatcher` (continuous 0..1). −1 for format violations. Continuous reward beats discrete in ablation (34.8 vs 29.0 oracle-repair). |
| **Headline results** | **41.0% SWE-bench Verified pass@1** with Agentless Mini scaffold. OOD: HumanEval+ 76.2 → 79.9; CRUXEval-O 61.9 → 75.5; MATH 70.9 → 73.7 — *SFT degrades on these while RL improves*. |
| **Distinctive contribution** | Continuous-similarity reward on PR patches without execution induces emergent self-reflection, multi-approach exploration, and divide-and-conquer reasoning that transfers OOD. The "world model" is implicit in the patch-similarity reward. |

### 8.3 Process Reward Models

**ExecVerify** (2603.11226), **SWE-PRM** (2509.02360), **DataPRM** (2604.24198), **ThinkPRM** (2504.16828) form a cluster where the WM is a learned *evaluator* of partial trajectories. As §16 develops critically, this is not the same object as a forward world model — PRMs are critics with execution grounding. They cannot roll out, cannot simulate counterfactuals. Survey hygiene argues for keeping the distinction.

---

## 9. Planning and Search with Code World Models

### 9.1 Deep dive — RAP (2305.14992)

| | |
|---|---|
| **What it models** | Generic reasoning MDP — state = textual configuration, action = step proposed by the same LLM, transition obtained by re-prompting the LLM as world model. |
| **Method** | MCTS-UCT over the reasoning tree. Rewards: action likelihood, state confidence (majority voting), self-evaluation (LLM "Is this correct?" probability), task heuristics. |
| **Headline results** | Blocksworld 4-step: RAP@10 = 0.86 (LLaMA-33B) vs CoT-pass@10 = 0.07 vs GPT-4+CoT = 0.63. **LLaMA-33B+RAP beats GPT-4+CoT by 33% relative on plan generation.** GSM8K: 51.6 (RAP+aggr) vs CoT+SC 46.8. |
| **Distinctive contribution** | Earliest clean formulation that repurposes the LLM as both policy and transition model under MCTS. The template every later "LLM-as-WM" paper extends. |

**Tree of Thoughts** (2305.10601), **AlphaZero-like Tree Search for LLM Decoding** (2309.17179), **Tree Search for LM Agents** (2407.01476), and **Mastering Board Games by External/Internal Planning with LMs** (2412.12119) develop the search frame; the last gives the clearest contemporary recipe for learned tree-search with LLM-as-WM, straightforwardly transferable to code.

### 9.2 Execution-conditioned generation

**Execution Guided Line-by-Line Code Generation** (2506.10948) uses classifier-free guidance to condition next-token prediction on candidate-runtime outcomes. **Jupiter** (2509.09245) formulates notebook state as MCTS nodes. **REPL-Plan** (2411.13826) reuses a REPL state pool across tasks. Substrate is well-developed for short-horizon code-gen; less so for long-horizon multi-file SWE.

---

## 10. JEPA, Dreamer, and the Latent-Action Gap

LeCun's **Joint Embedding Predictive Architecture** (I-JEPA, 2301.08243) predicts in embedding space rather than pixel space. The Dreamer family (RSSM, latent imagination) has near-zero direct application to code. Two papers occupy the gap.

### 10.1 Deep dive — LLM-JEPA (2509.14252)

| | |
|---|---|
| **What it models** | A *joint embedding* between two views of the same knowledge — Text (NL prompt) and Code (e.g., SQL). Not a temporal world model; an embedding-space abstraction objective. |
| **Architecture** | Predictor is **tied-weights**: a single `[PRED]` token (with K predictor tokens) is appended and the LLM re-runs to produce `Pred(Enc(·))`. A custom block-causal attention mask lets both views go through a single forward pass. |
| **Objective** | `L = Σₜ L_NTP(text) + λ · d(Pred(Enc(Text)), Enc(Code))`. d = cosine. Encoder reuses last-layer last-token hidden state. |
| **Headline results** | Llama-3.2-1B on NL-RX-SYNTH FT: 71.46% vs 57.29% NTP-FT (+14.2). Spider: ~50% vs ~47%. GSM8K: ~32% vs ~32%. Top-100 singular values of `Enc(Text) − Enc(Code)` collapse by orders of magnitude. |
| **Distinctive contribution** | First JEPA-style embedding-space objective added to a generative LLM that preserves NTP loss while inducing low-rank Text↔Code mapping. Critical question (§16): is this really JEPA in the LeCun sense, or a regularizer on LM training? |

### 10.2 Deep dive — CoLA (2503.21383)

| | |
|---|---|
| **What it models** | An MDP over text where the LLM is the transition model and actions are discrete *latent* tokens from a learned codebook, not vocabulary tokens. |
| **Data** | Llama-3.1-8B base, continued-pretrained on 200GB from SlimPajama / StarCoder / Proof-Pile-2 / WuDao; policy trained on 100GB subset. |
| **Three modules** | Inverse-Dynamics Model `f_inverse(x₁:t, xₜ₊₁) → aₜ` implemented as VQ-VAE-style encoder with codebook C. Language World Model inserts the chosen latent action into the LLM embedding stream and decodes the next token. Policy π(aₜ|x₁:t) is then behavior-cloned then RL-tuned. |
| **Planning** | Action-level MCTS over latent-action subtrees. MCTS-Q variant uses Double-DQN over (prompt, response, reward) tuples. |
| **Headline results** | Math-500: 42.4 (CoLA+RL) vs 38.2 baseline. **MCTS-Q on Math-500: 68.2 vs 63.0 baseline MCTS-Q.** +11% averaged on math reasoning; 64% win rate on alignment. |
| **Distinctive contribution** | First system to *replace* the 128k token-level action space of an LLM with a small learned latent-action codebook for RL — making the action space tractable for tree search. |

### 10.3 The gap

Despite CWM and dozens of LLM-as-world-model papers, *no public Dreamer/RSSM-style latent-imagination world model has been trained for SWE agents*. CWM rolls out in token space. CoLA is the closest concrete instance. **UniZero** (2406.10667) generalizes MuZero with transformers but is rarely instantiated on code. **Genie** (2402.15391) gives the vision-side template. **JEPA for RL** (2504.16591) extends the energy-based objective to RL.

Whether the gap matters is a live question developed critically in §16. The vision-domain pressure that motivated Dreamer's RSSM design (pixel-space rollout cost) does not exist for code, where state is small and the simulator is available. The argument *for* latent imagination rests on inference-time speed and the action-space compression CoLA demonstrates, not on rollout cost per se.

---

## 11. Specialized Domains

**Diffusion code models.** DiffuCoder (2506.20639), Dream-Coder 7B (2509.01142). Iterative denoising naturally accommodates plan-then-refine generation.

**Decompilation and cross-language.** SK2Decompile (2509.22114), SALT4Decompile (2509.14646). Translation as semantic-simulation task. EquiBench (2502.12466) supplies the equivalence eval.

**Hardware / RTL.** VeriRL (2508.18462), ChipSeek (2507.04736), VeriCoder (2504.15659) form a cluster where the simulator is the world model. Hardware is an attractive domain because simulators are precise, fast, and deterministic — closer to Atari than to Python.

**ARC and abstract synthesis.** Executable World Models for ARC-AGI-3 (2605.05138) instantiates literal-WM-per-task: synthesize a Python world model verified against observations. SOAR (2507.14172) evolves programs over ARC. Darwin / Huxley Godel Machines (2505.22954, 2510.21614) close the self-improvement loop.

---

## 12. Reasoning, Process Rewards, Memory

**Long-CoT reasoning for code.** o1-Coder (2412.00154) replicates o1 with MCTS+RL. R1-Code-Interpreter (2505.21668) supplies the open SFT+RL recipe across 144 tasks. **Scaling Test-Time Compute to Achieve IOI Gold Medal** (2510.14232) shows open-weight gpt-oss-120b matching closed reasoning models via inference-time scaling.

Long-CoT reasoning is *mental execution* — the chain-of-thought simulates the world model the network never explicitly trained. CWM-style explicit world modeling and R1-style reasoning are partial substitutes; whether they compose multiplicatively is open.

**Memory.** **Episodic Memory is the Missing Piece for Long-Term LLM Agents** (2502.06975) frames the gap. **Memory as Action** (2510.12635) treats memory operations as RL-learnable actions. **RepoGraph** (2410.14684) provides a durable repo-level dependency graph.

---

## 13. Verification, Probing, Safety

### 13.1 Formal verification: the leading edge

The verifier-grounded lineage is the only research direction in the corpus that does not rely on LLM self-report for correctness — the verifier provides ground truth.

#### Deep dive — ATLAS (2512.10173)

| | |
|---|---|
| **What it models** | Verifier-grounded synthesis of Dafny programs (specification + implementation + proof annotations) from NL + Python reference + tests. |
| **Data** | TACO-verified yields 2,751 verified Dafny programs decomposed into 19,385 training examples across 6 tasks: NL-to-Code, NL-to-Spec, Spec-to-Code, Spec-Repair, Impl-Repair, Proof-Infilling. Base: Qwen-2.5-Coder-7B + LoRA. |
| **Spec quality** | Three lemma types: **Soundness** (contract holds on test inputs), **Completeness-Contradiction** (negated output → false), **Completeness-Perturbation** (contract rejects structurally perturbed outputs). |
| **Headline results** | **DafnyBench Pass@1: 32.4 → 55.8 (+23.4); Pass@10 → 56.9.** **DafnySynthesis Pass@5: 15.8 → 65.8 (+50)**, surpassing GPT-4 (53.4) by 12.4 points at 7B. |
| **Distinctive contribution** | First end-to-end pipeline for scaling verified-code data the way auto-formalization scaled Lean theorems. Operational soundness/completeness criteria via SMT-discharged lemmas filter degenerate specs. |

The cluster also includes **Re:Form** (2507.16331, Dafny+RL), **CLEVER** (2505.13938, Lean), **VeriStruct** (2510.25015, Verus), **AutoRocq** (2511.17330, Rocq), and **Semantic Equivalence Self-Play with Formal Verification** (2604.17010, Liquid Haskell).

CLEVER's ≤1/161 end-to-end Lean result is the most sobering number in the corpus: frontier models, with Lean type-checker access for self-verification, still fail on >99% of HumanEval-derived problems requiring joint spec + implementation verification. **Understanding Formal Reasoning Failures in LLMs as Abstract Interpreters** (2503.12686) is the diagnostic: when asked to reason in the style of formal abstract interpretation over 22 SV-COMP programs, all frontier reasoning models make systematic errors in widening, fixpoint termination, and join operations.

### 13.2 Symbolic execution and LLMs

**AutoBug** (2505.13452), **SESpec** (2506.09550), **LLM-Sym** (2409.09271), **Loop Invariant Generation via Reasoning LLMs + SMT** (2508.00419) combine LLMs with concrete or symbolic engines. The unifying pattern: the LLM hypothesizes the world model; symbolic execution verifies or extends it.

### 13.3 Probing and mechanistic interpretability

**Mechanistic Interpretability of Code Correctness via SAEs** (2510.02917) and **On LLMs' Internal Representation of Code Correctness** (2512.07404) ask what code LLMs actually represent. Findings: *partial, brittle* internal execution representations — a vindication of explicit trace pretraining.

### 13.4 Repair and debugging as world-model probing

**Self-Debug** (2304.05128), **InspectCoder** (2510.18327), **Agent That Debugs — Dynamic State-Guided Vulnerability Repair** (2504.07634), **Agentic Code Reasoning** (2603.01896, semi-formal execution-path reasoning without running code). Shared pattern: maintain a belief over program state, query the runtime to update the belief, act on the posterior — Bayesian world-modeling in everything but name.

### 13.5 Safety and malicious code

**The Double Life of Code World Models** (2512.13821) repurposes CWM-style trace predictions for malicious-behavior detection. **CodeBreaker** (2406.06822) is the offensive analogue. **Concolic Execution + LLM for Zero-Day Malware Detection** (2603.09044) pairs path-prioritization with concrete execution.

---

## 14. Benchmarks and the Evaluation Gap

Benchmarks split cleanly by what they measure.

- **Static code quality** — HumanEval, MBPP, LiveCodeBench (2403.07974) measure code-LLM output without exercising the world-model claim.
- **Execution reasoning** — CRUXEval (2401.03065), REval (2403.16437), CRUXEval-X (2408.13001), TraceEval (2605.11006), PLSemanticsBench (2510.03415). The canonical WM evals.
- **Semantic equivalence** — EquiBench (2502.12466), CodeARC (2503.23145).
- **Agentic** — SWE-bench, SWE-Gym, WebArena (2307.13854), Mind2Web (2306.06070), PyBench (2407.16732), OSWorld, WindowsAgentArena.

**The eval gap.** No widely adopted benchmark directly measures world-model fidelity by holding the policy fixed and varying the WM. Every measurement of WM capability is mediated through downstream task performance, so we cannot distinguish *the model has internalized program semantics* from *the model is exploiting trace-token shortcuts in the test distribution*. **Demystifying Errors in LLM Reasoning Traces** (2512.00215) supplies the diagnostic: even DeepSeek-R1, o4-mini, Gemini 2.5 Flash, and Claude 4, when asked to simulate execution and explain their reasoning, produce traces with errors clustering into nine categories (Computation, Indexing, Control Flow, Skip Statements, Misvaluation of Native API, Hallucination, Input Misread, etc.). Models with 85–98% final-answer accuracy on output prediction produce traces with systematic errors throughout. The decoupling — high outcome accuracy, low process fidelity — is the signature of a system that has learned to predict outcomes without faithfully simulating dynamics.

---

## 15. Empirical Landscape

### 15.1 SWE-bench scoreboard

Pass@1 / resolve rate on SWE-bench Verified unless noted. WM type: *Scaffold* = no model training; *RL-Exec* = RL with execution rewards; *SFT-Traj* = SFT on agent trajectories; *Self-Play* = recursive self-improvement.

| System | Base model | Bench | Score | WM type | Source |
|---|---|---|---|---|---|
| SWE-agent | GPT-4 Turbo | full | 12.5% | Scaffold | 2405.15793 |
| AutoCodeRover | GPT-4 | Lite | 19.0% | Scaffold | 2404.05427 |
| Agentless | GPT-4o | Lite | 32.0% | Scaffold | 2407.01489 |
| SWE-Gym (Qwen-Coder-32B) | base 12.4% | Lite | 26.0% | SFT-Traj | 2412.21139 |
| SWE-Gym (Qwen-Coder-32B) | — | Verified | 20.6% | SFT-Traj | 2412.21139 |
| SWE-RL (Llama3-SWE-RL-70B) | Llama-3.3-70B | Verified | **41.0%** | RL-Exec | 2502.18449 |
| Agent-RLVR | Qwen-2.5-72B | Verified | 22.4% → 27.8% (w/ RM) | RL-Exec + guidance | 2506.11425 |
| Long-Context Multi-Turn RL | Qwen-2.5-72B | Verified | **39.0%** | RL-Exec | 2508.03501 |
| Darwin Godel Machine | Claude-3.5-Sonnet | Verified | 20% → **50%** | Self-Play | 2505.22954 |
| Huxley Godel Machine | GPT-5-mini | Verified (500) | **61.4%** | Self-Play | 2510.21614 |
| SICA | Claude-3.5-Sonnet + o3-mini | Verified (subset) | 17% → 53% | Self-Play scaffold | 2504.15228 |
| CWM | CWM-32B (own base) | Verified, TTS | **65.8%** (best@16) | Trace+Forager mid-train + RL | 2510.02387 |
| CWM | CWM-32B | Verified, pass@1 | ~53–55%* | (same) | 2510.02387 |
| Nanbeige SWE-World | Qwen-2.5-Coder-32B | Verified | 6.2% base → 52% SFT → 55% RL → **68.2% TTS@8** | SFT-Traj + simulated WM | 2602.03419 |

*CWM's 65.8% headline is best-of-16 over 40 verifier-reranked samples — *not* pure pass@1. Pure pass@1 is the mid-50s. Many citations omit this caveat.

**Synthesis.** Scaffold-only with frontier closed-model executor lands in the 30–55% band on Verified. SFT-on-trajectories on a 32B open-weight lands at 50–55%. Adding RL and verifier-reranked TTS pushes to 65–68%. World-model-trained variants are now competitive with frontier closed-model scaffold-only systems at far smaller parameter counts — the strongest empirical case for code-world-model training at this date. But once you account for the closed-model executor inside DGM/HGM/SICA, the gap "WM training adds on top of SFT-on-trajectories" is more like +15–25 absolute points (cf. Nanbeige SWE-World: SFT 52% → RL 55% → TTS 68%; the marginal value of RL alone on top of strong SFT is small).

### 15.2 Trace pretraining gains on execution-reasoning

| Paper | Backbone | Baseline | After trace pretrain/FT | Delta | Benchmark |
|---|---|---|---|---|---|
| TRACED | UnixCoder | — | +12.4% rel branch-coverage; +25.2% rel variable-value | rel | CodeNet exec |
| NExT | PaLM 2-L | 23.2 | 49.3 | **+26.1 abs** | MBPP-R |
| NExT | PaLM 2-L | 32.2 | 42.5 | +10.3 abs | HumanEvalFix-Plus |
| SemCoder (1.3B) | DS-Coder 1.3B | base | 63.6 / 63.9 | +23 abs | CRUXEval-I / O |
| "What I cannot execute" | Llama-3.1-8B | 37.8% | ~80% | **+42 abs** | CRUXEval-O |
| Do Code Semantics Help? | DSCoder, Llama-3, Gemma-2 | various | ≤ a few abs; some regressions | mixed | comprehensive |

For under-trained ≤8B open-weights, trace pretraining delivers +15 to +42 absolute on CRUXEval-O. The "Do Code Semantics Help?" ablation (2509.11686) is the disconfirming evidence: across multiple backbones and five trace representations, no single representation consistently outperforms others, and several downstream tasks regress under trace augmentation. The gain shrinks rapidly with base-model quality. Trace pretraining is a remedial intervention for weak code models; whether frontier models still benefit is unsettled.

### 15.3 Web/OS agents from WMs

| Paper | Benchmark | Base | With WM | Delta | Mechanism |
|---|---|---|---|---|---|
| WebDreamer (GPT-4o WM) | VisualWebArena | 17.6% | 23.6% | +34.1% rel (≈+6 abs) | LLM-as-WM + MPC |
| WebDreamer | Online-Mind2Web | 26.0% | 37.0% | +42.3% rel (≈+11 abs) | same |
| Dreamer-7B (trained WM) | VisualWebArena | base | +4.7 abs | — | trained WM |
| WMA (2410.13232) | WebArena | base | action-selection 52→70% | — | trained transition WM |
| Dyna-Think DDT (32B) | OSWorld BoN | RFT~28% | 43.1% | ≈+15 abs | Dyna-Q + WM head |
| Dyna-Think DDT | WindowsAgentArena | 28.4% | 34.9% | +6.5 abs | same |

WM gains on web/OS are real but quantitatively small (≤+5–10 absolute task success rate on most benchmarks), and partly confounded with the extra synthetic data the WM generates. DyMo's 90%+ state-prediction accuracy versus 72.8% task success rate exemplifies the decoupling: WM heads can be accurate without the agent being accurate.

### 15.4 Formal verification vs LLM-only

| System | Language | Benchmark | Baseline | With system | Source |
|---|---|---|---|---|---|
| ATLAS | Dafny | DafnyBench Pass@1 | 32.4% | **55.8%** | 2512.10173 |
| ATLAS | Dafny | DafnySynthesis Pass@5 | 15.8% | **65.8%** (>GPT-4 53.4) | 2512.10173 |
| CLEVER | Lean 4 | 161 problems end-to-end | best frontier | **≤1/161** | 2505.13938 |
| VeriStruct | Verus / Rust | 11 modules | — | **99.2%** (128/129 fns) | 2510.25015 |
| AutoRocq | Rocq | math + verif lemmas | 5 baselines | 48.0% math / 30.9% verif | 2511.17330 |
| Semantic Equiv Self-Play | Liquid Haskell | EquiBench | base | +13.3 pp | 2604.17010 |

Verified codegen has the steepest training-data sensitivity in the survey: small synthetic datasets (2.7K verified Dafny programs in ATLAS) produce +25–50 absolute gains because LLM-only baselines start near zero. CLEVER's ≤1/161 shows that without explicit data/scaffolding, frontier models cannot reliably produce verified code. VeriStruct shows that on curated targets near-perfect is reachable.

### 15.5 Reasoning-model competitive programming

| Model | Codeforces | IOI / ICPC |
|---|---|---|
| gpt-4o | 808 (11th pct) | — |
| o1-preview | 1258 (62nd pct) | — |
| o1 | 1673 (89th pct) | — |
| o1-ioi | 1807 (~93rd pct) | IOI 2024 49th pct live |
| o3 | elite-human-class | IOI 2024 gold |
| gpt-oss-120b + GenCluster | — | **IOI 2025 gold (first open-weight)** |
| Gemini 2.5 Pro Exp | — | ICPC-Eval Pass@1 22.0% |
| DeepSeek-R1 | — | ICPC-Eval Pass@1 14.4% |
| Claude 3.7 Sonnet | — | ICPC-Eval Pass@1 11.8% |
| GPT-4o | — | ICPC-Eval Pass@1 5.9% |

Codeforces +999 rating points in 14 months on the o-series. The same line shows that frontier reasoning models gain almost everything from RL scaling, not from domain-specialized scaffolds — which complicates the case that "trace-style world models" are doing causal work for frontier systems.

---

## 16. Critical Perspectives

This section names where the field overclaims, where the consensus is fragile, and where vocabulary is doing more work than evidence. We develop seven theses.

### 16.1 The "world model" label has become marketing for any code LLM trained on something other than raw source

Read CWM (2510.02387) carefully and the architecture it ships is a 32B decoder-only Transformer with GQA, sliding-window blocks, RoPE, AdamW — a Llama-class model. What earns it the "world model" badge is the mid-training datamix: 5T tokens of Python observation-action traces plus ForagerAgent SWE trajectories. There is no separate dynamics head, no inverse model, no recurrent latent. By the survey's own §2 definition this places CWM in the "implicit WMs in token policies" bucket, distinguishable from TRACED (2306.07487) or SemCoder (2406.01006) only by scale and data composition. The same accusation lands on LLM-JEPA, DyMo, and most "world model" papers from 2024–2026: the artifact is a standard LLM with an enriched objective.

A useful purity test: *can we ablate the supposed world-modeling component without changing the architecture?* If yes, the system is a trace-trained LLM. If no, there is a genuine architectural commitment. By that test, CoLA (2503.21383) and the Dreamer-for-LLMs gestures pass. CWM, SemCoder, NExT, and most of the "explicit WM" cluster fail. The survey should reserve "world model" as a strict technical term and call the rest by what they are — *execution-grounded code LLMs*. Terminology slippage is not innocent: it lets a field claim novelty while shipping incremental supervision.

### 16.2 Trace pretraining has a causal-isolation problem the surface numbers obscure

"Do Code Semantics Help?" (2509.11686) is the most damaging paper for the prevailing optimism. It runs a comprehensive ablation across DeepSeek-Coder, LLaMA-3, and Gemma-2 with five representations (Scratchpad, NExT, CodeExecutor, Concise, SemCoder) on program repair, code synthesis, BigCodeBench, LiveCodeBench, and CRUXEval. Its headline: integrating trace-based semantic information into SFT *cannot significantly enhance* code-generation ability. In 7 of 9 synthesis settings the no-trace baseline wins or ties. At inference, in 36 of 56 test-scaling configurations, trace prompts hurt.

"What I cannot execute, I do not understand" (2503.05703) is gentler — Execution Tuning reaches ~80% CRUXEval-O — but the same paper's downstream evaluations on HumanEval, MBPP, and GSM8K show *negligible* gains from trace data in the SFT mix. The honest reading: trace pretraining helps execution prediction (the thing trained on) and barely transfers to code generation (the thing we care about), the pattern you would expect if dense execution supervision is teaching a narrow tracking skill rather than a general predictive model of program semantics.

CWM's 65.8% on SWE-bench is the apparent counterexample, but the Meta team reports it after trace mid-training *and* 3M ForagerAgent SWE trajectories *and* multi-task RL with verifiable rewards — three interventions stacked. The "world model" component is not causally isolated from the SWE-trajectory and RL components. Without an ablation that removes trace mid-training while holding ForagerAgent and RL fixed, the headline is unfalsifiable. The field has agreed to call CWM a world-model success because the name is on the model card, not because the experimental design demonstrates it.

### 16.3 The Dreamer-for-code gap may be a non-problem

The conventional framing treats the absence of latent-imagination world models for SWE as the field's largest architectural gap. The empirical record argues the opposite. CWM in token space reaches 65.8% SWE-bench. CoLA produces respectable but not field-shifting results, and even there the WM is fine-tuned on top of a standard LLM rather than replacing it.

Vision world models needed latent rollouts because pixel-space rollouts were too expensive — a frame is ~10^6 dimensions, dynamics are partially observed. Program execution is the opposite: a Python frame is small, dynamics are observable, and the simulator (CPython) is available for free at training time. The pressure that drove Dreamer's RSSM design does not exist for code.

Debugging Code World Models (2602.07672) shows CWM's long-horizon failures are dominated by *action hallucination*, not state-propagation error — under teacher forcing CWM tracks state correctly for 128 steps. A latent rollout would compress states but not fix the action policy, which is the actual bottleneck.

The counterargument is fair: latent rollouts permit faster planning at inference, and for multi-agent or population-scale search the speedup is asymptotically meaningful. But the survey should retire "single largest architectural gap" framing and replace it with "an interesting open question whose payoff is not yet demonstrated."

### 16.4 PRMs are critics, not world models

Process reward models — ExecVerify (2603.11226), SWE-PRM (2509.02360), ThinkPRM (2504.16828), FunPRM (2601.22249), DataPRM (2604.24198) — are often grouped under the world-modeling umbrella. This is wrong in a way that matters. A world model is, by every definition the survey uses, a *forward* predictor of `(state, action) → next_state`. A PRM is a *backward-looking evaluator*: given a partial trajectory, score it. In classical model-based RL these are different objects — Dreamer has both a world model (RSSM) and a critic (value function).

PRMs cannot roll out. Cannot simulate counterfactuals. Cannot be used by a planner that wants to score a hypothesized future. Conflating them dilutes the world-model concept until it means "any neural network trained on execution-related signals" — at which point the term is useless. Vocabulary discipline is cheap and the field would benefit from it.

The same critique applies, less severely, to verifier-grounded systems: a Lean proof checker is not a world model, it is a deterministic verifier of a candidate output. Calling it "the world model" when ATLAS, Re:Form, or AutoRocq use it makes for a tidy survey arc but blurs the actual computational structure.

### 16.5 "General Agents Contain World Models" is much weaker than its title suggests

Richens et al. (2506.01622) prove that any goal-conditioned policy satisfying a regret bound `δ` for sufficiently deep composite goals (depth `n ≫ 1`) must encode an extractable approximation of the transition function with bounded error. Genuine and elegant.

But read the assumptions: fully observed environment, finite communicating stationary controlled MDP, goal-conditioned policy satisfying a regret bound for a specific class of LTL composite goals of depth n. Theorem 2 of the same paper explicitly shows that for myopic agents (depth-1 goals), *no world model is needed*. Real SWE agents are myopic-ish over short turns and approximately competent over longer ones; their environments are partially observed (rarely full filesystem state); they violate stationarity (the repository changes under their actions); and their regret bound for arbitrary composite goals is unknown and almost certainly not satisfied. The authors caveat this in §5 ("Limitations") of their paper.

The theorem is a beautiful existence proof for an idealized agent class. It is *not* an empirical statement that SWE coding agents have learned world models, and it provides no guidance about the fidelity of any world model they may have learned.

### 16.6 The verifier-grounded lineage is the actual leading edge

ATLAS, Re:Form, CLEVER, VeriStruct, AutoRocq, and the Liquid Haskell self-play paper (2604.17010) share a property no LLM-only system possesses: code whose correctness is *machine-checked* against a formal specification. Compare to the SWE-bench paradigm, where "correctness" means "hidden unit tests pass" — a weaker guarantee, since unit tests cover specific inputs and the system can pass them while being wrong on adjacent inputs.

The abstract-interpreter paper (2503.12686) is the diagnostic: when frontier reasoning LLMs are asked to reason in the style of formal abstract interpretation over 22 SV-COMP programs, they make systematic errors in widening, fixpoint termination, control-flow propagation, and meet/join operations. They generated unsound invariants on programs as small as `count_by_2.c`. If LLMs cannot reliably perform interval-domain abstract interpretation on toy C programs, claims that they have learned faithful internal world models of program semantics are doing a lot of inferential work.

The verifier-grounded line is the only research direction that does not rely on LLM self-report for correctness, and it should be promoted from §13.1 to a co-equal pillar of the survey alongside trace pretraining and agentic SWE. The future of correct code is almost certainly hybrid: neural proposal, symbolic verification, with the verifier providing the ground truth that the world model fails to.

### 16.7 The evaluation gap is the structural reason the field looks confused

Across CRUXEval, REval, CRUXEval-X, PLSemanticsBench, TraceEval, and EquiBench, no benchmark holds policy fixed and varies world-model quality. Every measurement of "world-modeling capability" is mediated through downstream task performance, so we cannot distinguish *the model has internalized program semantics* from *the model is exploiting trace-token shortcuts in the test distribution*.

"Demystifying Errors in LLM Reasoning Traces" (2512.00215) is the diagnostic: even DeepSeek-R1, o4-mini, Gemini 2.5 Flash, and Claude 4, when asked to simulate execution, produce traces with errors in nine systematic categories. Models with 85–98% final-answer accuracy on output prediction produce traces with systematic errors throughout — high outcome accuracy, low process fidelity, the signature of a system that predicts outcomes without faithfully simulating dynamics.

Self-repair literature exhibits the same pathology: Olausson et al. (2306.09896) showed that GPT-4 self-repair on APPS and HumanEval, normalized by compute, often performs *worse* than i.i.d. resampling. The bottleneck is the model's feedback quality, not its repair capability — human-written feedback boosts repair success by 1.58×. The model can generate code, can sometimes recognize bugs, but cannot reliably simulate why its code is wrong — which is exactly what a faithful world model would let it do. The empirical bound on LLM self-repair is, in effect, an empirical bound on the fidelity of the implicit world model the LLM is running. Calling that world model internal is fine; calling it good is not.

Until benchmarks measure process fidelity independently of outcome, "is this system actually building a world model?" remains scientifically undecidable.

---

## 17. Open Problems

The critical perspectives of §16 reshape the conventional open-problems list. We propose six problems where the literature is thinnest *and* the upside is largest.

**1. Causal isolation of trace-pretraining contributions.** Every claim of the form "this WM-trained model achieves X" should be paired with an ablation removing the WM component while holding training data and RL fixed. CWM in particular needs this. Without it, the headline numbers underdetermine whether the WM did the work.

**2. World-model fidelity as a first-class metric.** §14's eval gap is concrete: build a benchmark where holding policy fixed and varying WM quality causes measurable variation in planning quality, independent of downstream task. This benchmark would clarify the field more than any single new model.

**3. Hybrid neural-symbolic systems.** §16.6 argues the verifier-grounded line is the leading edge. The natural integration is *neural proposal, symbolic verification*, with the verifier providing gradient-free correctness signal and the neural component providing proposals at scale. Differentiable surrogates of symbolic verifiers (Lean / Dafny / Rocq) that pass verifier-style gradients during training are open.

**4. Multi-modal WMs for coding.** GUI agents need pixel-level WMs (Neural Computers, 2604.06425, is a first attempt). Tying pixel WMs to code-state WMs through a shared latent is essentially unsolved.

**5. Long-horizon credit assignment with execution-grounded rewards.** PRMs (§8.3) are early, and §16.4 argues they should be conceptually separated from world models. The right structure for rewarding an agent across hundreds of execution-grounded steps is a live question.

**6. World models of the developer, not just the program.** All current WMs model the *machine*. Few model the *developer intent* with comparable fidelity. ATLAS and Re:Form gesture in this direction by treating the spec as the WM. A full developer-intent WM would close the agentic loop.

We do not list "Dreamer-for-SWE-agents" as the field's largest gap, contrary to common framing. §16.3 argues the pressure motivating that direction in vision does not transfer to code. It remains an interesting research question, not the highest-leverage one.

---

## 18. Conclusion

Across the literature surveyed here, a single trajectory is visible: from neural execution (modeling the machine), through trace pretraining (modeling execution implicitly), to CWM and its descendants (modeling execution explicitly with a named artifact), to agentic SWE and RL (modeling the environment), to JEPA and latent-action models (modeling in compressed space), and on toward formal verification, probing, and safety (modeling reliably). What was a scattered set of insights in 2014 has by 2026 cohered into a recognizable research program with a recognizable artifact — the code world model.

The remaining work splits into two halves. The first is empirical: close the eval gap, isolate the causal contribution of WM-training, build hybrid neural-symbolic systems whose correctness is verifier-checkable rather than test-checkable. The second is rhetorical: hold the term "world model" to a strict definition so the literature can distinguish architectural commitments from training-data choices, and resist the temptation to oversell extractability theorems and latent-imagination analogies whose premises do not transfer to code.

The opportunity is large precisely because the framework is now clear enough to identify what is missing. The work to do is the work this survey has tried to make visible.

---

## Appendix · Glossary

- **CWM** — Code World Model (2510.02387 and lineage).
- **JEPA** — Joint Embedding Predictive Architecture (LeCun et al.).
- **RSSM** — Recurrent State-Space Model (Dreamer family).
- **PRM** — Process Reward Model.
- **SWE agent** — Software-engineering agent operating on real repositories.
- **Trace pretraining** — Pretraining where execution traces appear in input or target.
- **Execution-grounded RL** — RL whose reward derives from program execution.
- **Latent-imagination rollout** — Forward simulation in compressed latent space rather than token space.
- **TTS** — Test-time scaling (sampling many candidates + verifier reranking at inference).
- **GRPO** — Group Relative Policy Optimization (R1-family RL algorithm).
