# Viva Guide

## 30-second explanation

RiskRoute is a delivery-delay decision-support prototype. A gradient-boosted classifier predicts delay probability. A second algorithm searches only allowed operational changes—reducing vehicle load, leaving earlier, or adding schedule buffer—and returns minimal scenarios that reduce risk below a selected threshold.

## Questions you should be able to answer

### Why is this a full-stack project?
The React frontend handles interaction, FastAPI provides REST endpoints, the ML
module performs prediction and counterfactual search, and SQLite stores accounts
and prediction history.

### Why use FastAPI?
FastAPI validates typed request data, generates API documentation, and keeps the
user interface separate from the machine-learning logic.

### Why use SQLite?
SQLite requires no separate database server, making the prototype easy to run
while still demonstrating persistent relational storage.

### Why not stop at prediction?
A prediction tells the user what may happen. A counterfactual gives a possible action that could change the model outcome.

### What is the research gap?
Many predictive systems optimize accuracy but do not test whether their recommendations are feasible. This project evaluates constraint satisfaction together with validity, sparsity, cost, and runtime.

### What is immutable?
Distance, traffic, weather, driver experience, priority status. They represent context for one decision and are not altered by the intervention engine.

### Why gradient boosting?
Delivery risk contains non-linear effects and interactions, such as distance becoming more important under heavy traffic. Tree boosting handles these patterns without requiring a deep neural network.

### How are counterfactuals generated?
The program enumerates a bounded grid of realistic actions, predicts every candidate, filters candidates that meet the target, assigns a normalized action cost, and returns low-cost diverse solutions.

### Is the dataset real?
No. It is a reproducible synthetic teaching dataset. This is a stated limitation, not hidden. The next research step is validation on operational data.

### What makes the work reproducible?
Fixed random seeds, saved requirements, generated dataset, separate training
and evaluation scripts, exported metrics, SQLite history, and a unit test.

## Honest limitations

- Synthetic data cannot establish real-world effectiveness.
- The search grid is small and may miss a better continuous solution.
- Model predictions are associations, not causal guarantees.
- Costs are normalized weights, not actual company expenses.
- Traffic is fixed rather than recalculated after departure-time changes.

## Future work

- connect live traffic and weather data;
- learn intervention costs from operations;
- compare grid search with DiCE or genetic optimization;
- add causal constraints;
- test user trust and usefulness with logistics planners.
