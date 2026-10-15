// Package testsupport holds stubs, small fakes, and sample data. Only test
// code imports it.
package testsupport

import (
	"fmt"
	"slices"
	"sync"
	"time"

	"__GO_MODULE__/internal/domain"
)

// FakeClock starts at a fixed time and moves only when a test calls Advance.
type FakeClock struct {
	mu  sync.Mutex
	now time.Time
}

func NewFakeClock(start time.Time) *FakeClock {
	return &FakeClock{now: start}
}

func (c *FakeClock) Now() time.Time {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.now
}

func (c *FakeClock) Advance(d time.Duration) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.now = c.now.Add(d)
}

// SequentialIDs returns id-001, id-002, and so on.
type SequentialIDs struct {
	mu   sync.Mutex
	next int
}

func (g *SequentialIDs) NewID() string {
	g.mu.Lock()
	defer g.mu.Unlock()
	g.next++
	return fmt.Sprintf("id-%03d", g.next)
}

// RecordingLogger records every log call.
type RecordingLogger struct {
	mu       sync.Mutex
	messages []string
}

func (l *RecordingLogger) Info(msg string, args ...any)  { l.record(msg) }
func (l *RecordingLogger) Error(msg string, args ...any) { l.record(msg) }

func (l *RecordingLogger) Messages() []string {
	l.mu.Lock()
	defer l.mu.Unlock()
	return slices.Clone(l.messages)
}

func (l *RecordingLogger) record(msg string) {
	l.mu.Lock()
	defer l.mu.Unlock()
	l.messages = append(l.messages, msg)
}

// SampleNote returns a valid note for tests.
func SampleNote(number int, createdAt time.Time) domain.Note {
	title, err := domain.NewNoteTitle(fmt.Sprintf("Note %d", number))
	if err != nil {
		panic(err)
	}
	return domain.Note{ID: domain.NoteID(fmt.Sprintf("id-%03d", number)), Title: title, CreatedAt: createdAt}
}
