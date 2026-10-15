package app_test

import (
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
// slice receives. Unit tests of a slice build their use cases directly and
// never see the wiring.
func TestNotesSliceStoresThroughTheLoggingMiddleware(t *testing.T) {
	store := &testsupport.StubNoteStore{}
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
	if saved := store.Saved(); len(saved) != 1 {
		t.Fatalf("saved %v; want one note", saved)
	}
	if got := logger.Messages(); !slices.Equal(got, []string{"note saved"}) {
		t.Fatalf("logged %v; want the middleware's entry", got)
	}
}
