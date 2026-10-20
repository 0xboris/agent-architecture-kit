package filestore_test

import (
	"context"
	"path/filepath"
	"slices"
	"testing"
	"time"

	"__GO_MODULE__/internal/adapters/filestore"
	"__GO_MODULE__/internal/domain"
	"__GO_MODULE__/internal/testsupport"
)

// The adapter is tested against the real file system, in t.TempDir().
func newStore(t *testing.T) *filestore.NoteStore {
	return filestore.New(filepath.Join(t.TempDir(), "notes.json"))
}

var start = time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC)

func TestNewStoreListsNoNotes(t *testing.T) {
	notes, err := newStore(t).AllNotes(context.Background())
	if err != nil || len(notes) != 0 {
		t.Fatalf("AllNotes() = %v, %v; want no notes", notes, err)
	}
}

func TestSavedNoteIsListed(t *testing.T) {
	store := newStore(t)
	note := testsupport.SampleNote(1, start)
	if err := store.Save(context.Background(), note); err != nil {
		t.Fatal(err)
	}
	notes, err := store.AllNotes(context.Background())
	if err != nil || !slices.Equal(notes, []domain.Note{note}) {
		t.Fatalf("AllNotes() = %v, %v; want [%v]", notes, err, note)
	}
}

func TestSavingTheSameIDReplacesTheNote(t *testing.T) {
	store := newStore(t)
	original := testsupport.SampleNote(1, start)
	title, err := domain.NewNoteTitle("Changed")
	if err != nil {
		t.Fatal(err)
	}
	replacement := domain.Note{ID: original.ID, Title: title, CreatedAt: start}
	if err := store.Save(context.Background(), original); err != nil {
		t.Fatal(err)
	}
	if err := store.Save(context.Background(), replacement); err != nil {
		t.Fatal(err)
	}
	notes, err := store.AllNotes(context.Background())
	if err != nil || !slices.Equal(notes, []domain.Note{replacement}) {
		t.Fatalf("AllNotes() = %v, %v; want [%v]", notes, err, replacement)
	}
}
