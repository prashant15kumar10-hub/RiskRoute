# Project Proposal

## Title

**RiskRoute: A Constraint-Aware Explainable AI Framework for Counterfactual Decision Optimization in Intelligent Logistics**

## Problem statement

Delivery-delay models generally provide a risk estimate but do not directly state what feasible operational changes could lower the predicted risk. The project builds a two-stage decision-support system: prediction followed by constrained counterfactual search.

## Research question

Can a constraint-aware counterfactual search produce valid, sparse, feasible, and computationally practical interventions for delivery-delay predictions?

## Objectives

1. Train a non-linear delay-risk classifier.
2. Separate mutable operational variables from immutable context.
3. Generate what-if scenarios under explicit constraints.
4. rank valid scenarios using normalized intervention cost.
5. Evaluate predictive and counterfactual performance.
6. Deliver an interactive demonstration.

## Scope

The prototype changes only vehicle load, departure time, and schedule buffer. It does not optimize routing, assign drivers, or claim causal effects.

## Expected outcomes

- trained prediction model;
- responsive React dashboard and FastAPI REST API;
- SQLite authentication and simulation history;
- multiple feasible what-if scenarios;
- evaluation of validity, sparsity, proximity, constraint satisfaction, and runtime;
- reproducible code and paper draft.
