package testsupport

import (
	"context"

	"__GO_MODULE__/internal/domain"
)

// FailingNoteStore returns Err from every call, so a test can reach the error paths.
type FailingNoteStore struct {
	Err error
}

var _ domain.NoteStore = FailingNoteStore{}

func (s FailingNoteStore) AllNotes(ctx context.Context) ([]domain.Note, error) {
	return nil, s.Err
}

func (s FailingNoteStore) Save(ctx context.Context, note domain.Note) error {
	return s.Err
}
