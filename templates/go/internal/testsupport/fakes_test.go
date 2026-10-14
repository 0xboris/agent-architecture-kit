package testsupport_test

import (
	"testing"

	"__GO_MODULE__/internal/domain"
	"__GO_MODULE__/internal/testsupport"
)

func TestFakeNoteStoreMeetsTheContract(t *testing.T) {
	testsupport.NoteStoreContract(t, func(t *testing.T) domain.NoteStore {
		return testsupport.NewFakeNoteStore()
	})
}
