package testsupport

import (
	"context"
	"testing"
	"time"

	"__GO_MODULE__/internal/domain"
)

// NoteStoreContract checks the behavior that every domain.NoteStore must have.
// The fake runs it in fakes_test.go and the filestore adapter in its own
// tests, so the fake cannot drift from the real store.
func NoteStoreContract(t *testing.T, newStore func(t *testing.T) domain.NoteStore) {
	ctx := context.Background()
	start := time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC)

	t.Run("an empty store lists no notes", func(t *testing.T) {
		notes, err := newStore(t).AllNotes(ctx)
		if err != nil || len(notes) != 0 {
			t.Fatalf("AllNotes() = %v, %v; want no notes", notes, err)
		}
	})

	t.Run("a saved note is listed", func(t *testing.T) {
		store := newStore(t)
		note := SampleNote(1, start)
		if err := store.Save(ctx, note); err != nil {
			t.Fatal(err)
		}
		notes, err := store.AllNotes(ctx)
		if err != nil || len(notes) != 1 || notes[0] != note {
			t.Fatalf("AllNotes() = %v, %v; want [%v]", notes, err, note)
		}
	})

	t.Run("saving the same id replaces the note", func(t *testing.T) {
		store := newStore(t)
		original := SampleNote(1, start)
		title, err := domain.NewNoteTitle("Changed")
		if err != nil {
			t.Fatal(err)
		}
		replacement := domain.Note{ID: original.ID, Title: title, CreatedAt: start}
		if err := store.Save(ctx, original); err != nil {
			t.Fatal(err)
		}
		if err := store.Save(ctx, replacement); err != nil {
			t.Fatal(err)
		}
		notes, err := store.AllNotes(ctx)
		if err != nil || len(notes) != 1 || notes[0] != replacement {
			t.Fatalf("AllNotes() = %v, %v; want [%v]", notes, err, replacement)
		}
	})
}
