package domain_test

import (
	"slices"
	"testing"
	"time"

	"__GO_MODULE__/internal/domain"
	"__GO_MODULE__/internal/testsupport"
)

func TestNewestNoteComesFirst(t *testing.T) {
	start := time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC)
	older := testsupport.SampleNote(1, start)
	newer := testsupport.SampleNote(2, start.Add(time.Hour))
	if got := domain.NewestFirst([]domain.Note{older, newer}); !slices.Equal(got, []domain.Note{newer, older}) {
		t.Fatalf("NewestFirst() = %v", got)
	}
}

func TestNotesWithTheSameTimeAreOrderedByID(t *testing.T) {
	start := time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC)
	first := testsupport.SampleNote(1, start)
	second := testsupport.SampleNote(2, start)
	if got := domain.NewestFirst([]domain.Note{second, first}); !slices.Equal(got, []domain.Note{first, second}) {
		t.Fatalf("NewestFirst() = %v", got)
	}
}
