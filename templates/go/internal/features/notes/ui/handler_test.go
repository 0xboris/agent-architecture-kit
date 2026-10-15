package ui_test

import (
	"errors"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"__GO_MODULE__/internal/domain"
	"__GO_MODULE__/internal/features/notes/ui"
	"__GO_MODULE__/internal/features/notes/usecases"
	"__GO_MODULE__/internal/testsupport"
)

func newServer(store *testsupport.StubNoteStore) *http.ServeMux {
	mux := http.NewServeMux()
	ui.NewHandler(
		usecases.NewCreateNote(store, testsupport.NewFakeClock(time.Unix(0, 0)), &testsupport.SequentialIDs{}),
		usecases.NewListNotes(store),
		&testsupport.RecordingLogger{},
	).Register(mux)
	return mux
}

func TestListingNotesReturnsThem(t *testing.T) {
	store := &testsupport.StubNoteStore{Notes: []domain.Note{testsupport.SampleNote(1, time.Unix(0, 0))}}
	response := httptest.NewRecorder()
	newServer(store).ServeHTTP(response, httptest.NewRequest(http.MethodGet, "/notes", nil))

	if response.Code != http.StatusOK || !strings.Contains(response.Body.String(), `"title":"Note 1"`) {
		t.Fatalf("got %d %s", response.Code, response.Body)
	}
}

func TestPostingANoteReturnsCreated(t *testing.T) {
	response := httptest.NewRecorder()
	newServer(&testsupport.StubNoteStore{}).ServeHTTP(response,
		httptest.NewRequest(http.MethodPost, "/notes", strings.NewReader(`{"title":"Groceries"}`)))

	if response.Code != http.StatusCreated || !strings.Contains(response.Body.String(), `"title":"Groceries"`) {
		t.Fatalf("got %d %s", response.Code, response.Body)
	}
}

func TestPostingAnEmptyTitleReturnsUnprocessable(t *testing.T) {
	response := httptest.NewRecorder()
	newServer(&testsupport.StubNoteStore{}).ServeHTTP(response,
		httptest.NewRequest(http.MethodPost, "/notes", strings.NewReader(`{"title":" "}`)))

	if response.Code != http.StatusUnprocessableEntity || !strings.Contains(response.Body.String(), "title_empty") {
		t.Fatalf("got %d %s", response.Code, response.Body)
	}
}

func TestFailedLoadReturnsServerError(t *testing.T) {
	response := httptest.NewRecorder()
	newServer(&testsupport.StubNoteStore{Err: errors.New("offline")}).ServeHTTP(response,
		httptest.NewRequest(http.MethodGet, "/notes", nil))

	if response.Code != http.StatusInternalServerError {
		t.Fatalf("got %d %s", response.Code, response.Body)
	}
}
