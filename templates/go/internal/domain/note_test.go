package domain_test

import (
	"errors"
	"strings"
	"testing"

	"__GO_MODULE__/internal/domain"
)

func TestNoteTitleIsTrimmed(t *testing.T) {
	title, err := domain.NewNoteTitle("  Groceries  ")
	if err != nil || title.String() != "Groceries" {
		t.Fatalf("NewNoteTitle() = %q, %v; want Groceries", title, err)
	}
}

func TestEmptyNoteTitleIsRejected(t *testing.T) {
	if _, err := domain.NewNoteTitle("   "); !errors.Is(err, domain.ErrTitleEmpty) {
		t.Fatalf("err = %v; want ErrTitleEmpty", err)
	}
}

func TestTooLongNoteTitleIsRejected(t *testing.T) {
	tooLong := strings.Repeat("a", domain.MaxTitleLength+1)
	if _, err := domain.NewNoteTitle(tooLong); !errors.Is(err, domain.ErrTitleTooLong) {
		t.Fatalf("err = %v; want ErrTitleTooLong", err)
	}
}
