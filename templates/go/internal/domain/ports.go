package domain

import (
	"context"
	"time"
)

type NoteStore interface {
	AllNotes(ctx context.Context) ([]Note, error)
	Save(ctx context.Context, note Note) error
}

type Clock interface {
	Now() time.Time
}

type IDGenerator interface {
	NewID() string
}
