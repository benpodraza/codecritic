**Comprehensive End-to-End Engineering Specification for CodeCritic Experimentation**

**Overview**

The CodeCritic system is an autonomous multi-agent framework designed to facilitate software generation, evaluation, maintenance, and continuous improvement. This comprehensive manual provides detailed guidance on structuring, executing, and evaluating experiments. These experiments systematically identify the optimal combinations of system components for creating software systems maintainable by artificial intelligence (AI).

**Purpose of Experiments**

The experiments aim to explore different configurations of CodeCritic’s integrated tools and methodologies, including structured logging, multi-agent interactions, symbolic reasoning via symbol graphs, and iterative self-improvement. Each experimental iteration seeks to enhance agent interactions, logging accuracy, and system adaptability to achieve AI-driven software maintenance.

**Folder-File Structure**

The following folder and file structure outlines how the CodeCritic framework organizes its components and outputs:

app

├── abstract_classes

│ ├── system_manager_base.py

│ ├── agent_base.py

│ ├── state_manager_base.py

│ ├── prompt_generator_base.py

│ ├── context_provider_base.py

│ ├── tool_provider_base.py

│ └── scoring_provider_base.py

├── extensions

│ ├── system_managers

│ ├── state_managers

│ ├── agents

│ ├── tools

│ ├── prompt_generators

│ ├── context_providers

│ ├── tool_providers

│ ├── agent_prompts

│ ├── system_prompts

│ └── scoring_models

├── enums

│ ├── system_enums.py

│ └── agent_enums.py

├── utilities

│ ├── file_management

│ ├── metadata

│ │ ├── logging

│ │ └── footer

│ └── snapshots

├── factories

│ ├── system_manager.py

│ ├── state_manager.py

│ ├── agent.py

│ ├── prompt_manager.py

│ ├── system_config_provider.py

│ ├── experiment_config_provider.py

│ ├── tool_provider.py

│ └── scoring_provider.py

├── registries

│ ├── system_managers

│ ├── state_managers

│ ├── agents

│ ├── agent_engines

│ ├── prompt_generators

│ ├── agent_prompts

│ ├── system_prompts

│ ├── context_providers

│ ├── tool_providers

│ ├── tools

│ └── scoring_models

└── tools

├── black_runner.py

├── doc_formatter.py

├── mypy_runner.py

├── radon_runner.py

├── ruff_runner.py

└── sonarcloud_runner.py

experiments

├── logs

│ ├── structured logging output

│ └── detailed execution logs

└── artifacts

├── intermediate and final outputs

└── snapshots of code states

**Database Schemas**

SQLite is the database backend for structured logging and metadata storage, supporting experiment reproducibility and analysis.

CREATE TABLE agent_engine (

id INTEGER PRIMARY KEY,

name TEXT,

description TEXT,

model TEXT,

engine_config TEXT,

artifact_path TEXT

);

CREATE TABLE agent_prompt (

id INTEGER PRIMARY KEY,

name TEXT,

description TEXT,

agent_role TEXT,

system_type TEXT,

artifact_path TEXT

);

CREATE TABLE system_prompt (

id INTEGER PRIMARY KEY,

name TEXT,

description TEXT,

system_type TEXT,

artifact_path TEXT

);

CREATE TABLE context_provider (

id INTEGER PRIMARY KEY,

name TEXT,

description TEXT,

system_type TEXT,

tooling_provider_id INTEGER

);

CREATE TABLE file_path (

artifact_path TEXT PRIMARY KEY

);

CREATE TABLE agent_config (

id INTEGER PRIMARY KEY,

name TEXT,

description TEXT,

agent_role TEXT,

system_type TEXT,

agent_engine_id INTEGER,

prompt_generator_id INTEGER,

artifact_path TEXT

);

CREATE TABLE tooling_provider (

id INTEGER PRIMARY KEY,

name TEXT,

description TEXT,

artifact_path TEXT

);

CREATE TABLE scoring_provider (

id INTEGER PRIMARY KEY,

name TEXT,

description TEXT,

artifact_path TEXT

);

CREATE TABLE prompt_generator (

id INTEGER PRIMARY KEY,

name TEXT,

description TEXT,

agent_prompt_id INTEGER,

system_prompt_id INTEGER,

content_provider_id INTEGER,

artifact_path TEXT

);

CREATE TABLE state_manager (

id INTEGER PRIMARY KEY,

name TEXT,

description TEXT,

system_state TEXT,

system_type TEXT,

agent_id INTEGER,

artifact_path TEXT

);

CREATE TABLE system_config (

id INTEGER PRIMARY KEY,

name TEXT,

description TEXT,

system_type TEXT,

state_manager_id INTEGER,

scoring_model_id INTEGER

);

CREATE TABLE experiment_config (

id INTEGER PRIMARY KEY,

name TEXT,

description TEXT,

system_manager_id INTEGER,

scoring_model_id INTEGER

);

CREATE TABLE series (

id INTEGER PRIMARY KEY,

experiment_config_id INTEGER

);

**Comprehensive End-to-End Engineering Specification for CodeCritic Experimentation (Part 2)**

**Components and Responsibilities**

**Experiment Lifecycle Management**

**Experiment**

- Initiates and manages the execution of experiments.
- **Method:** run() initiates experiments based on configurations.

**System and State Management**

**SystemManagerBase**

- Handles logging and finite state machine (FSM) logic.
- **Method:** run() ensures logging; \_run_system_logic() performs state transitions.

**StateManagerBase**

- Manages the execution of agent-level operations within system states.
- **Method:** run() executes logging and agent actions.

**Agents and Logic Execution**

**AgentBase**

- Responsible for executing agent-specific logic with logging.
- **Method:** run() manages logging; \_run_agent_logic() implements agent tasks.

**Prompt Generation**

**PromptGeneratorBase**

- Generates prompts needed by agents, ensuring logging.
- **Method:** generate_prompt() oversees logging and calls \_generate_prompt().

**Context and Symbol Management**

**ContextProviderBase**

- Supplies context using symbol graphs, enforcing comprehensive logging.
- **Method:** get_context() handles logging; \_get_context() manages symbol graph access.

**External Tool Integration**

**ToolProviderBase**

- Integrates and manages the execution of external tools with robust logging.
- **Method:** run() handles logging; \_run() executes tool-specific logic.

**Scoring and Evaluation**

**ScoringProviderBase**

- Evaluates agent performance using predefined metrics.
- **Method:** score() ensures logging; \_score() computes evaluation metrics.

**Logging Strategy**

Structured logging captures comprehensive data throughout each experiment run. Logs are categorized into:

- **Experiment Logs**
- **State and Transition Logs**
- **Prompt and Conversation Logs**
- **Scoring Logs**
- **Code Quality Logs**
- **Error Logs**

Each category has clearly defined triggers and schemas to ensure consistent and analyzable data.

**Unified Log Schemas**

- **ScoringLog:** experiment_id, round, symbol, final, score, passed, evaluator_name, evaluator_version, diagnostics, tests_total, tests_passed, all_tests_passed, issue_id, attempt_number, parent_attempt_number, timestamp
- **CodeQualityLog:** experiment_id, round, symbol, lines_of_code, cyclomatic_complexity, maintainability_index, lint_errors, timestamp
- **ConversationLog:** experiment_id, round, agent_role, target, content, originating_agent, intervention, intervention_type, intervention_reason, timestamp
- **PromptLog:** experiment_id, round, system, agent_id, agent_role, agent_engine, symbol, prompt, response, attempt_number, agent_action_outcome, start, stop
- **StateLog:** experiment_id, system, round, state, action, score, details, timestamp
- **StateTransitionLog:** experiment_id, round, from_state, to_state, reason, timestamp
- **ErrorLog:** experiment_id, round, error_type, message, file_path, timestamp
- **ExperimentLog:** experiment_id, description, mode, variant, max_iterations, stop_threshold, model_engine, evaluator_name, evaluator_version, final_score, passed, reason_for_stop, start, stop

**Comprehensive Trigger Events**

- **ExperimentLog:** Experiment initialization/start, completion/end, errors or exceptions.
- **StateLog:** Entry into and completion of system states; errors during execution.
- **StateTransitionLog:** Transition between states.
- **PromptLog:** Generation attempts by agents, including successes, failures, partial completions, and exceptions.
- **ConversationLog:** Communications between agents, humans, and orchestrators; interventions; exceptions.
- **ScoringLog:** Scoring events, including start, completion of evaluations, and test suite execution; exceptions.
- **CodeQualityLog:** Completion of static code analysis and linting checks; exceptions.
- **ErrorLog:** Any encountered exceptions.

**Evaluation Metrics**

Each experiment evaluates performance against multiple metrics:

- **Bug-fix success rate**
- **Functional correctness**
- **Test pass rates**
- **Maintainability and complexity indices**
- **Linting compliance**
- **Iterations to convergence**
- **Intervention frequencies**
- **Role-specific success rates**
- **Retry and mediation effectiveness**

Detailed evaluation functions and metric computations are provided separately.

**Comprehensive End-to-End Engineering Specification for CodeCritic Experimentation (Part 3)**

**Conducting Experiments**

Follow these structured steps for systematically conducting and managing experiments:

1. **Configure Experiment Parameters**
    - Clearly define and document all experiment settings, including agent configurations, evaluation criteria, and logging preferences.
2. **Execution of Experiments**
    - Invoke the run() method of the Experiment class to initiate the configured experiments.
3. **Data Logging**
    - Verify that all logs are accurately captured and stored in the designated SQLite database and filesystem.
4. **Data Analysis**
    - Utilize provided analysis scripts and notebooks to evaluate and interpret the collected log data and experiment outcomes.

**Reporting Results**

Upon experiment completion, results should be systematically reported using:

- **Evaluation Notebooks:** Clearly documented notebooks to visualize metrics and performance outcomes.
- **Benchmark Comparisons:** Results should be benchmarked against established industry standards and known baselines such as SWE-Bench and HumanEval.

This structured reporting ensures clear visibility of experiment results and facilitates informed decisions on system optimizations.

**Detailed Implementation Plan**

**Phase 1: Infrastructure Setup**

**Tasks:**

- Implement abstract base classes.
- Define and validate folder structure.
- Set up registries and factories.

**Deliverables:**

- Initial class and directory structure.
- Test notebook confirming instantiation and structural correctness.

**Phase 2: FSM Logic and State Management**

**Tasks:**

- Develop finite state machine (FSM) transitions.
- Implement system and state management classes.

**Deliverables:**

- Functional FSM implementation.
- State manager execution logic.
- Test notebook for validating state transitions and logging.

**Phase 3: Agent Logic and Tool Integration**

**Tasks:**

- Implement agent logic for execution.
- Integrate tooling such as black, mypy, radon, ruff, sonarcloud.

**Deliverables:**

- Integrated agent logic with external tools.
- Test notebook demonstrating agent actions and tool outputs.

**Phase 4: Contextual and Prompt Generation**

**Tasks:**

- Implement context providers integrating symbol graphs.
- Develop prompt generators for agent and system prompts.

**Deliverables:**

- Operational context providers.
- Prompt generation modules.
- Test notebook confirming the accuracy of generated contexts and prompts.

**Phase 5: Scoring and Metric Evaluation**

**Tasks:**

- Implement scoring providers.
- Develop evaluation metric computation logic.

**Deliverables:**

- Fully functional scoring mechanisms.
- Test notebook demonstrating accurate computation of evaluation metrics.

**Phase 6: Full System Integration and Validation**

**Tasks:**

- Perform comprehensive integration of all system components.
- Implement multi-agent interaction logic.

**Deliverables:**

- Fully integrated and operational system.
- Final benchmarking notebook detailing system performance.

---

## Phase 7: Schema Implementation and Persistence Layer

### Goals

* Define and implement database schemas for all core system entities.
* Enable persistent representation of experiments, agents, configurations, tools, and prompts.
* Use SQLite (or SQLAlchemy) as the backing store.

### Deliverables

* `app/schemas/` defining Pydantic models for:

  * `AgentConfig`, `PromptGenerator`, `ToolProvider`, `ScoringProvider`
  * `SystemConfig`, `StateManager`, `ExperimentConfig`, `Session`
  * `AgentPrompt`, `SystemPrompt`, `ContextProvider`, `ModelEngine`
* `app/utilities/schema/create_schema.py` for schema DDL and migration.
* `experiments/config/seed/*.json` or `.yaml` for bootstrapping entries.

### Tables to Implement

* `agent_engine`
* `agent_prompt`, `system_prompt`
* `context_provider`, `tooling_provider`, `file_path`
* `agent_config`, `prompt_generator`, `scoring_provider`
* `state_manager`, `system_config`, `experiment_config`, `series`

Each schema must support loading, saving, and updating entries. External references (e.g. tool IDs, prompt file paths) should be explicitly validated.

---

# CodeCritic Specification (Updated after Phase 7 Completion)

## Summary of Updates
This version of the CodeCritic specification reflects the complete and tested implementation of Phase 7. All seed schemas, enum-safe insertions, Pydantic v2 compatibility improvements, and logging provider integration are now complete and aligned with the runtime architecture.

## Key Changes

### ✅ Enum and Path Serialization
- All enum fields and `Path` objects in both schema seeding and logging are now converted to strings before SQLite insertion.
- This prevents `ProgrammingError` on insertion and ensures logs and data are human-readable.

### ✅ Schema Reflection (Pydantic v2 Compliant)
- Field introspection now uses `__annotations__` instead of `model_fields`.
- Schema generation for SQLite does not require model instantiation.

### ✅ LoggingProvider Implementation
- A centralized `LoggingProvider` was introduced and is now injected across all base classes.
- Logs are validated by type using a `LogType → dataclass` mapping.
- `_serialize()` safely converts dataclass instances and enums.

### ✅ Seed Initialization Pipeline
- `initialize_database(reset=True)` deletes and rebuilds the DB.
- Seed files in `experiments/config/seed/*.json` are automatically loaded and type-checked.
- Schema files have been confirmed present and validated for:
  - `agent_engine`, `agent_prompt`, `system_prompt`
  - `context_provider`, `tooling_provider`, `file_path`
  - `agent_config`, `prompt_generator`, `scoring_provider`
  - `state_manager`, `system_config`, `experiment_config`, `series`

### ✅ All Seed Data Type Constraints Enforced
- Enums are now used in fields such as `system_state`, `agent_role`, and `system_type`
- All `model_dump()` calls conform to Pydantic’s default signature.

### ✅ Logging Schema Consistency
- Logging format uses defined schemas from `log_schemas.py`.
- Logging provider guarantees consistent insertions using validated log models.

## Status
Phase 7 is fully complete and stable.
- ✅ Enum compatibility
- ✅ Schema serialization
- ✅ Logging provider
- ✅ Clean `mypy` and `ruff`
- ✅ Seed tested and loaded
- ✅ Database introspection verified

---

## Phase 8: Registry Seeding and Bootstrap Loader

### Goals

* Load persistent schema entries into in-memory registries.
* Establish an initial working set of system components (agents, tools, prompts, etc.).
* Enable modular extension via `extensions/` folder and registry factories.

### Deliverables

* `app/registries/` + `app/factories/` updated to load from persistent config.
* Bootstrapping logic in `bootstrap.py` or `seed_registries.py`.
* Example registration of one full working system configuration:
  * `GeneratorAgent` using `black`, `docformatter`
  * Prompt and context providers
  * Associated scoring config

### Outcomes

By the end of this phase, any valid schema entry should be fully instantiable from:
- database → registry
- registry → factory
- factory → runtime component

This will complete the foundation for dynamic system reconfiguration, grid-searchable experiments, and runtime injection of custom agent logic.

---

## Phase 9: LoggingProvider and Snapshot Integration

### Goals

* Implement a centralized `LoggingProvider` and snapshot writer.
* Standardize structured logging across all `Base` class hierarchies.
* Enable file-based and SQLite-backed audit trails for all experiment runs.

### Deliverables

* `app/utilities/metadata/logging/logging_provider.py`
* `app/utilities/snapshots/snapshot_writer.py`
* Extend all abstract base classes to inherit from `LoggingProvider`:

  * `ExperimentBase`, `SystemManagerBase`, `StateManagerBase`
  * `AgentBase`, `PromptGeneratorBase`, `ToolProviderBase`, `ScoringProviderBase`

### Outcomes

* Unified logging interface for prompt logs, error logs, scoring logs, etc.
* Snapshots of modified code and contextual metadata written to `experiments/artifacts/snapshots/`.
* Enforced consistency in log structure across all phases of system execution.

---

## Phase 10: Footer Annotation System

### Goals

* Restore footer tagging and metadata injection for traceable, annotated outputs.
* Strip previous metadata, attach new AI-FIRST metadata blocks per round.

### Deliverables

* `app/utilities/metadata/footer/footer_annotation_helper.py`:

  * `strip_metadata_footer(code)`
  * `append_metadata_footer(code, metadata)`
  * `reapply_footer(code, previous_footer, new_metadata)`
* Integrate into all modifying agents (`PatchAgent`, `GeneratorAgent`, etc.)

### Outcomes

* Footer-based traceability across experiments, including:

  * Round and experiment ID
  * Agent and system used
  * Modifications and annotations applied
* Fully reversible and auditable transformations via metadata blocks

---

## Phase 11: SonarCloud Integration

### Goals

* Complete integration with SonarCloud as an external analysis backend.
* Automate scan process via a temporary Git workflow.
* Normalize and log metrics returned by the SonarCloud API.

### Deliverables

* `app/tools/sonarcloud_runner.py`
* Git repo creation, push, scan, and cleanup utility
* Structured report parser to convert scan results to evaluation-ready metrics

### Outcomes

* SonarCloud integration becomes an additional tool in `ToolProvider`
* SonarCloud data included in scoring, quality, and experiment-level logs
* Standardization of tool output metadata for third-party services

---

## Phase 12: Evaluation Notebook

### Goals

* Build an interactive notebook to visualize experiments and system runs.
* Support comparison across agents, configurations, and scoring metrics.
* Validate experiment reproducibility with structured snapshots and logs.

### Deliverables

* `notebooks/evaluation_session_runner.ipynb`
* Matplotlib, seaborn, or Plotly visualizations for experiment logs
* CLI or cell-based triggers for experiment/session replay

### Outcomes

* Clear visual summary of system performance and agent behavior
* Central tool for reviewing experiments and benchmarking CodeCritic systems
* Supports longitudinal research on agent ensembles and iterative improvements

---

**Test Notebook Structure per Phase**

1. **Setup**
    - Environment initialization.
2. **Execution**
    - Task and agent execution.
3. **Validation**
    - Verification of states, outputs, and logging integrity.
4. **Metrics**
    - Computation and validation of evaluation metrics.

**Final Benchmark Notebook**

- Comprehensive evaluation and visualization against benchmarks.
- Detailed metrics performance report.

**Recommendations for Codex Implementation**

- Provide explicit, clear examples.
- Ensure structured and consistent logging practices.
- Conduct stepwise implementations to facilitate easy debugging and iterative refinement.

This document concludes the comprehensive guide to executing and optimizing CodeCritic experiments.