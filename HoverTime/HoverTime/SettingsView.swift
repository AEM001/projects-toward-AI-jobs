//
//  SettingsView.swift
//  HoverTime
//

import SwiftUI

struct SettingsView: View {
    @ObservedObject var manager: TimerManager

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                modeSection
                Divider().padding(.vertical, 4)
                appearanceSection
                Divider().padding(.vertical, 4)
                clockSection
                Divider().padding(.vertical, 4)
                countdownSection
                Divider().padding(.vertical, 4)
                pomodoroSection
                Divider().padding(.vertical, 4)
                generalSection
            }
            .padding(20)
        }
        .frame(width: 400)
        .onDisappear {
            manager.saveSettings()
        }
    }

    // MARK: - Mode

    private var modeSection: some View {
        settingsSection("Mode") {
            Picker("", selection: $manager.mode) {
                ForEach(TimeMode.allCases, id: \.self) { mode in
                    Text(mode.rawValue).tag(mode)
                }
            }
            .pickerStyle(.segmented)
            .labelsHidden()
        }
    }

    // MARK: - Appearance

    private var appearanceSection: some View {
        settingsSection("Appearance") {
            HStack {
                Text("Color")
                    .frame(width: 80, alignment: .leading)
                HStack(spacing: 10) {
                    ForEach(DisplayColor.allCases, id: \.self) { color in
                        Button(action: { manager.displayColor = color }) {
                            Circle()
                                .fill(swatchColor(for: color))
                                .frame(width: 22, height: 22)
                                .overlay(
                                    Circle()
                                        .stroke(.primary.opacity(manager.displayColor == color ? 0.9 : 0.0), lineWidth: 2)
                                        .frame(width: 28, height: 28)
                                )
                        }
                        .buttonStyle(.plain)
                        .help(color.rawValue)
                    }
                }
            }

            Picker("Typeface", selection: $manager.displayFont) {
                ForEach(DisplayFont.allCases, id: \.self) { font in
                    Text(font.rawValue).tag(font)
                }
            }
            .pickerStyle(.menu)

            HStack {
                Text("Font size")
                Slider(value: $manager.fontSize, in: 40...200, step: 2)
                Text("\(Int(manager.fontSize))")
                    .frame(width: 30)
                    .foregroundStyle(.secondary)
            }

            HStack {
                Text("Opacity")
                Slider(value: $manager.windowOpacity, in: 0.1...1.0, step: 0.05)
                Text("\(Int(manager.windowOpacity * 100))%")
                    .frame(width: 40)
                    .foregroundStyle(.secondary)
            }

            Toggle("Background blur", isOn: $manager.showShadow)
        }
    }

    // MARK: - Clock

    private var clockSection: some View {
        settingsSection("Clock") {
            Toggle("24-hour format", isOn: $manager.use24Hour)
            Toggle("Show seconds", isOn: $manager.showSeconds)
            Toggle("Show date", isOn: $manager.showDate)
        }
    }

    // MARK: - Countdown

    private var countdownSection: some View {
        settingsSection("Countdown") {
            HStack {
                Text("Minutes")
                Spacer()
                TextField("", value: Binding(
                    get: { Int(manager.countdownTotal / 60) },
                    set: { manager.countdownTotal = TimeInterval($0 * 60) }
                ), format: .number)
                .frame(width: 60)
                .textFieldStyle(.roundedBorder)
            }

            HStack(spacing: 8) {
                Text("Presets:")
                    .foregroundStyle(.secondary)
                ForEach([5, 10, 25, 45, 60], id: \.self) { mins in
                    Button("\(mins)m") {
                        manager.countdownTotal = TimeInterval(mins * 60)
                        manager.countdownRemaining = manager.countdownTotal
                    }
                    .buttonStyle(.bordered)
                    .controlSize(.small)
                }
            }

            Toggle("Auto-repeat", isOn: $manager.countdownAutoRepeat)
        }
    }

    // MARK: - Pomodoro

    private var pomodoroSection: some View {
        settingsSection("Pomodoro") {
            durationRow("Work", value: Binding(
                get: { Int(manager.pomodoroWorkDuration / 60) },
                set: { manager.pomodoroWorkDuration = TimeInterval($0 * 60) }
            ))
            durationRow("Short break", value: Binding(
                get: { Int(manager.pomodoroShortBreak / 60) },
                set: { manager.pomodoroShortBreak = TimeInterval($0 * 60) }
            ))
            durationRow("Long break", value: Binding(
                get: { Int(manager.pomodoroLongBreak / 60) },
                set: { manager.pomodoroLongBreak = TimeInterval($0 * 60) }
            ))
            Stepper("Sessions before long break: \(manager.pomodoroSessionsBeforeLong)",
                    value: $manager.pomodoroSessionsBeforeLong, in: 2...8)
            Toggle("Auto-start next session", isOn: $manager.pomodoroAutoStart)
        }
    }

    private func durationRow(_ label: String, value: Binding<Int>) -> some View {
        HStack {
            Text(label)
            Spacer()
            TextField("", value: value, format: .number)
                .frame(width: 60)
                .textFieldStyle(.roundedBorder)
            Text("min").foregroundStyle(.secondary)
        }
    }

    // MARK: - General

    private var generalSection: some View {
        settingsSection("General") {
            Toggle("Sound notifications", isOn: $manager.soundEnabled)
            Toggle("Click-through mode", isOn: $manager.clickThrough)

            VStack(alignment: .leading, spacing: 4) {
                Text("Keyboard Shortcuts")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                shortcutRow("Show/Hide", "⌘⇧T")
                shortcutRow("Start/Pause", "⌘⇧S")
                shortcutRow("Cycle Mode", "⌘⇧M")
                shortcutRow("Reset", "⌘⇧R")
            }
            .padding(.top, 4)
        }
    }

    // MARK: - Helpers

    private func settingsSection<Content: View>(_ title: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(title)
                .font(.headline)
                .padding(.bottom, 2)
            content()
        }
    }

    private func shortcutRow(_ label: String, _ shortcut: String) -> some View {
        HStack {
            Text(label)
                .foregroundStyle(.secondary)
            Spacer()
            Text(shortcut)
                .font(.system(size: 11, design: .monospaced))
                .padding(.horizontal, 6)
                .padding(.vertical, 2)
                .background(.quaternary, in: RoundedRectangle(cornerRadius: 4))
        }
    }

    private func swatchColor(for color: DisplayColor) -> Color {
        switch color {
        case .white:    return .white
        case .cyan:     return Color(red: 0.0, green: 0.9, blue: 1.0)
        case .green:    return Color(red: 0.2, green: 1.0, blue: 0.6)
        case .amber:    return Color(red: 1.0, green: 0.8, blue: 0.2)
        case .rose:     return Color(red: 1.0, green: 0.4, blue: 0.5)
        case .lavender: return Color(red: 0.7, green: 0.5, blue: 1.0)
        }
    }
}
