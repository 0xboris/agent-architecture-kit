package usecases

import (
	"context"
	"fmt"

	"__GO_MODULE__/internal/domain"
)

type ListNotes struct {
	store domain.NoteStore
}

func NewListNotes(store domain.NoteStore) ListNotes {
	return ListNotes{store: store}
}

func (u ListNotes) Run(ctx context.Context) ([]domain.Note, error) {
	notes, err := u.store.AllNotes(ctx)
	if err != nil {
		return nil, fmt.Errorf("load notes: %w", err)
	}
	return domain.NewestFirst(notes), nil
}
