---
name: new-port
description: Adds a port and its adapter in the shape of the reference slice. Use when domain or use case code needs storage, the network, the time, ids, randomness, the file system, or a platform or third-party service.
---

1. Check `docs/architecture/modules.md` and the domain's ports first. Reuse a port that already covers the need, and add a method to it if the method belongs to the same capability.
2. Declare the port in the domain, next to the reference slice's ports. Name it for what the use case needs, such as `BudgetStore` or `PaymentGateway`, not for the technology behind it. Declare it in a file that `portFiles` in `architecture.json` lists, so the check knows it is a port.
3. Declare the operations with domain types only. Storage records, wire payloads, and SDK types stay inside the adapter.
4. Make each operation's results a closed set of cases: a union or enum of outcomes, or a closed set of errors. Callers and their tests then know every case to handle.
5. Implement the port in an adapter module. Map outside data to domain types inside the adapter.
6. Test the adapter against the real system: a real database, a temporary directory, or recorded responses from a remote service. Cover each case that the port promises. When the adapter stores data, commit a file in the stored format and a test that loads it.
7. In the tests of code that calls the port, use the real adapter when it runs locally and fast. When it is remote, slow, or nondeterministic, or a test needs it to fail, add a small fake or a failing implementation to test support, like the reference slice's failing store.
8. Add the real implementation to the composition root's live dependencies.
9. Run `./check`.
