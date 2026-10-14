package usecases_test

import (
	"context"
	"errors"
	"testing"
	"time"

	"__GO_MODULE__/internal/domain"
	"__GO_MODULE__/internal/features/notes/usecases"
	"__GO_MODULE__/internal/testsupport"
)

func TestCreatedNoteGetsIDAndTimeFromThePorts(t *testing.T) {
	store := testsupport.NewFakeNoteStore()
	now := time.Date(2025, 3, 1, 9, 0, 0, 0, time.UTC)
	createNote := usecases.NewCreateNote(store, testsupport.NewFakeClock(now), &testsupport.SequentialIDs{})

	note, err := createNote.Run(context.Background(), "Groceries")

	if err != nil || note.ID != "id-001" || !note.CreatedAt.Equal(now) {
		t.Fatalf("Run() = %+v, %v", note, err)
	}
	if notes, _ := store.AllNotes(context.Background()); len(notes) != 1 || notes[0] != note {
		t.Fatalf("stored notes = %v", notes)
	}
}

func TestInvalidTitleIsNotStored(t *testing.T) {
	store := testsupport.NewFakeNoteStore()
	createNote := usecases.NewCreateNote(store, testsupport.NewFakeClock(time.Unix(0, 0)), &testsupport.SequentialIDs{})

	_, err := createNote.Run(context.Background(), "")

	if !errors.Is(err, domain.ErrTitleEmpty) {
		t.Fatalf("err = %v; want ErrTitleEmpty", err)
	}
	if notes, _ := store.AllNotes(context.Background()); len(notes) != 0 {
		t.Fatalf("stored notes = %v; want none", notes)
	}
}

func TestNotesAreListedNewestFirst(t *testing.T) {
	start := time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC)
	older := testsupport.SampleNote(1, start)
	newer := testsupport.SampleNote(2, start.Add(time.Hour))

	notes, err := usecases.NewListNotes(testsupport.NewFakeNoteStore(older, newer)).Run(context.Background())

	if err != nil || len(notes) != 2 || notes[0] != newer {
		t.Fatalf("Run() = %v, %v", notes, err)
	}
}
