Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional

# Workbench Project Graph Model

Workbench may present project graph snapshots and query results as an inspection aid. It may filter by workspace, module, app, command, provider, service, capability, pack, artifact, or evidence packet.

Workbench must not mutate source truth through the graph, promote graph facts into authority, hide incomplete query status, or override contracts, manifests, registries, descriptors, tests, or evidence packets. If Workbench later adds a Project Graph Explorer, it must show the graph as a derived index and preserve source references for displayed facts.

This task does not implement the Project Graph Explorer, graph viewer UI, runtime graph service, or generator. It only defines the contract model and fixtures that a future viewer can consume.
