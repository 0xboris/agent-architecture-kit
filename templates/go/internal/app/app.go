// Package app is the composition root. It applies middleware and wires each
// slice in a wire_<slice>.go file. It holds straight-line wiring only: no
// control flow and no feature code.
package app

import (
	"net/http"

	"__GO_MODULE__/internal/domain"
	"__GO_MODULE__/internal/domain/middleware"
	"__GO_MODULE__/internal/utilities"
)

// Dependencies are the adapters that the service runs with. LiveDependencies
// creates the real ones; the composition test passes stubs.
type Dependencies struct {
	NoteStore domain.NoteStore
	Clock     domain.Clock
	IDs       domain.IDGenerator
	Logger    utilities.Logger
}

type App struct {
	deps Dependencies
	mux  *http.ServeMux

	// Mandatory middleware: applied once here, so no slice receives the bare store.
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
