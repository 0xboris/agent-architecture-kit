package ui_test

import (
	"context"
	"errors"
	"net/http"
	"net/http/httptest"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"__GO_MODULE__/internal/adapters/filestore"
	"__GO_MODULE__/internal/domain"
	"__GO_MODULE__/internal/features/notes/ui"
	"__GO_MODULE__/internal/features/notes/usecases"
	"__GO_MODULE__/internal/testsupport"
)

func newStore(t *testing.T) *filestore.NoteStore {
	return filestore.New(filepath.Join(t.TempDir(), "notes.json"))
}

func newServer(store domain.NoteStore) *http.ServeMux {
	mux := http.NewServeMux()
	ui.NewHandler(
		usecases.NewCreateNote(store, testsupport.NewFakeClock(time.Unix(0, 0)), &testsupport.SequentialIDs{}),
		usecases.NewListNotes(store),
		&testsupport.RecordingLogger{},
	).Register(mux)
	return mux
}

func serve(server *http.ServeMux, method, body string) *httptest.ResponseRecorder {
	response := httptest.NewRecorder()
	server.ServeHTTP(response, httptest.NewRequest(method, "/notes", strings.NewReader(body)))
	return response
}

func TestListingNotesReturnsThem(t *testing.T) {
	store := newStore(t)
	if err := store.Save(context.Background(), testsupport.SampleNote(1, time.Unix(0, 0))); err != nil {
		t.Fatal(err)
	}

	response := serve(newServer(store), http.MethodGet, "")

	if response.Code != http.StatusOK || !strings.Contains(response.Body.String(), `"title":"Note 1"`) {
		t.Fatalf("got %d %s", response.Code, response.Body)
	}
}

func TestPostedNoteIsCreatedAndListed(t *testing.T) {
	server := newServer(newStore(t))

	created := serve(server, http.MethodPost, `{"title":"Groceries"}`)
	listed := serve(server, http.MethodGet, "")

	if created.Code != http.StatusCreated || !strings.Contains(created.Body.String(), `"title":"Groceries"`) {
		t.Fatalf("POST got %d %s", created.Code, created.Body)
	}
	if !strings.Contains(listed.Body.String(), `"title":"Groceries"`) {
		t.Fatalf("GET got %d %s", listed.Code, listed.Body)
	}
}

func TestPostingAnEmptyTitleReturnsUnprocessable(t *testing.T) {
	response := serve(newServer(newStore(t)), http.MethodPost, `{"title":" "}`)

	if response.Code != http.StatusUnprocessableEntity || !strings.Contains(response.Body.String(), "title_empty") {
		t.Fatalf("got %d %s", response.Code, response.Body)
	}
}

func TestFailedLoadReturnsServerError(t *testing.T) {
	response := serve(newServer(testsupport.FailingNoteStore{Err: errors.New("offline")}), http.MethodGet, "")

	if response.Code != http.StatusInternalServerError {
		t.Fatalf("got %d %s", response.Code, response.Body)
	}
}
