package middleware

import (
	"context"

	"__GO_MODULE__/internal/domain"
	"__GO_MODULE__/internal/utilities"
)

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
