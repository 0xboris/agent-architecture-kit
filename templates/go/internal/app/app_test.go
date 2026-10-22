package app_test

import (
	"context"
	"net/http"
	"net/http/httptest"
	"path/filepath"
	"slices"
	"strings"
	"testing"
	"time"

	"__GO_MODULE__/internal/adapters/filestore"
	"__GO_MODULE__/internal/app"
	"__GO_MODULE__/internal/testsupport"
)

func TestNotesSliceStoresThroughTheLoggingMiddleware(t *testing.T) {
	store := filestore.New(filepath.Join(t.TempDir(), "notes.json"))
	logger := &testsupport.RecordingLogger{}
	service := app.New(app.Dependencies{
		NoteStore: store,
		Clock:     testsupport.NewFakeClock(time.Unix(0, 0)),
		IDs:       &testsupport.SequentialIDs{},
		Logger:    logger,
	})

	response := httptest.NewRecorder()
	service.Handler().ServeHTTP(response,
		httptest.NewRequest(http.MethodPost, "/notes", strings.NewReader(`{"title":"Groceries"}`)))

	if response.Code != http.StatusCreated {
		t.Fatalf("got %d %s", response.Code, response.Body)
	}
	if stored, err := store.AllNotes(context.Background()); err != nil || len(stored) != 1 {
		t.Fatalf("stored %v, %v; want one note", stored, err)
	}
	if got := logger.Messages(); !slices.Equal(got, []string{"note saved"}) {
		t.Fatalf("logged %v; want the middleware's entry", got)
	}
}
