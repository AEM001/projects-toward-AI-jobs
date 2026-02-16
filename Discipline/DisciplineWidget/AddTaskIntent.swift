//
//  AddTaskIntent.swift
//  DisciplineWidget
//
//  Created by Albert on 2026/2/16.
//

import AppIntents
import SwiftData
import Foundation
import WidgetKit

struct AddTaskIntent: AppIntent {
    static var title: LocalizedStringResource = "Add Task"
    static var description: IntentDescription = "Add a new task to today's list"
    
    @Parameter(title: "Task Title", requestValueDialog: "What task would you like to add?")
    var taskTitle: String
    
    init() {}
    
    init(taskTitle: String) {
        self.taskTitle = taskTitle
    }
    
    func perform() async throws -> some IntentResult {
        let schema = Schema([DisciplineTask.self])
        let modelConfiguration = ModelConfiguration(schema: schema, groupContainer: .identifier("group.albert.Discipline.share"))
        
        let container = try ModelContainer(for: schema, configurations: [modelConfiguration])
        let context = ModelContext(container)
        
        let newTask = DisciplineTask(title: taskTitle)
        context.insert(newTask)
        try? context.save()
        
        WidgetCenter.shared.reloadAllTimelines()
        
        return .result()
    }
}
