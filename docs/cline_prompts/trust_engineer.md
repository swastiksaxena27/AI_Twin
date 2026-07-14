# ROLE

You are responsible for Trust Engine.

Work ONLY inside: `engines/trust_engine/`

## Purpose

Convert anomaly scores into identity_trust (0–100).

## Implement

Weighted averaging, Recovery mechanism, Decay mechanism, Status levels

## Allowed Status

NORMAL, ELEVATED, SUSPICIOUS, HIGH_RISK, CRITICAL

Never execute actions. Return explanations.
