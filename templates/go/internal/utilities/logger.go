// Package utilities holds helpers with no business meaning.
package utilities

// Logger is the logging interface. The platform adapter implements it with
// log/slog, and tests use testsupport.RecordingLogger.
type Logger interface {
	Info(msg string, args ...any)
	Error(msg string, args ...any)
}
