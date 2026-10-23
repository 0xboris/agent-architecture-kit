package platform

import (
	"crypto/rand"
	"io"
	"log/slog"
	"time"
)

type SystemClock struct{}

func (SystemClock) Now() time.Time {
	return time.Now()
}

type RandomIDs struct{}

func (RandomIDs) NewID() string {
	return rand.Text()
}

type SlogLogger struct {
	logger *slog.Logger
}

func NewSlogLogger(output io.Writer) SlogLogger {
	return SlogLogger{logger: slog.New(slog.NewJSONHandler(output, nil))}
}

func (l SlogLogger) Info(msg string, args ...any) {
	l.logger.Info(msg, args...)
}

func (l SlogLogger) Error(msg string, args ...any) {
	l.logger.Error(msg, args...)
}
