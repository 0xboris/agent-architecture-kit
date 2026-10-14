package app

import (
	"io"
	"path/filepath"

	"__GO_MODULE__/internal/adapters/filestore"
	"__GO_MODULE__/internal/adapters/platform"
)

func LiveDependencies(config Config, logOutput io.Writer) Dependencies {
	return Dependencies{
		NoteStore: filestore.New(filepath.Join(config.DataDir, "notes.json")),
		Clock:     platform.SystemClock{},
		IDs:       platform.RandomIDs{},
		Logger:    platform.NewSlogLogger(logOutput),
	}
}
