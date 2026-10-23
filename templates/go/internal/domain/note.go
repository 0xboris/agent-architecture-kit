package domain

import (
	"errors"
	"strings"
	"time"
	"unicode/utf8"
)

type NoteID string

type Note struct {
	ID        NoteID
	Title     NoteTitle
	CreatedAt time.Time
}

const MaxTitleLength = 200

var (
	ErrTitleEmpty   = errors.New("note title is empty")
	ErrTitleTooLong = errors.New("note title is too long")
)

// NoteTitle follows the title rules. The only way to create one is
// NewNoteTitle; treat the zero value as invalid.
type NoteTitle struct {
	value string
}

func NewNoteTitle(raw string) (NoteTitle, error) {
	trimmed := strings.TrimSpace(raw)
	switch {
	case trimmed == "":
		return NoteTitle{}, ErrTitleEmpty
	case utf8.RuneCountInString(trimmed) > MaxTitleLength:
		return NoteTitle{}, ErrTitleTooLong
	}
	return NoteTitle{value: trimmed}, nil
}

func (t NoteTitle) String() string {
	return t.value
}
