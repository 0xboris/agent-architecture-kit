package testsupport

import (
	"context"
	"slices"
	"sync"

	"__GO_MODULE__/internal/domain"
)

// StubNoteStore is a domain.NoteStore that returns what a test sets and
// records the notes it receives. It has no behavior of its own: a test sets
// Notes and Err to the results it wants the code under test to handle.
type StubNoteStore struct {
	Notes []domain.Note // returned by AllNotes
	Err   error         // returned by every call when set

	mu    sync.Mutex
	saved []domain.Note
}

var _ domain.NoteStore = (*StubNoteStore)(nil)

func (s *StubNoteStore) AllNotes(ctx context.Context) ([]domain.Note, error) {
	if s.Err != nil {
		return nil, s.Err
	}
	return slices.Clone(s.Notes), nil
}

func (s *StubNoteStore) Save(ctx context.Context, note domain.Note) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.saved = append(s.saved, note)
	return s.Err
}

// Saved returns the notes passed to Save, in order.
func (s *StubNoteStore) Saved() []domain.Note {
	s.mu.Lock()
	defer s.mu.Unlock()
	return slices.Clone(s.saved)
}
