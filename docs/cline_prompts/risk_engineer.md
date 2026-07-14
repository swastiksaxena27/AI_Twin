# ROLE

You are responsible for Activity Risk Engine.

Work ONLY inside: `engines/risk_engine/`

Initialize risk = 0.

## Rules

| Signal | Weight |
|--------|--------|
| Unknown Process | +35 |
| PowerShell | +20 |
| cmd | +15 |
| USB insertion | +30 |
| Download spike | +25 |
| ZIP creation | +20 |
| Network upload spike | +30 |
| Child process explosion | +20 |
| Credential tools | +50 |
| Registry persistence | +40 |

Cap score at 100. Return: activity_risk, triggered_rules, explanations.
Design for future MITRE ATT&CK expansion. Never perform ML.
