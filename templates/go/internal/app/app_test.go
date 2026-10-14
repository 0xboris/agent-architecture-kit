package app_test

import (
	"context"
	"net/http"
	"net/http/httptest"
	"slices"
	"strings"
	"testing"
	"time"

	"__GO_MODULE__/internal/app"
	"__GO_MODULE__/internal/testsupport"
)

// Composition tests check the wiring in package app: which middleware each
// slice receives. Unit tests of a slice use fakes and never see the wiring.
func TestNotesSliceStoresThroughTheLoggingMiddleware(t *testing.T) {
	store := testsupport.NewFakeNoteStore()
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
	if notes, _ := store.AllNotes(context.Background()); len(notes) != 1 {
		t.Fatalf("stored notes = %v; want one", notes)
	}
	if got := logger.Messages(); !slices.Equal(got, []string{"note saved"}) {
		t.Fatalf("logged %v; want the middleware's entry", got)
	}
}
