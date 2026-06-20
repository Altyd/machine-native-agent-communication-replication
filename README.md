# Machine-Native Agent Communication Replication Package

This folder contains the paper draft, browser harnesses, and raw exported results for the machine-native agent communication experiments.

## Contents

- `paper/machine_native_agent_communication.docx` - edited paper draft.
- `data/battery_gpt4o_mini.json` - original 160-run validation battery.
- `data/battery_gpt54_mini.json` - 160-run GPT-5.4-mini replication battery.
- `data/pilot_*.json` - five pilot experiment exports.
- `harnesses/*.html` - browser harnesses used to run the pilots and validation battery.
- `analysis/analyze_batteries.py` - no-dependency script that regenerates battery aggregates.

## Replication Note

The GPT-5.4-mini battery produced all 160 expected trials with no API failures. Eight NATURAL runs emitted a final decision before receiving any Tasker response. These are labeled as premature finalization / invalid communication runs and are excluded from the adjusted NATURAL aggregate.

Run:

```bash
python3 analysis/analyze_batteries.py
```

from this folder to print raw and adjusted battery summaries.

## Naming

The files in this package use descriptive names for publication. The raw JSON payloads are copied unchanged from the original exports.
