package filestore

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"sync"
	"time"

	"__GO_MODULE__/internal/domain"
)

type noteRecord struct {
	ID        string    `json:"id"`
	Title     string    `json:"title"`
	CreatedAt time.Time `json:"createdAt"`
}

type NoteStore struct {
	path string
	mu   sync.Mutex
}

func New(path string) *NoteStore {
	return &NoteStore{path: path}
}

func (s *NoteStore) AllNotes(ctx context.Context) ([]domain.Note, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	records, err := s.read()
	if err != nil {
		return nil, err
	}
	notes := make([]domain.Note, 0, len(records))
	for _, record := range records {
		title, err := domain.NewNoteTitle(record.Title)
		if err != nil {
			return nil, fmt.Errorf("stored note %s: %w", record.ID, err)
		}
		notes = append(notes, domain.Note{ID: domain.NoteID(record.ID), Title: title, CreatedAt: record.CreatedAt})
	}
	return notes, nil
}

func (s *NoteStore) Save(ctx context.Context, note domain.Note) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	records, err := s.read()
	if err != nil {
		return err
	}
	kept := records[:0]
	for _, record := range records {
		if record.ID != string(note.ID) {
			kept = append(kept, record)
		}
	}
	kept = append(kept, noteRecord{ID: string(note.ID), Title: note.Title.String(), CreatedAt: note.CreatedAt})
	return s.write(kept)
}

func (s *NoteStore) read() ([]noteRecord, error) {
	data, err := os.ReadFile(s.path)
	if errors.Is(err, fs.ErrNotExist) {
		return nil, nil
	}
	if err != nil {
		return nil, fmt.Errorf("read %s: %w", s.path, err)
	}
	var records []noteRecord
	if err := json.Unmarshal(data, &records); err != nil {
		return nil, fmt.Errorf("decode %s: %w", s.path, err)
	}
	return records, nil
}

// write renames a temporary file into place, so a crash never leaves half a file.
func (s *NoteStore) write(records []noteRecord) error {
	data, err := json.Marshal(records)
	if err != nil {
		return fmt.Errorf("encode notes: %w", err)
	}
	if err := os.MkdirAll(filepath.Dir(s.path), 0o755); err != nil {
		return fmt.Errorf("create directory: %w", err)
	}
	temp, err := os.CreateTemp(filepath.Dir(s.path), ".notes-*.json")
	if err != nil {
		return fmt.Errorf("create temporary file: %w", err)
	}
	defer os.Remove(temp.Name())
	if _, err := temp.Write(data); err != nil {
		temp.Close()
		return fmt.Errorf("write temporary file: %w", err)
	}
	if err := temp.Close(); err != nil {
		return fmt.Errorf("close temporary file: %w", err)
	}
	if err := os.Rename(temp.Name(), s.path); err != nil {
		return fmt.Errorf("replace %s: %w", s.path, err)
	}
	return nil
}
