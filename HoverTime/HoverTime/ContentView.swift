//
//  ContentView.swift
//  HoverTime
//

import SwiftUI

struct ContentView: View {
    @ObservedObject var manager: TimerManager
    @State private var isHovering = false

    var body: some View {
        ZStack {
            if manager.showShadow {
                RoundedRectangle(cornerRadius: 12)
                    .fill(.ultraThinMaterial)
                    .opacity(0.3)
            }

            VStack(spacing: 4) {
                switch manager.mode {
                case .clock:
                    clockView
                case .countdown:
                    countdownView
                case .pomodoro:
                    pomodoroView
                }

                if isHovering {
                    controlBar
                        .transition(.opacity.combined(with: .move(edge: .bottom)))
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
        }
        .frame(minWidth: 150, minHeight: 50)
        .fixedSize()
        .onHover { hovering in
            withAnimation(.easeInOut(duration: 0.2)) {
                isHovering = hovering
            }
        }
    }

    // MARK: - Color & Font Helpers

    private var tintColor: Color {
        switch manager.displayColor {
        case .white:    return .white
        case .cyan:     return Color(red: 0.0, green: 0.9, blue: 1.0)
        case .green:    return Color(red: 0.2, green: 1.0, blue: 0.6)
        case .amber:    return Color(red: 1.0, green: 0.8, blue: 0.2)
        case .rose:     return Color(red: 1.0, green: 0.4, blue: 0.5)
        case .lavender: return Color(red: 0.7, green: 0.5, blue: 1.0)
        }
    }

    private func timeFont(size: CGFloat, weight: Font.Weight = .thin) -> Font {
        switch manager.displayFont {
        case .system:
            return .system(size: size, weight: weight, design: .default)
        case .mono:
            return .system(size: size, weight: weight, design: .monospaced)
        case .rounded:
            return .system(size: size, weight: weight, design: .rounded)
        case .newYork:
            return .system(size: size, weight: weight, design: .serif)
        case .helveticaNeue:
            return Font.custom("HelveticaNeue-Thin", size: size)
        case .avenir:
            return Font.custom("AvenirNext-UltraLight", size: size)
        }
    }

    // MARK: - Clock View

    private var clockView: some View {
        VStack(spacing: 2) {
            Text(manager.clockDisplayString)
                .font(timeFont(size: manager.fontSize))
                .foregroundStyle(tintColor)
                .shadow(color: .black.opacity(0.6), radius: 3, x: 0, y: 1)

            if manager.showDate {
                Text(manager.dateDisplayString)
                    .font(timeFont(size: manager.fontSize * 0.3, weight: .light))
                    .foregroundStyle(tintColor.opacity(0.7))
            }
        }
    }

    // MARK: - Countdown View

    private var countdownView: some View {
        VStack(spacing: 4) {
            ZStack {
                Circle()
                    .stroke(tintColor.opacity(0.15), lineWidth: 3)
                    .frame(width: manager.fontSize * 1.8, height: manager.fontSize * 1.8)

                Circle()
                    .trim(from: 0, to: manager.countdownProgress)
                    .stroke(tintColor.opacity(0.6), style: StrokeStyle(lineWidth: 3, lineCap: .round))
                    .frame(width: manager.fontSize * 1.8, height: manager.fontSize * 1.8)
                    .rotationEffect(.degrees(-90))
                    .animation(.linear(duration: 1), value: manager.countdownProgress)

                Text(TimerManager.formatTime(manager.countdownRemaining))
                    .font(timeFont(size: manager.fontSize * 0.7))
                    .foregroundStyle(tintColor)
                    .shadow(color: .black.opacity(0.6), radius: 3, x: 0, y: 1)
            }

            if isHovering && !manager.countdownRunning && !manager.countdownPaused {
                presetButtons
                    .transition(.opacity)
            }
        }
    }

    // MARK: - Pomodoro View

    private var pomodoroView: some View {
        VStack(spacing: 4) {
            ZStack {
                Circle()
                    .stroke(pomodoroColor.opacity(0.15), lineWidth: 3)
                    .frame(width: manager.fontSize * 1.8, height: manager.fontSize * 1.8)

                Circle()
                    .trim(from: 0, to: manager.pomodoroProgress)
                    .stroke(pomodoroColor.opacity(0.8), style: StrokeStyle(lineWidth: 3, lineCap: .round))
                    .frame(width: manager.fontSize * 1.8, height: manager.fontSize * 1.8)
                    .rotationEffect(.degrees(-90))
                    .animation(.linear(duration: 1), value: manager.pomodoroProgress)

                Text(TimerManager.formatTime(manager.pomodoroRemaining))
                    .font(timeFont(size: manager.fontSize * 0.6))
                    .foregroundStyle(tintColor)
                    .shadow(color: .black.opacity(0.6), radius: 3, x: 0, y: 1)
            }

            HStack(spacing: 6) {
                Text(manager.pomodoroPhase.rawValue)
                    .font(timeFont(size: manager.fontSize * 0.22, weight: .regular))
                    .foregroundStyle(pomodoroColor.opacity(0.9))

                HStack(spacing: 3) {
                    ForEach(1...manager.pomodoroSessionsBeforeLong, id: \.self) { i in
                        Circle()
                            .fill(i <= manager.pomodoroCurrentSession ? pomodoroColor : tintColor.opacity(0.2))
                            .frame(width: 5, height: 5)
                    }
                }
            }
        }
    }

    private var pomodoroColor: Color {
        switch manager.pomodoroPhase {
        case .work: return .red
        case .shortBreak: return .green
        case .longBreak: return .blue
        }
    }

    // MARK: - Controls

    private var controlBar: some View {
        HStack(spacing: 8) {
            if manager.mode != .clock {
                Button(action: { manager.toggleStartPause() }) {
                    Image(systemName: isRunning ? "pause.fill" : "play.fill")
                        .font(.system(size: 10, weight: .semibold))
                        .foregroundStyle(.black)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(.white.opacity(0.85), in: Capsule())
                }
                .buttonStyle(.plain)

                Button(action: { manager.resetCurrent() }) {
                    Image(systemName: "arrow.counterclockwise")
                        .font(.system(size: 10, weight: .semibold))
                        .foregroundStyle(.black)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(.white.opacity(0.85), in: Capsule())
                }
                .buttonStyle(.plain)
            }

            Button(action: { manager.cycleMode() }) {
                Text(manager.mode.rawValue)
                    .font(.system(size: 10, weight: .semibold, design: .monospaced))
                    .foregroundStyle(.black)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(.white.opacity(0.85), in: Capsule())
            }
            .buttonStyle(.plain)
        }
        .padding(.top, 4)
    }

    private var presetButtons: some View {
        HStack(spacing: 6) {
            ForEach([5, 10, 25, 45, 60], id: \.self) { mins in
                Button(action: { manager.setCountdownPreset(mins) }) {
                    Text("\(mins)")
                        .font(.system(size: 10, weight: .semibold, design: .monospaced))
                        .foregroundStyle(.black)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 3)
                        .background(.white.opacity(0.85), in: Capsule())
                }
                .buttonStyle(.plain)
            }
        }
    }

    private var isRunning: Bool {
        switch manager.mode {
        case .clock: return false
        case .countdown: return manager.countdownRunning
        case .pomodoro: return manager.pomodoroRunning
        }
    }
}
