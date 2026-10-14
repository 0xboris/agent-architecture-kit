package middleware_test

import (
	"context"
	"errors"
	"slices"
	"testing"
	"time"

	"__GO_MODULE__/internal/domain/middleware"
	"__GO_MODULE__/internal/testsupport"
)

func TestSaveThroughTheMiddlewareLogsAndStores(t *testing.T) {
	store := testsupport.NewFakeNoteStore()
	logger := &testsupport.RecordingLogger{}
	note := testsupport.SampleNote(1, time.Unix(0, 0))

	if err := middleware.NewLoggingNoteStore(store, logger).Save(context.Background(), note); err != nil {
		t.Fatal(err)
	}

	if notes, _ := store.AllNotes(context.Background()); len(notes) != 1 {
		t.Fatalf("stored notes = %v; want one", notes)
	}
	if got := logger.Messages(); !slices.Equal(got, []string{"note saved"}) {
		t.Fatalf("logged %v", got)
	}
}

func TestFailedSaveIsNotLogged(t *testing.T) {
	store := testsupport.NewFakeNoteStore()
	offline := errors.New("offline")
	store.FailNextCall(offline)
	logger := &testsupport.RecordingLogger{}

	err := middleware.NewLoggingNoteStore(store, logger).Save(context.Background(), testsupport.SampleNote(1, time.Unix(0, 0)))

	if !errors.Is(err, offline) || len(logger.Messages()) != 0 {
		t.Fatalf("err = %v, logged %v; want offline and nothing logged", err, logger.Messages())
	}
}
