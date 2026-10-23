package domain

import (
	"slices"
	"strings"
)

// NewestFirst sorts notes newest first, and by id when two notes share a
// creation time. Every list of notes uses this order.
func NewestFirst(notes []Note) []Note {
	sorted := slices.Clone(notes)
	slices.SortFunc(sorted, func(a, b Note) int {
		if order := b.CreatedAt.Compare(a.CreatedAt); order != 0 {
			return order
		}
		return strings.Compare(string(a.ID), string(b.ID))
	})
	return sorted
}
