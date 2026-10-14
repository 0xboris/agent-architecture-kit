package app

import (
	notesui "__GO_MODULE__/internal/features/notes/ui"
	notesusecases "__GO_MODULE__/internal/features/notes/usecases"
)

func (a *App) wireNotes() {
	notesui.NewHandler(
		notesusecases.NewCreateNote(a.noteStore, a.deps.Clock, a.deps.IDs),
		notesusecases.NewListNotes(a.noteStore),
		a.deps.Logger,
	).Register(a.mux)
}
