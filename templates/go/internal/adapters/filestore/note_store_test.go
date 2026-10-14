package filestore_test

import (
	"path/filepath"
	"testing"

	"__GO_MODULE__/internal/adapters/filestore"
	"__GO_MODULE__/internal/domain"
	"__GO_MODULE__/internal/testsupport"
)

func TestFileNoteStoreMeetsTheContract(t *testing.T) {
	testsupport.NoteStoreContract(t, func(t *testing.T) domain.NoteStore {
		return filestore.New(filepath.Join(t.TempDir(), "notes.json"))
	})
}
