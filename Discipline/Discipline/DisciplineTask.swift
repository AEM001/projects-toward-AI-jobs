import Foundation
import SwiftData

@Model
final class DisciplineTask {
    var id: UUID
    var title: String
    var isCompleted: Bool
    var createdAt: Date
    var completedAt: Date?
    
    init(title: String, isCompleted: Bool = false, createdAt: Date = Date()) {
        self.id = UUID()
        self.title = title
        self.isCompleted = isCompleted
        self.createdAt = createdAt
    }
}
