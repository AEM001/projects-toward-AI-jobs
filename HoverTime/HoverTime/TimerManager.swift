//
//  TimerManager.swift
//  HoverTime
//

import Foundation
import Combine
import AppKit
import UserNotifications

enum TimeMode: String, CaseIterable {
    case clock = "Clock"
    case countdown = "Countdown"
    case pomodoro = "Pomodoro"
}

enum PomodoroPhase: String {
    case work = "Work"
    case shortBreak = "Break"
    case longBreak = "Long Break"
}

enum DisplayColor: String, CaseIterable {
    case white = "White"
    case cyan = "Cyan"
    case green = "Green"
    case amber = "Amber"
    case rose = "Rose"
    case lavender = "Lavender"
}

enum DisplayFont: String, CaseIterable {
    case newYork = "New York"
    case sfProHeavy = "SF Pro Heavy"
    case impact = "Impact"
    case arialBlack = "Arial Black"
}

class TimerManager: ObservableObject {
    // MARK: - Mode
    @Published var mode: TimeMode = .clock

    // MARK: - Clock
    @Published var currentTime: Date = Date()
    @Published var use24Hour: Bool = true
    @Published var showSeconds: Bool = true
    @Published var showDate: Bool = false

    // MARK: - Countdown
    @Published var countdownTotal: TimeInterval = 25 * 60
    @Published var countdownRemaining: TimeInterval = 25 * 60
    @Published var countdownRunning: Bool = false
    @Published var countdownPaused: Bool = false
    @Published var countdownAutoRepeat: Bool = false

    // MARK: - Pomodoro
    @Published var pomodoroWorkDuration: TimeInterval = 25 * 60
    @Published var pomodoroShortBreak: TimeInterval = 5 * 60
    @Published var pomodoroLongBreak: TimeInterval = 15 * 60
    @Published var pomodoroSessionsBeforeLong: Int = 4
    @Published var pomodoroCurrentSession: Int = 1
    @Published var pomodoroPhase: PomodoroPhase = .work
    @Published var pomodoroRunning: Bool = false
    @Published var pomodoroPaused: Bool = false
    @Published var pomodoroRemaining: TimeInterval = 25 * 60
    @Published var pomodoroAutoStart: Bool = false

    // MARK: - Appearance
    @Published var fontSize: CGFloat = 64
    @Published var windowOpacity: Double = 1.0
    @Published var showShadow: Bool = false
    @Published var clickThrough: Bool = false
    @Published var displayColor: DisplayColor = .cyan
    @Published var displayFont: DisplayFont = .newYork

    // MARK: - Sound
    @Published var soundEnabled: Bool = true

    private var clockTimer: Timer?
    private var countdownTimer: Timer?
    private var pomodoroTimer: Timer?

    init() {
        loadSettings()
        startClockTimer()
        requestNotificationPermission()
    }

    // MARK: - Clock

    private func startClockTimer() {
        clockTimer = Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { [weak self] _ in
            self?.currentTime = Date()
        }
    }

    var clockDisplayString: String {
        let formatter = DateFormatter()
        if use24Hour {
            formatter.dateFormat = showSeconds ? "HH:mm:ss" : "HH:mm"
        } else {
            formatter.dateFormat = showSeconds ? "h:mm:ss a" : "h:mm a"
        }
        return formatter.string(from: currentTime)
    }

    var dateDisplayString: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "E, MMM d"
        return formatter.string(from: currentTime)
    }

    // MARK: - Countdown

    func startCountdown() {
        if countdownPaused {
            countdownPaused = false
        } else {
            countdownRemaining = countdownTotal
        }
        countdownRunning = true
        countdownTimer?.invalidate()
        countdownTimer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
            guard let self = self else { return }
            if self.countdownRemaining > 0 {
                self.countdownRemaining -= 1
            } else {
                self.countdownFinished()
            }
        }
    }

    func pauseCountdown() {
        countdownRunning = false
        countdownPaused = true
        countdownTimer?.invalidate()
    }

    func resetCountdown() {
        countdownRunning = false
        countdownPaused = false
        countdownTimer?.invalidate()
        countdownRemaining = countdownTotal
    }

    func setCountdownPreset(_ minutes: Int) {
        countdownTotal = TimeInterval(minutes * 60)
        resetCountdown()
    }

    private func countdownFinished() {
        countdownTimer?.invalidate()
        countdownRunning = false
        countdownPaused = false
        playSound()
        sendNotification(title: "Countdown Complete", body: "Your timer has finished!")
        if countdownAutoRepeat {
            DispatchQueue.main.asyncAfter(deadline: .now() + 1) { [weak self] in
                self?.startCountdown()
            }
        }
    }

    var countdownProgress: Double {
        guard countdownTotal > 0 else { return 0 }
        return 1.0 - (countdownRemaining / countdownTotal)
    }

    // MARK: - Pomodoro

    func startPomodoro() {
        if pomodoroPaused {
            pomodoroPaused = false
        } else {
            pomodoroRemaining = currentPomodoroDuration
        }
        pomodoroRunning = true
        pomodoroTimer?.invalidate()
        pomodoroTimer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
            guard let self = self else { return }
            if self.pomodoroRemaining > 0 {
                self.pomodoroRemaining -= 1
            } else {
                self.pomodoroPhaseFinished()
            }
        }
    }

    func pausePomodoro() {
        pomodoroRunning = false
        pomodoroPaused = true
        pomodoroTimer?.invalidate()
    }

    func resetPomodoro() {
        pomodoroRunning = false
        pomodoroPaused = false
        pomodoroTimer?.invalidate()
        pomodoroPhase = .work
        pomodoroCurrentSession = 1
        pomodoroRemaining = pomodoroWorkDuration
    }

    private var currentPomodoroDuration: TimeInterval {
        switch pomodoroPhase {
        case .work: return pomodoroWorkDuration
        case .shortBreak: return pomodoroShortBreak
        case .longBreak: return pomodoroLongBreak
        }
    }

    private func pomodoroPhaseFinished() {
        pomodoroTimer?.invalidate()
        pomodoroRunning = false
        pomodoroPaused = false
        playSound()

        switch pomodoroPhase {
        case .work:
            if pomodoroCurrentSession >= pomodoroSessionsBeforeLong {
                pomodoroPhase = .longBreak
                sendNotification(title: "Long Break", body: "Great work! Take a long break.")
            } else {
                pomodoroPhase = .shortBreak
                sendNotification(title: "Break Time", body: "Session \(pomodoroCurrentSession) complete. Take a short break.")
            }
        case .shortBreak:
            pomodoroCurrentSession += 1
            pomodoroPhase = .work
            sendNotification(title: "Back to Work", body: "Break's over. Session \(pomodoroCurrentSession) starting.")
        case .longBreak:
            pomodoroCurrentSession = 1
            pomodoroPhase = .work
            sendNotification(title: "Fresh Start", body: "Long break over. New cycle begins!")
        }

        pomodoroRemaining = currentPomodoroDuration

        if pomodoroAutoStart {
            DispatchQueue.main.asyncAfter(deadline: .now() + 1) { [weak self] in
                self?.startPomodoro()
            }
        }
    }

    var pomodoroProgress: Double {
        let total = currentPomodoroDuration
        guard total > 0 else { return 0 }
        return 1.0 - (pomodoroRemaining / total)
    }

    // MARK: - Toggle / Shortcuts

    func toggleStartPause() {
        switch mode {
        case .clock:
            break
        case .countdown:
            if countdownRunning {
                pauseCountdown()
            } else {
                startCountdown()
            }
        case .pomodoro:
            if pomodoroRunning {
                pausePomodoro()
            } else {
                startPomodoro()
            }
        }
    }

    func cycleMode() {
        let modes = TimeMode.allCases
        guard let idx = modes.firstIndex(of: mode) else { return }
        let next = (idx + 1) % modes.count
        mode = modes[next]
    }

    func resetCurrent() {
        switch mode {
        case .clock: break
        case .countdown: resetCountdown()
        case .pomodoro: resetPomodoro()
        }
    }

    // MARK: - Helpers

    static func formatTime(_ interval: TimeInterval) -> String {
        let total = max(0, Int(interval))
        let h = total / 3600
        let m = (total % 3600) / 60
        let s = total % 60
        if h > 0 {
            return String(format: "%d:%02d:%02d", h, m, s)
        }
        return String(format: "%02d:%02d", m, s)
    }

    private func playSound() {
        guard soundEnabled else { return }
        NSSound(named: "Glass")?.play()
    }

    private func requestNotificationPermission() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound]) { _, _ in }
    }

    private func sendNotification(title: String, body: String) {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        let request = UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: nil)
        UNUserNotificationCenter.current().add(request)
    }

    // MARK: - Persistence

    func saveSettings() {
        let d = UserDefaults.standard
        d.set(use24Hour, forKey: "use24Hour")
        d.set(showSeconds, forKey: "showSeconds")
        d.set(showDate, forKey: "showDate")
        d.set(fontSize, forKey: "fontSize")
        d.set(windowOpacity, forKey: "windowOpacity")
        d.set(showShadow, forKey: "showShadow")
        d.set(clickThrough, forKey: "clickThrough")
        d.set(soundEnabled, forKey: "soundEnabled")
        d.set(pomodoroWorkDuration, forKey: "pomodoroWorkDuration")
        d.set(pomodoroShortBreak, forKey: "pomodoroShortBreak")
        d.set(pomodoroLongBreak, forKey: "pomodoroLongBreak")
        d.set(pomodoroSessionsBeforeLong, forKey: "pomodoroSessionsBeforeLong")
        d.set(pomodoroAutoStart, forKey: "pomodoroAutoStart")
        d.set(countdownAutoRepeat, forKey: "countdownAutoRepeat")
        d.set(countdownTotal, forKey: "countdownTotal")
        d.set(mode.rawValue, forKey: "timeMode")
        d.set(displayColor.rawValue, forKey: "displayColor")
        d.set(displayFont.rawValue, forKey: "displayFont")
    }

    private func loadSettings() {
        let d = UserDefaults.standard
        if d.object(forKey: "use24Hour") != nil {
            use24Hour = d.bool(forKey: "use24Hour")
            showSeconds = d.bool(forKey: "showSeconds")
            showDate = d.bool(forKey: "showDate")
            fontSize = CGFloat(d.double(forKey: "fontSize"))
            windowOpacity = d.double(forKey: "windowOpacity")
            showShadow = d.bool(forKey: "showShadow")
            clickThrough = d.bool(forKey: "clickThrough")
            soundEnabled = d.bool(forKey: "soundEnabled")
            pomodoroWorkDuration = d.double(forKey: "pomodoroWorkDuration")
            pomodoroShortBreak = d.double(forKey: "pomodoroShortBreak")
            pomodoroLongBreak = d.double(forKey: "pomodoroLongBreak")
            pomodoroSessionsBeforeLong = d.integer(forKey: "pomodoroSessionsBeforeLong")
            pomodoroAutoStart = d.bool(forKey: "pomodoroAutoStart")
            countdownAutoRepeat = d.bool(forKey: "countdownAutoRepeat")
            countdownTotal = d.double(forKey: "countdownTotal")
            countdownRemaining = countdownTotal
            if let modeStr = d.string(forKey: "timeMode"), let m = TimeMode(rawValue: modeStr) {
                mode = m
            }
            if let colorStr = d.string(forKey: "displayColor"), let c = DisplayColor(rawValue: colorStr) {
                displayColor = c
            }
            if let fontStr = d.string(forKey: "displayFont"), let f = DisplayFont(rawValue: fontStr) {
                displayFont = f
            }
            if fontSize < 40 { fontSize = 64 }
            if windowOpacity <= 0 { windowOpacity = 1.0 }
            if pomodoroWorkDuration <= 0 { pomodoroWorkDuration = 25 * 60 }
            if pomodoroShortBreak <= 0 { pomodoroShortBreak = 5 * 60 }
            if pomodoroLongBreak <= 0 { pomodoroLongBreak = 15 * 60 }
            if pomodoroSessionsBeforeLong <= 0 { pomodoroSessionsBeforeLong = 4 }
            if countdownTotal <= 0 { countdownTotal = 25 * 60; countdownRemaining = countdownTotal }
        }
    }
}
