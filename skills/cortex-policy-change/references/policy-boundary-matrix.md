# Policy Boundary Matrix

## Classification rubric

| Target layer | Use when | Avoid when |
| --- | --- | --- |
| Policy (`policies/`) | Rule is durable, testable, and safety/compliance-critical | Rule is temporary, subjective, or implementation tactic |
| Playbook (`playbooks/`) | Workflow sequence and operational procedure | Statement is a normative invariant that must always hold |
| Skill (`skills/`) | Tool-specific execution steps and command choreography | Content must be canonical governance authority |
| Spec/Contract (`specs/`, `contracts/`) | Machine-checkable semantics and schema/API behavior | Guidance is prose-only and not enforceable by contract |

## Rule of thumb

1. Put "what must be true" in policy.
2. Put "how to do it with current tools" in skills/playbooks.
3. Put "how systems must behave" in spec/contract.

## Examples

- Good policy: "Governance-impacting closeout must pass required gate bundle."
- Good skill content: "Run `./scripts/quality_gate_ci_v0.sh`, then clean incidental generated timestamp drift."
- Bad policy content: "Always use tool X for this week of implementation."
