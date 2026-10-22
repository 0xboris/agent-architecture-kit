# List notes

A client lists every stored note, newest first.

## Sub-features

- `list-empty` returns an empty list when no note is stored.
- `list-order` returns the newest note first.

## How to get to it (user POV)

- `GET /notes`.

## Driving it with scripts/app

Preconditions:

- `$app doctor "$run"` reports `ok`.
- The run's store holds no notes.

- **Empty.** Run `$app call "$run" list-empty GET /notes`. The status is `200`, and the body is `[]`.
- **Two notes.** Run `$app call "$run" list-first POST /notes '{"title":"First"}'`, then `sleep 1`, then `$app call "$run" list-second POST /notes '{"title":"Second"}'`. Both statuses are `201`.
- **Order.** Run `$app call "$run" list-order GET /notes`. The status is `200`, and `Second` comes before `First`.

## Gotchas

- The service orders two notes created in the same millisecond by id, not by the order of the requests. Wait a second between the two creates.
