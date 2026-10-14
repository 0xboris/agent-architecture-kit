/// The order in which notes appear everywhere in the app: newest first, and
/// by id when two notes share a creation time, so the order is stable.
public enum NoteOrdering {
    public static func newestFirst(_ notes: [Note]) -> [Note] {
        notes.sorted { lhs, rhs in
            lhs.createdAt != rhs.createdAt
                ? lhs.createdAt > rhs.createdAt
                : lhs.id.uuidString < rhs.id.uuidString
        }
    }
}
