package app

import (
	"net/http"

	"__GO_MODULE__/internal/domain"
	"__GO_MODULE__/internal/domain/middleware"
	"__GO_MODULE__/internal/utilities"
)

type Dependencies struct {
	NoteStore domain.NoteStore
	Clock     domain.Clock
	IDs       domain.IDGenerator
	Logger    utilities.Logger
}

type App struct {
	deps Dependencies
	mux  *http.ServeMux

	noteStore domain.NoteStore
}

func New(deps Dependencies) *App {
	app := &App{
		deps:      deps,
		mux:       http.NewServeMux(),
		noteStore: middleware.NewLoggingNoteStore(deps.NoteStore, deps.Logger),
	}
	app.wireNotes()
	return app
}

func (a *App) Handler() http.Handler {
	return a.mux
}
