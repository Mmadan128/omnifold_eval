# Project Proposal for CERN-HSF
## Standardizing Publication of OmniFold Unfolding Results

**Contributor:** Mohit Madan  
**Email:** mohitmadan128@gmail.com  
**Country of Residence:** India  
**Timezone:** India/UTC+5:30, Indian Standard Time  
**Degree:** Bachelor of Technology in CST, 2028  
**Primary Languages:** English and Hindi  
**Social Handle:** [LinkedIn](https://www.linkedin.com/in/mohit-madan-b8447a313/) | [GitHub](https://github.com/Mmadan128)  
**Evaluation Task:** [Mmadan128/omnifold_eval](https://github.com/Mmadan128/omnifold_eval)

---

### Table of Contents
* [1. Overview](#1-overview)
    * [1.1 Project Synopsis](#11-project-synopsis)
    * [1.2 State of the Art and Background](#12-state-of-the-art-and-background)
    * [1.3 My Direction](#13-my-direction)
    * [1.4 Identified Gaps](#14-identified-gaps)
* [2. Goals and Deliverables](#2-goals-and-deliverables)
    * [2.1 Strict JSON Metadata Schema](#21-strict-json-metadata-schema)
    * [2.2 Standardized HDF5 Container Format](#22-standardized-hdf5-container-format)
    * [2.3 The omnifold-pub Python Package](#23-the-omnifold-pub-python-package)
    * [2.4 Workflow Validation](#24-end-to-end-workflow-validation)
* [3. Work Plan and Timeline](#3-work-plan-and-timeline)
* [4. Past Experience](#4-past-experience)
* [5. Availability and Commitments](#5-availability-and-other-commitments)

---

<a name="1-overview"></a>
### 1. Overview

#### 1.1 Project Synopsis
In my evaluation task, I inspected the three pseudodata files and found practical reuse issues: missing metadata, inconsistent bootstrap columns, and unclear normalization. Bootstrap counts are not uniform across files, so a naive loop over `weights_bootstrap_mc_N` can fail unless this is declared up front. This proposal turns those observations into a concrete implementation plan: a strict metadata schema, a predictable HDF5 layout, and a Python API for reading, writing, and validation. The target outcome is OmniFold outputs that another analyst can use immediately without reverse-engineering internals.

#### 1.2 State of the Art and Background
OmniFold outputs per-event weights instead of fixed binned histograms, which is useful for reinterpretation and post-publication studies. The current gap is publication, not training: there is no shared standard for storing these weights, documenting their meaning, and exposing them through tooling. In practice, arrays such as `weights_nominal` and `weight_mc` are often shared without machine-readable context (units, selections, normalization, and systematic conventions). Without that context, downstream users cannot safely automate checks or integrate results into HEPData workflows.

#### 1.3 My Direction
I will first lock down metadata requirements using a JSON Schema that enforces units, event-selection records, and systematic/bootstrap declarations. Then I will map this into a structured HDF5 container with explicit groups for observables and weights, while embedding validated metadata in `file.attrs['omnifold_metadata']`. On top of that, I will implement `omnifold-pub` modules for I/O, validation, and analysis utilities so users can load files safely, detect malformed inputs early, and compute observables with consistent uncertainty handling.

#### 1.4 Identified Gaps
The full technical details are documented in my evaluation deliverables. The main blockers for reuse are:

1. **Silent Failures on Missing Bootstrap Replicas** The three files contain different numbers of bootstrap replicas, including one file with none. A standard analysis loop can throw a KeyError or silently drop events if this is not handled explicitly. The schema must enforce an explicit n_bootstrap_replicas field so the API knows array bounds before loading data into memory.

2. **Unexplained Normalization Weights** The weights in all three files have a shared normalization behavior, but there is no record of what convention that represents. Calling `np.histogram(..., weights=...)` without this context yields ambiguous integrals. The standard should require explicit normalization metadata, including a declared convention and `sum_of_weights`.

3. **Missing Event Selection Cuts** The HDF5 files contain no record of the generator-level cuts or jet algorithms applied before running OmniFold. If a user applies these weights to a new Monte Carlo sample with different baseline cuts, the physics will be incorrect even if the script runs. Event selection cuts must be a mandatory metadata block.

4. **Missing Units for Physics Variables** The observable columns lack unit labels. Passing values with the wrong unit silently corrupts results. Also, complex variables such as N-subjettiness are missing parameter metadata. The schema must enforce strict units and parameter fields for every declared observable.

---

<a name="2-goals-and-deliverables"></a>
### 2. Goals and Deliverables

#### 2.1 Strict JSON Metadata Schema
I will formalize the evaluation YAML draft into a JSON Schema so files can be validated before they are saved or published.
- **Enforcing Data Types:** Require explicit strings for units so they cannot be left blank.
- **Consistent Naming:** Standardize the naming for systematic variations (using regex like ^weight_syst_[a-zA-Z0-9]+_(up|dn)$) to prevent column names from drifting between different experiments.
- **Mandatory Physics Context:** Make generator details (MadGraph/Sherpa version) and event selection cuts mandatory, throwing a ValidationError if a user attempts to save a file without them.
- **Iteration Structure:** Add explicit fields for OmniFold iteration information so users can understand what stage each weight came from.

#### 2.2 Standardized HDF5 Container Format
I will define a structured HDF5 layout optimized for fast I/O and cross-compatibility.
- **Organized Groups:** Replace flat file structures with logical HDF5 groups: /events/observables, /weights/nominal, /weights/systematics, and /weights/bootstraps.
- **Self-Describing Files:** The validated metadata JSON will be serialized and embedded directly into the HDF5 root as `file.attrs['omnifold_metadata']`.
- **Model Archiving Standards:** Define the technical difference between a "Minimal" publication (only kinematics and weights for plotting) versus a "Full" publication (including OmniFold hyperparameters and model checkpoints for retraining).
- **Observable Definitions:** For each observable, store a clear physics name, object definition, phase-space restriction, and unit. Keep binning optional so users can choose custom bins for reinterpretation.

#### 2.3 The omnifold-pub Python Package
I will implement a pip-installable library consisting of three core modules:
- **omnifold_pub.io:** Includes `write_unfolding(data_dict, metadata_dict)` to validate metadata, build the HDF5 structure, and write arrays, plus `read_unfolding(filepath)` to load data and metadata with schema checks.
- **omnifold_pub.validate:** Includes checks such as `check_closure()` and `verify_normalization()` so users can verify physics-level consistency against metadata declarations.
- **omnifold_pub.apply:** Extends my evaluation-task `weighted_histogram` utility with publication-ready plotting and bootstrap-based statistical uncertainty propagation.

#### 2.4 End-to-End Workflow Validation
Once the package reaches >85% test coverage, I will validate the full workflow on the evaluation pseudodata (`multifold.h5`, `multifold_sherpa.h5`, and `multifold_nonDY.h5`). This includes automated normalization and consistency checks plus a reference notebook that reads raw files, converts them to the standard format, and produces an `mplhep` plot with uncertainty bands.
I will define clear pass/fail criteria for closure tests, normalization checks, and iteration stability checks, so validation results are objective and easy to review.

I will also provide a practical HEPData integration path: mapping OmniFold outputs to HEPData records, metadata conventions, and a submission checklist/template.

#### 2.5 Deliverables
This project will be considered successful if:
1. The JSON Schema and HDF5 layout specifications are documented and versioned.
2. The omnifold-pub Python package is published with functional io, validate, and apply modules, backed by solid unit tests.
3. Reference Jupyter notebooks demonstrate a complete end-to-end publication, validation, and reinterpretation workflow using the new standard.
4. Documentation includes a basic HEPData mapping guide and submission checklist.

---

<a name="3-work-plan-and-timeline"></a>
### 3. Work Plan and Timeline

| Phase | Dates | Plan | Weekly Hours |
| :--- | :--- | :--- | :--- |
| **Community Bonding** | May 1-24 | Mentor discussions, schema checks, and repo setup. | - |
| **Week 1-2** | May 25-Jun 6 | Finalize JSON Schema v1.0, allowed variables, and validation rules. | 13.5 |
| **Week 3-4** | Jun 7-20 | Implement HDF5 layout, naming rules, and indexing plan. | 13.5 |
| **Week 5-6** | Jun 21-Jul 4 | Build `write_unfolding`, connect schema validation, and add tests. | 13.5 |
| **Midterm** | Jul 10 | Schema, container format, and write path complete. | - |
| **Week 7-8** | Jul 5-18 | Build `read_unfolding` with metadata extraction and bootstrap handling. | 13.5 |
| **Week 9-10** | Jul 19-Aug 1 | Implement `weighted_histogram` and uncertainty propagation logic. | 13.5 |
| **Week 11-12** | Aug 2-15 | Build validation checks, notebooks, and usage documentation. | 13.5 |
| **Week 13** | Aug 16-24 | Final testing, cleanup, and final submission. | 13 |

---

<a name="4-past-experience"></a>
### 4. Past Experience

#### 4.1 Academic Details
I am pursuing a Bachelor of Technology in Computer Science and Technology at MAIT, Delhi. I work primarily in Python and C++, with hands-on experience in ML and data pipelines using NumPy, PyTorch, and h5py.

#### 4.2 Evaluation Task
I analyzed the provided OmniFold HDF5 pseudodata files and completed three tasks:
- I analyzed internal data structures and identified four critical failure points in physics context and consistency (detailed in Identified Gaps).
- I designed a draft YAML metadata schema specifically structured to resolve these gaps and prevent data corruption.
- I implemented a `weighted_histogram` Python API with 14 unit tests covering edge cases such as negative weights, shape mismatches, empty inputs, and zero-normalization failures.

#### 4.3 Personal Projects & Open Source
- **Hacktoberfest 2025:** Authored and merged 8 pull requests across open-source repositories, which gave me strong practice in review-driven iteration and collaborative Git workflows.
- **Vortex Codec:** A byte-level autoregressive compression engine combining transformer-based byte modeling with range coding for lossless compression. Built with PyTorch, torchac, and CUDA.
- **Feynman AI Tutor:** Fine-tuned a Qwen2.5 1.5B Instruct model using parameter-efficient methods (PEFT) on a structured educational dataset.

---

<a name="5-availability-and-other-commitments"></a>
### 5. Availability and Other Commitments

#### 5.1 Working Hours and Schedule
I can commit approximately 13.5 hours per week for the coding period. On weekdays I am available in the late evenings, and on weekends I have flexible timings. I have no other internships during this period.

#### 5.2 Regular Updates and Meetings
1. I will share written progress updates weekly and push code regularly to GitHub following repository guidelines.
2. I will be available via email, Slack, or any preferred communication platform, and I will attend scheduled mentor meets.

#### 5.3 Post-GSoC
I plan to continue contributing to omnifold-pub after GSoC. I want to stay involved as the HEP community begins adopting the schema for real analyses, helping to maintain the Python package and review incoming issues.