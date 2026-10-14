// Package ui holds the HTTP handlers of the notes slice. It turns requests
// into use case calls and results into responses.
package ui

import (
	"errors"
	"fmt"
	"net/http"
	"time"

	"__GO_MODULE__/internal/domain"
	"__GO_MODULE__/internal/features/notes/usecases"
	"__GO_MODULE__/internal/sharedui/httpjson"
	"__GO_MODULE__/internal/utilities"
)

type Handler struct {
	createNote usecases.CreateNote
	listNotes  usecases.ListNotes
	logger     utilities.Logger
}

func NewHandler(createNote usecases.CreateNote, listNotes usecases.ListNotes, logger utilities.Logger) Handler {
	return Handler{createNote: createNote, listNotes: listNotes, logger: logger}
}

func (h Handler) Register(mux *http.ServeMux) {
	mux.HandleFunc("GET /notes", h.list)
	mux.HandleFunc("POST /notes", h.create)
}

// The wire format. It stays in this package and maps to and from domain types.
type noteResponse struct {
	ID        string    `json:"id"`
	Title     string    `json:"title"`
	CreatedAt time.Time `json:"createdAt"`
}

type createRequest struct {
	Title string `json:"title"`
}

func toResponse(note domain.Note) noteResponse {
	return noteResponse{ID: string(note.ID), Title: note.Title.String(), CreatedAt: note.CreatedAt}
}

func (h Handler) list(w http.ResponseWriter, r *http.Request) {
	notes, err := h.listNotes.Run(r.Context())
	if err != nil {
		h.logger.Error("list notes failed", "error", err)
		httpjson.Error(w, http.StatusInternalServerError, "notes_unavailable", "The notes could not be loaded.")
		return
	}
	responses := make([]noteResponse, 0, len(notes))
	for _, note := range notes {
		responses = append(responses, toResponse(note))
	}
	httpjson.Write(w, http.StatusOK, responses)
}

func (h Handler) create(w http.ResponseWriter, r *http.Request) {
	var request createRequest
	if err := httpjson.Read(r, &request); err != nil {
		httpjson.Error(w, http.StatusBadRequest, "invalid_json", "The request body is not valid JSON.")
		return
	}
	note, err := h.createNote.Run(r.Context(), request.Title)
	switch {
	case errors.Is(err, domain.ErrTitleEmpty):
		httpjson.Error(w, http.StatusUnprocessableEntity, "title_empty", "Enter a title.")
	case errors.Is(err, domain.ErrTitleTooLong):
		httpjson.Error(w, http.StatusUnprocessableEntity, "title_too_long",
			fmt.Sprintf("Use at most %d characters.", domain.MaxTitleLength))
	case err != nil:
		h.logger.Error("create note failed", "error", err)
		httpjson.Error(w, http.StatusInternalServerError, "note_not_saved", "The note could not be saved.")
	default:
		httpjson.Write(w, http.StatusCreated, toResponse(note))
	}
}
