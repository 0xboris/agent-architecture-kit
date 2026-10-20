package middleware_test

import (
	"context"
	"errors"
	"slices"
	"testing"
	"time"

	"__GO_MODULE__/internal/domain"
	"__GO_MODULE__/internal/domain/middleware"
	"__GO_MODULE__/internal/testsupport"
)

func TestSaveThroughTheMiddlewareSavesAndLogs(t *testing.T) {
	store := &testsupport.StubNoteStore{}
	logger := &testsupport.RecordingLogger{}
	note := testsupport.SampleNote(1, time.Unix(0, 0))

	if err := middleware.NewLoggingNoteStore(store, logger).Save(context.Background(), note); err != nil {
		t.Fatal(err)
	}

	if saved := store.Saved(); !slices.Equal(saved, []domain.Note{note}) {
		t.Fatalf("saved %v; want [%v]", saved, note)
	}
	if got := logger.Messages(); !slices.Equal(got, []string{"note saved"}) {
		t.Fatalf("logged %v", got)
	}
}

func TestFailedSaveIsNotLogged(t *testing.T) {
	offline := errors.New("offline")
	store := &testsupport.StubNoteStore{Err: offline}
	logger := &testsupport.RecordingLogger{}

	err := middleware.NewLoggingNoteStore(store, logger).Save(context.Background(), testsupport.SampleNote(1, time.Unix(0, 0)))

	if !errors.Is(err, offline) || len(logger.Messages()) != 0 {
		t.Fatalf("err = %v, logged %v; want offline and nothing logged", err, logger.Messages())
	}
}
