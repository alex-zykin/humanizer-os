# Real-world demo provenance

The files `real-world-ai-before.md` and `real-world-ai-after.md` form a reproducible editorial demo built from a machine-generated article in the **Human Detectors** research dataset by Jenna Russell, Marzena Karpinska, and Mohit Iyyer.

Dataset record:

- repository: `jenna-russell/human_detectors`
- dataset: `human_detectors.json`
- record id: `4`
- generation model: `gpt-4o`
- prompt id: `2`
- ground truth: `AI-generated`
- expert majority vote: `Machine-Generated`
- reference title: `When the first warm-blooded dinosaurs roamed Earth`
- reference source metadata: Associated Press
- reference URL: `https://apnews.com/article/warm-blooded-dinosaur-jurassic-fossil-68d21d8778440825ed8dccfd8efb5186`

The `author` and `source` fields in the research dataset describe the human reference article. They are **not** an authorship claim for the machine-generated text used in this demo.

HumanizerOS rewrites only the machine-generated dataset sample. It does not reproduce the paired human-written Associated Press article.

The Human Detectors repository is MIT licensed. This demo preserves the generated sample's claims and direct quotations for an editing comparison; it does not independently verify their truth. Fact Guard checks consistency between source and rewrite, not factual accuracy.

Research citation:

Jenna Russell, Marzena Karpinska, and Mohit Iyyer. “People who frequently use ChatGPT for writing tasks are accurate and robust detectors of AI-generated text.” arXiv:2501.15654 (2025).
