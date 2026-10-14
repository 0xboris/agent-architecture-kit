// Package usecases holds the use cases of the notes slice. They orchestrate
// only: the rules live in the domain, and storage sits behind ports.
package usecases

import (
	"context"
	"fmt"

	"__GO_MODULE__/internal/domain"
)

type CreateNote struct {
	store domain.NoteStore
	clock domain.Clock
	ids   domain.IDGenerator
}

func NewCreateNote(store domain.NoteStore, clock domain.Clock, ids domain.IDGenerator) CreateNote {
	return CreateNote{store: store, clock: clock, ids: ids}
}

func (u CreateNote) Run(ctx context.Context, rawTitle string) (domain.Note, error) {
	title, err := domain.NewNoteTitle(rawTitle)
	if err != nil {
		return domain.Note{}, err
	}
	note := domain.Note{ID: domain.NoteID(u.ids.NewID()), Title: title, CreatedAt: u.clock.Now()}
	if err := u.store.Save(ctx, note); err != nil {
		return domain.Note{}, fmt.Errorf("save note %s: %w", note.ID, err)
	}
	return note, nil
}
