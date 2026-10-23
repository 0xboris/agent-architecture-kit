package usecases_test

import (
	"context"
	"slices"
	"testing"
	"time"

	"__GO_MODULE__/internal/domain"
	"__GO_MODULE__/internal/features/notes/usecases"
	"__GO_MODULE__/internal/testsupport"
)

func TestNotesAreListedNewestFirst(t *testing.T) {
	store := newStore(t)
	start := time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC)
	older := testsupport.SampleNote(1, start)
	newer := testsupport.SampleNote(2, start.Add(time.Hour))
	for _, note := range []domain.Note{older, newer} {
		if err := store.Save(context.Background(), note); err != nil {
			t.Fatal(err)
		}
	}

	notes, err := usecases.NewListNotes(store).Run(context.Background())

	if err != nil || !slices.Equal(notes, []domain.Note{newer, older}) {
		t.Fatalf("Run() = %v, %v", notes, err)
	}
}
