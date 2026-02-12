//
//  HoverTimeApp.swift
//  HoverTime
//

import SwiftUI

@main
struct HoverTimeApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    @StateObject private var manager = TimerManager()
    @Environment(\.openWindow) private var openWindow

    var body: some Scene {
        MenuBarExtra("HoverTime", systemImage: "clock") {
            MenuBarView(manager: manager, appDelegate: appDelegate)
        }

        Window("HoverTime Settings", id: "settings") {
            SettingsView(manager: manager)
                .onAppear {
                    // Ensure floating panel is created
                    appDelegate.setupPanel(with: manager)
                }
                .onReceive(NotificationCenter.default.publisher(for: .openSettings)) { _ in
                    // Already showing since this view received the notification
                }
        }
        .windowStyle(.titleBar)
        .defaultSize(width: 420, height: 600)
        .defaultLaunchBehavior(.presented)
    }
}
