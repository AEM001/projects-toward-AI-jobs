//
//  DisciplineApp.swift
//  Discipline
//
//  Created by Albert on 2026/2/5.
//

import SwiftUI
import SwiftData
import AppKit

@main
struct DisciplineApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    
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
        Window("Discipline", id: "main") {
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

class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.regular)
    }
    
    func applicationShouldHandleReopen(_ sender: NSApplication, hasVisibleWindows flag: Bool) -> Bool {
        if !flag {
            activateMainWindow()
        }
        return true
    }
    
    func application(_ application: NSApplication, open urls: [URL]) {
        activateMainWindow()
    }
    
    private func activateMainWindow() {
        NSApp.activate()
        if let window = NSApp.windows.first(where: { $0.isKeyWindow }) {
            window.makeKeyAndOrderFront(nil)
        } else if let window = NSApp.windows.first(where: { $0.title == "Discipline" || !$0.title.isEmpty }) {
            window.makeKeyAndOrderFront(nil)
        }
    }
}
