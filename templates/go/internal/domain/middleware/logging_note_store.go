// Package middleware holds decorators for the ports. The composition root
// applies them: mandatory ones once to the real adapter, optional ones per slice.
package middleware

import (
	"context"

	"__GO_MODULE__/internal/domain"
	"__GO_MODULE__/internal/utilities"
)

// LoggingNoteStore logs each save. It is mandatory middleware.
type LoggingNoteStore struct {
	base   domain.NoteStore
	logger utilities.Logger
}

func NewLoggingNoteStore(base domain.NoteStore, logger utilities.Logger) LoggingNoteStore {
	return LoggingNoteStore{base: base, logger: logger}
}

func (s LoggingNoteStore) AllNotes(ctx context.Context) ([]domain.Note, error) {
	return s.base.AllNotes(ctx)
}

func (s LoggingNoteStore) Save(ctx context.Context, note domain.Note) error {
	if err := s.base.Save(ctx, note); err != nil {
		return err
	}
	s.logger.Info("note saved", "id", string(note.ID))
	return nil
}
