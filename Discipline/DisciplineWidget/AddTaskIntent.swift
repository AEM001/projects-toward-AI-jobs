//
//  AddTaskIntent.swift
//  DisciplineWidget
//
//  Created by Albert on 2026/2/16.
//

import AppIntents
import Foundation

struct AddTaskIntent: AppIntent {
    static var title: LocalizedStringResource = "Add Task"
    static var description: IntentDescription = "Add a new task to today's list"
    static var openAppWhenRun: Bool = true
    
    init() {}
    
    func perform() async throws -> some IntentResult {
        DistributedNotificationCenter.default().postNotificationName(
            Notification.Name("com.albert.Discipline.addTask"),
            object: nil
        )
        return .result()
    }
}
