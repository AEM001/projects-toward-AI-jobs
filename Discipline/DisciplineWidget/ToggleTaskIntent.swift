//
//  ToggleTaskIntent.swift
//  DisciplineWidget
//
//  Created by Albert on 2026/2/5.
//

import AppIntents
import SwiftData
import Foundation
import WidgetKit

struct ToggleTaskIntent: AppIntent {
    static var title: LocalizedStringResource = "Toggle Task"
    
    @Parameter(title: "Task ID")
    var taskId: String
    
    init() {
        self.taskId = ""
    }
    
    init(taskId: String) {
        self.taskId = taskId
    }
    
    func perform() async throws -> some IntentResult {
        let schema = Schema([DisciplineTask.self])
        let modelConfiguration = ModelConfiguration(schema: schema, groupContainer: .identifier("group.albert.Discipline.share"))
        
        let container = try ModelContainer(for: schema, configurations: [modelConfiguration])
        let context = ModelContext(container)
        
        guard let uuid = UUID(uuidString: taskId) else {
            return .result()
        }
        
        let descriptor = FetchDescriptor<DisciplineTask>(predicate: #Predicate { task in
            task.id == uuid
        })
        
        if let task = try? context.fetch(descriptor).first {
            task.isCompleted.toggle()
            if task.isCompleted {
                task.completedAt = Date()
            } else {
                task.completedAt = nil
            }
            try? context.save()
            
            // Force immediate widget reload
            WidgetCenter.shared.reloadAllTimelines()
        }
        
        return .result()
    }
}
