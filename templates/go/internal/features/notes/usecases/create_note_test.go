package usecases_test

import (
	"context"
	"errors"
	"path/filepath"
	"slices"
	"testing"
	"time"

	"__GO_MODULE__/internal/adapters/filestore"
	"__GO_MODULE__/internal/domain"
	"__GO_MODULE__/internal/features/notes/usecases"
	"__GO_MODULE__/internal/testsupport"
)

func newStore(t *testing.T) *filestore.NoteStore {
	return filestore.New(filepath.Join(t.TempDir(), "notes.json"))
}

func TestCreatedNoteGetsIDAndTimeFromThePortsAndIsStored(t *testing.T) {
	store := newStore(t)
	now := time.Date(2025, 3, 1, 9, 0, 0, 0, time.UTC)
	createNote := usecases.NewCreateNote(store, testsupport.NewFakeClock(now), &testsupport.SequentialIDs{})

	note, err := createNote.Run(context.Background(), "Groceries")

	if err != nil || note.ID != "id-001" || !note.CreatedAt.Equal(now) {
		t.Fatalf("Run() = %+v, %v", note, err)
	}
	if stored, err := store.AllNotes(context.Background()); err != nil || !slices.Equal(stored, []domain.Note{note}) {
		t.Fatalf("stored %v, %v; want [%v]", stored, err, note)
	}
}

func TestInvalidTitleIsNotStored(t *testing.T) {
	store := newStore(t)
	createNote := usecases.NewCreateNote(store, testsupport.NewFakeClock(time.Unix(0, 0)), &testsupport.SequentialIDs{})

	_, err := createNote.Run(context.Background(), "")

	if !errors.Is(err, domain.ErrTitleEmpty) {
		t.Fatalf("err = %v; want ErrTitleEmpty", err)
	}
	if stored, err := store.AllNotes(context.Background()); err != nil || len(stored) != 0 {
		t.Fatalf("stored %v, %v; want nothing", stored, err)
	}
}

func TestFailedSaveReachesTheCaller(t *testing.T) {
	offline := errors.New("offline")
	createNote := usecases.NewCreateNote(testsupport.FailingNoteStore{Err: offline},
		testsupport.NewFakeClock(time.Unix(0, 0)), &testsupport.SequentialIDs{})

	if _, err := createNote.Run(context.Background(), "Groceries"); !errors.Is(err, offline) {
		t.Fatalf("err = %v; want offline", err)
	}
}
