//
//  DisciplineApp.swift
//  Discipline
//
//  Created by Albert on 2026/2/5.
//

import SwiftUI
import SwiftData

@main
struct DisciplineApp: App {
    var sharedModelContainer: ModelContainer = {
        let schema = Schema([DisciplineTask.self])
        let modelConfiguration = ModelConfiguration(schema: schema, groupContainer: .identifier("group.albert.Discipline.share"))
        
        do {
            return try ModelContainer(for: schema, configurations: [modelConfiguration])
        } catch {
            fatalError("Could not create ModelContainer: \(error)")
        }
    }()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .frame(minWidth: 600, minHeight: 400)
        }
        .modelContainer(sharedModelContainer)
        .windowStyle(.titleBar)
        .windowToolbarStyle(.unified)
        .commands {
            SidebarCommands()
        }
    }
}
