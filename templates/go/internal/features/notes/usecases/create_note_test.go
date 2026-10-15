package usecases_test

import (
	"context"
	"errors"
	"slices"
	"testing"
	"time"

	"__GO_MODULE__/internal/domain"
	"__GO_MODULE__/internal/features/notes/usecases"
	"__GO_MODULE__/internal/testsupport"
)

func TestCreatedNoteGetsIDAndTimeFromThePortsAndIsSaved(t *testing.T) {
	store := &testsupport.StubNoteStore{}
	now := time.Date(2025, 3, 1, 9, 0, 0, 0, time.UTC)
	createNote := usecases.NewCreateNote(store, testsupport.NewFakeClock(now), &testsupport.SequentialIDs{})

	note, err := createNote.Run(context.Background(), "Groceries")

	if err != nil || note.ID != "id-001" || !note.CreatedAt.Equal(now) {
		t.Fatalf("Run() = %+v, %v", note, err)
	}
	if saved := store.Saved(); !slices.Equal(saved, []domain.Note{note}) {
		t.Fatalf("saved %v; want [%v]", saved, note)
	}
}

func TestInvalidTitleIsNotSaved(t *testing.T) {
	store := &testsupport.StubNoteStore{}
	createNote := usecases.NewCreateNote(store, testsupport.NewFakeClock(time.Unix(0, 0)), &testsupport.SequentialIDs{})

	_, err := createNote.Run(context.Background(), "")

	if !errors.Is(err, domain.ErrTitleEmpty) {
		t.Fatalf("err = %v; want ErrTitleEmpty", err)
	}
	if saved := store.Saved(); len(saved) != 0 {
		t.Fatalf("saved %v; want nothing", saved)
	}
}

func TestFailedSaveReachesTheCaller(t *testing.T) {
	offline := errors.New("offline")
	store := &testsupport.StubNoteStore{Err: offline}
	createNote := usecases.NewCreateNote(store, testsupport.NewFakeClock(time.Unix(0, 0)), &testsupport.SequentialIDs{})

	if _, err := createNote.Run(context.Background(), "Groceries"); !errors.Is(err, offline) {
		t.Fatalf("err = %v; want offline", err)
	}
}

func TestNotesAreListedNewestFirst(t *testing.T) {
	start := time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC)
	older := testsupport.SampleNote(1, start)
	newer := testsupport.SampleNote(2, start.Add(time.Hour))
	store := &testsupport.StubNoteStore{Notes: []domain.Note{older, newer}}

	notes, err := usecases.NewListNotes(store).Run(context.Background())

	if err != nil || !slices.Equal(notes, []domain.Note{newer, older}) {
		t.Fatalf("Run() = %v, %v", notes, err)
	}
}
