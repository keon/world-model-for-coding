# A Comprehensive Survey on World Models for Coding

Survey draft: [`SURVEY.md`](./SURVEY.md) · Machine-readable corpus index: [`papers.json`](./papers.json) (183 papers)

This README lists the 101 papers cited in the survey, grouped by section, with one-line summaries. The full 183-paper corpus considered for the survey is enumerated in `papers.json`; PDFs are not redistributed in this repo, but every paper is fetchable from arxiv via its ID (`https://arxiv.org/abs/<id>` or `https://arxiv.org/pdf/<id>`).

---

## Related surveys

- **2406.00515 — A Survey on LLMs for Code Generation** — broad code-LLM landscape; complements ours without the world-model lens.
- **2411.14499 — Understanding World or Predicting Future** — general survey of world models; complements ours without the code lens.

## §4 Foundations: neural execution

- **1410.4615 — Learning to Execute** — LSTM seq2seq trained to evaluate short Python programs; the foundational neural-execution paper.
- **2112.00114 — Show Your Work / Scratchpads** — transformer emits intermediate computation states; hinge moment between LSTM neural-exec and trace pretraining.
- **2401.03065 — CRUXEval** — canonical input/output-prediction benchmark for code-execution reasoning.
- **2403.16437 — REval** — runtime-behavior benchmark across coverage, value, and state tasks.

## §5 Trace pretraining and the CWM lineage

### Trace pretraining
- **2305.05383 — CodeExecutor** — transformer trained to simulate Python execution token-by-token.
- **2306.07487 — TRACED** — execution-aware pretraining mixes dynamic-state supervision into code-LLM training.
- **2404.14662 — NExT** — naturalized execution tuning; trace-grounded chain-of-thought.
- **2406.01006 — SemCoder** — monologue reasoning linking source text to execution state.
- **2503.05703 — What I Cannot Execute, I Do Not Understand** — trains and evaluates LLMs on traces with dynamic scratchpads.
- **2506.10343 — Code Execution as Grounded Supervision** — line-by-line traces as verifiable CoT supervision.
- **2604.03253 — Self-Execution Simulation** — LLMs trained on their own execution predictions.
- **2512.00215 — Demystifying Errors in LLM Reasoning Traces** — empirical failure-mode audit of trace-trained LLMs.

### CWM proper
- **2510.02387 — CWM (Code World Models)** — Meta FAIR's open-weights code world model; mid-trained on Python interpreter traces and SWE forager-agent trajectories; 65.8% SWE-bench Verified.
- **2602.07672 — Debugging Code World Models** — systematic probe of CWM failures on long traces and string state.
- **2604.20926 — Reasoning World Models for Parallel Code** — predicts race conditions and profiling artifacts from parallel source.
- **2604.03144 — Industrial CWM / InCoder-32B-Thinking** — CWM recipe applied to Verilog and GPU execution traces.
- **2512.13821 — The Double Life of Code World Models** — CWM trace predictions repurposed for malicious-behavior detection.
- **2603.09951 — Towards a Neural Debugger for Python** — neural debugger framed as forward/inverse world model.
- **2604.06425 — Neural Computers** — video-model-style world models of CLI/GUI runtime from I/O traces.
- **2405.15383 — Generating Code World Models with LLMs Guided by MCTS** — LLM synthesizes Python world-model programs executed during planning.
- **2506.01622 — General Agents Contain World Models** — proves extractable world models are structural for general agents.

## §6 World models for code agents

### Web and computer-use agents
- **2411.06559 — WebDreamer** — LLM-as-world-model simulates click/fill outcomes; trains specialist "Dreamer-7B."
- **2506.02918 — DyMo / World Modeling Improves LM Agents** — next-state-prediction head improves function-calling agents on BFCL-V2.
- **2410.13232 — Web Agents with World Models** — systematic study of WM use across web agents.
- **2506.00320 — Dyna-Think** — Dyna-Q-style synthesis of real and imagined experience for OSWorld and WindowsAgentArena.
- **2602.05842 — Reinforcement World Model Learning for LLM-based Agents** — action-conditioned WMs on textual states.
- **2602.00785 — World Models as an Intermediary between Agents and the Real World** — WM as surrogate for expensive environments.

### SWE agents
- **2310.06770 — SWE-bench** — canonical SWE evaluation on real-world GitHub issues.
- **2412.21139 — SWE-Gym** — executable SWE training environment with real runtimes.
- **2602.03419 — Nanbeige SWE-World** — learned Docker-free execution surrogate for SWE agents.
- **2603.11103 — Understanding by Reconstruction** — reverses the development process to harvest agentic pretraining traces.
- **2604.14820 — SWE-TRACE** — process reward modeling over execution trajectories for long-horizon SWE.
- **2512.18552 — Self-Play SWE-RL** — adversarial bug-injection/repair self-play.
- **2603.17399 — Bootstrapping Coding Agents / Specification Is the Program** — frames the SWE task itself as a programmatic spec.
- **2402.01030 — CodeAct** — Python interpreter as the unified action space and state-carrying medium.
- **2303.11366 — Reflexion** — verbal RL with episodic memory over environment feedback.

## §7 RL with execution as the world signal

- **2410.02089 — RLEF (Reinforcement Learning from Execution Feedback)** — RL where the Python interpreter is the environment.
- **2502.18449 — SWE-RL** — R1-style RL on open-source software evolution; 65%+ SWE-bench.
- **2501.12948 — DeepSeek-R1** — long-CoT reasoning RL; anchor of the modern reasoning-RL paradigm.
- **2207.01780 — CodeRL** — foundational execution-reward RL for code generation.
- **2603.11226 — ExecVerify** — white-box stepwise rewards from execution traces.
- **2509.02360 — SWE-PRM** — taxonomy-guided process reward model for SWE agents.
- **2604.24198 — DataPRM** — PRM that actively probes execution state to catch silent errors.
- **2410.17621 — Process Supervision-Guided Policy Optimization** — step-level execution-grounded supervision.
- **2412.15118 — Outcome-Refining Process Supervision** — process supervision via concrete execution signals.

## §8 Planning and search with code world models

- **2305.14992 — RAP** — Reasoning with Language Model is Planning with World Model; foundational LLM-as-WM + MCTS.
- **2305.10601 — Tree of Thoughts** — deliberate search over LLM intermediate states.
- **2412.12119 — Mastering Board Games by External/Internal Planning with LMs** — learned tree search with LLM as WM.
- **2506.10948 — Execution Guided Line-by-Line Code Generation** — classifier-free guidance conditioning next token on candidate runtime outcome.
- **2509.09245 — Jupiter** — notebook state as MCTS search nodes.
- **2411.13826 — REPL-Plan** — REPL state pool reused across tasks.

## §9 JEPA, Dreamer, and the latent-action gap

- **1803.10122 — Ha & Schmidhuber, World Models** — foundational world-model paper for RL.
- **2301.08243 — I-JEPA** — joint embedding predictive architecture; LeCun's energy-based world model.
- **2509.14252 — LLM-JEPA** — JEPA objective applied to LLMs using (text, code) as the two views; only code-relevant JEPA paper.
- **2504.16591 — JEPA for RL** — energy-based JEPA objective generalized to RL.
- **2503.21383 — CoLA — Controlling LLMs with Latent Actions** — inverse-dynamics latent action space + LLM-as-WM + RL/MCTS; the single clearest Dreamer-for-LLMs instance.
- **2406.10667 — UniZero** — transformer-based latent world model generalizing MuZero; domain-agnostic, rarely instantiated on code.
- **2402.15391 — Genie** — generative interactive environments; vision-WM template.

## §10 Reasoning, process rewards, memory

### Long-CoT reasoning for code
- **2412.00154 — o1-Coder** — o1 replication for code with MCTS+RL.
- **2505.21668 — R1-Code-Interpreter** — open SFT+RL recipe across 144 code-interpreter tasks; emergent self-checking.
- **2510.14232 — Scaling Test-Time Compute to Achieve IOI Gold Medal** — open-weight gpt-oss-120b matches closed models via inference-time scaling.

### Process reward models
- **2504.16828 — ThinkPRM** — generative long-CoT process reward model.

### Memory
- **2502.06975 — Episodic Memory is the Missing Piece for Long-Term LLM Agents** — position paper on agent memory.
- **2510.12635 — Memory as Action** — memory operations as RL-learnable actions.
- **2410.14684 — RepoGraph** — repository-level dependency graph as durable agent state.

## §11 Verification, probing, safety

### Symbolic execution and formal verification
- **2505.13452 — AutoBug / LLM-Powered Symbolic Execution** — path-based decomposition combining symbolic execution with LLMs.
- **2506.09550 — SESpec** — strongest-postcondition guidance for LLM-generated invariants.
- **2508.00419 — Loop Invariant Generation via Reasoning LLMs + SMT** — O1+Z3 generate-and-check; 100% on Code2Inv.
- **2512.10173 — ATLAS** — fine-tunes Qwen on 2.7K verified Dafny programs.
- **2507.16331 — Re:Form** — RL with Dafny verifier feedback.
- **2505.13938 — CLEVER** — 161-problem Lean verified-code benchmark.
- **2510.25015 — VeriStruct** — Verus verification of Rust data structures.
- **2511.17330 — AutoRocq / Agentic Program Verification** — LLM agent iteratively building Rocq proofs.
- **2604.17010 — Semantic Equivalence Self-Play with Formal Verification** — Liquid Haskell proofs as adversarial training signal.
- **2503.12686 — Understanding Formal Reasoning Failures in LLMs as Abstract Interpreters** — frames code LLM as abstract interpreter.

### Probing and mechanistic interpretability
- **2510.02917 — Mechanistic Interpretability of Code Correctness via SAEs** — probes what code LLMs represent about correctness.
- **2512.07404 — On LLMs' Internal Representation of Code Correctness** — internal-representation probing study.

### Repair and debugging as world-model probing
- **2304.05128 — Teaching LLMs to Self-Debug** — rubber-duck debugging from execution results.
- **2510.18327 — InspectCoder** — LLM control of an interactive debugger as a dynamic-analysis WM probe.
- **2504.07634 — Agent That Debugs / Dynamic State-Guided Vulnerability Repair** — runtime state-guided security repair.
- **2603.01896 — Agentic Code Reasoning** — semi-formal execution-path reasoning without running code.

### Safety and malicious code
- **2406.06822 — CodeBreaker** — LLM-assisted backdoor attack on code completion that evades static detection.
- **2603.09044 — Concolic Execution + LLM for Zero-Day AI-Generated Malware Detection** — path-prioritization with concrete execution.

## §12 Specialized domains

### Diffusion code models
- **2506.20639 — DiffuCoder** — masked diffusion + coupled-GRPO code generation.
- **2509.01142 — Dream-Coder 7B** — open diffusion code language model.

### Decompilation and cross-language
- **2509.22114 — SK2Decompile** — skeleton+skin two-phase binary decompilation.
- **2509.14646 — SALT4Decompile** — abstract-logic-tree-based decompilation.
- **2502.12466 — EquiBench** — semantic-equivalence benchmark across transformations.

### Hardware / RTL
- **2508.18462 — VeriRL** — Verilog RL with trace-back rescoring.
- **2507.04736 — ChipSeek** — EDA-integrated hierarchical-reward RL.
- **2504.15659 — VeriCoder** — functional-correctness-validated RTL fine-tuning dataset.

### ARC and abstract synthesis
- **2605.05138 — Executable World Models for ARC-AGI-3** — literal-WM-per-task: synthesized Python world model verified against observations.
- **2507.14172 — SOAR** — self-improving evolutionary program synthesis on ARC-AGI.

### Self-improvement
- **2505.22954 — Darwin Godel Machine** — open-ended self-modifying coding agent.
- **2510.21614 — Huxley Godel Machine** — human-level coding agent via CMP-guided self-improvement.

## §13 Benchmarks (additional)

- **2403.07974 — LiveCodeBench** — contamination-resistant code-LLM eval.
- **2408.13001 — CRUXEval-X** — multilingual execution-reasoning across 19 languages.
- **2605.11006 — TraceEval** — execution-verified multi-language code-semantics benchmark.
- **2510.03415 — PLSemanticsBench** — LLMs as formal-semantics interpreters.
- **2503.23145 — CodeARC** — inductive program synthesis benchmark with differential-testing oracle.

---

*All PDFs are in `papers/`. The folder also contains the broader 183-paper corpus surveyed across four expansion passes, including papers not cited here.*
