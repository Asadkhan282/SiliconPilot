\# SiliconPilot



SiliconPilot is an autonomous RTL analysis, repair, and verification agent for Verilog/SystemVerilog.



It analyzes broken RTL, classifies diagnostics, applies targeted repair strategies, re-runs lint verification, and performs functional simulation.



\## Live Demo



Public Streamlit demo:



https://siliconpilot-4yhyjfguuv2kntvvcn37oj.streamlit.app



\## What SiliconPilot Does



SiliconPilot currently supports:



\- Verilog/SystemVerilog RTL analysis

\- Verilator lint diagnostics

\- Diagnostic classification

\- Automatic repair strategy selection

\- Sequential assignment repair

\- Width mismatch repair

\- Missing combinational default repair

\- Unused internal signal cleanup

\- Undriven signal repair

\- Iterative re-verification

\- Icarus Verilog functional simulation

\- Batch validation

\- Public Streamlit interface



\## Workflow



```text

RTL Upload

&#x20;   ↓

Verilator Analysis

&#x20;   ↓

Diagnostic Classification

&#x20;   ↓

Repair Strategy Selection

&#x20;   ↓

Autonomous RTL Repair

&#x20;   ↓

Verilator Re-Verification

&#x20;   ↓

Functional Simulation

&#x20;   ↓

VERIFIED\_PASS / VERIFIED\_WITH\_REVIEW

