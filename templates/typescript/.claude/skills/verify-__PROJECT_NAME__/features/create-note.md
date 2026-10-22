# Create a note

A client creates a note by sending its title, and gets the stored note back. The service rejects an empty or a too-long title with a code that the client can show.

## Sub-features

- `create-save` stores a note with a trimmed title, an id, and a creation time.
- `create-empty` rejects an empty title with `title_empty`.
- `create-too-long` rejects a title longer than 200 characters with `title_too_long`.

## How to get to it (user POV)

- `POST /notes` with the JSON body `{"title": "<title>"}`.

## Driving it with scripts/app

Preconditions:

- `$app doctor "$run"` reports `ok`.
- The run's store holds no notes.

- **Create.** Run `$app call "$run" create-save POST /notes '{"title":"  Groceries  "}'`. The status is `201`, and the body has an `id`, `"title":"Groceries"`, and a `createdAt` time.
- **Read back.** Run `$app call "$run" create-read GET /notes`. The status is `200`, and the list holds one note titled `Groceries` with the same `id`.
- **Empty title.** Run `$app call "$run" create-empty POST /notes '{"title":"   "}'`. The status is `422`, and the body's `code` is `title_empty`.
- **Too long.** Run `$app call "$run" create-too-long POST /notes "{\"title\":\"$(printf 'a%.0s' $(seq 201))\"}"`. The status is `422`, and the body's `code` is `title_too_long`.
- **Nothing else stored.** Run `$app call "$run" create-read-after GET /notes`. The list still holds only `Groceries`.

## Gotchas

- The service trims the title. Assert the stored title, not the one you sent.
- A `201` alone is not proof. Read the note back with `GET /notes`.
- The limit counts Unicode code points, not bytes. An emoji with a skin tone is two code points, so it counts as two.
