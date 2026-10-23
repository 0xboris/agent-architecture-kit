package middleware_test

import (
	"context"
	"errors"
	"path/filepath"
	"slices"
	"testing"
	"time"

	"__GO_MODULE__/internal/adapters/filestore"
	"__GO_MODULE__/internal/domain"
	"__GO_MODULE__/internal/domain/middleware"
	"__GO_MODULE__/internal/testsupport"
)

func TestNoteSavedThroughTheMiddlewareIsStoredAndLogged(t *testing.T) {
	store := filestore.New(filepath.Join(t.TempDir(), "notes.json"))
	logger := &testsupport.RecordingLogger{}
	note := testsupport.SampleNote(1, time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC))

	if err := middleware.NewLoggingNoteStore(store, logger).Save(context.Background(), note); err != nil {
		t.Fatal(err)
	}

	if stored, err := store.AllNotes(context.Background()); err != nil || !slices.Equal(stored, []domain.Note{note}) {
		t.Fatalf("stored %v, %v; want [%v]", stored, err, note)
	}
	if got := logger.Messages(); !slices.Equal(got, []string{"note saved"}) {
		t.Fatalf("logged %v", got)
	}
}

func TestFailedSaveIsNotLogged(t *testing.T) {
	offline := errors.New("offline")
	logger := &testsupport.RecordingLogger{}

	err := middleware.NewLoggingNoteStore(testsupport.FailingNoteStore{Err: offline}, logger).
		Save(context.Background(), testsupport.SampleNote(1, time.Unix(0, 0)))

	if !errors.Is(err, offline) || len(logger.Messages()) != 0 {
		t.Fatalf("err = %v, logged %v; want offline and nothing logged", err, logger.Messages())
	}
}
