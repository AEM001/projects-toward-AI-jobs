import SwiftUI
import SwiftData

struct HistoryView: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \DisciplineTask.createdAt, order: .reverse) private var tasks: [DisciplineTask]
    
    @State private var selectedTimeFrame: TimeFrame = .day
    @State private var expandedDates: Set<String> = []
    
    enum TimeFrame: String, CaseIterable, Identifiable {
        case day = "Day"
        case week = "Week"
        case month = "Month"
        
        var id: String { self.rawValue }
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("History")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundStyle(Color(nsColor: .labelColor))
                
                Spacer()
                
                Picker("", selection: $selectedTimeFrame) {
                    ForEach(TimeFrame.allCases) { frame in
                        Text(frame.rawValue).tag(frame)
                    }
                }
                .pickerStyle(.segmented)
                .labelsHidden()
                .frame(width: 180)
            }
            .padding(.horizontal, 24)
            .padding(.top, 24)
            .padding(.bottom, 16)
            
            // Content
            List {
                ForEach(groupedTasks, id: \.dateKey) { group in
                    Section {
                        if expandedDates.contains(group.dateKey) {
                            ForEach(group.tasks) { task in
                                HStack(spacing: 12) {
                                    Image(systemName: task.isCompleted ? "checkmark.circle.fill" : "circle")
                                        .foregroundStyle(task.isCompleted ? .green : Color(nsColor: .tertiaryLabelColor))
                                        .font(.system(size: 16))
                                    
                                    Text(task.title)
                                        .strikethrough(task.isCompleted)
                                        .foregroundStyle(task.isCompleted ? Color(nsColor: .secondaryLabelColor) : Color(nsColor: .labelColor))
                                    
                                    Spacer()
                                }
                                .padding(.vertical, 4)
                            }
                        }
                    } header: {
                        HStack {
                            Button(action: {
                                withAnimation {
                                    if expandedDates.contains(group.dateKey) {
                                        expandedDates.remove(group.dateKey)
                                    } else {
                                        expandedDates.insert(group.dateKey)
                                    }
                                }
                            }) {
                                HStack {
                                    Image(systemName: expandedDates.contains(group.dateKey) ? "chevron.down" : "chevron.right")
                                        .frame(width: 16)
                                        .foregroundStyle(Color(nsColor: .secondaryLabelColor))
                                    
                                    Text(formatDate(group.date, for: selectedTimeFrame))
                                        .font(.headline)
                                        .foregroundStyle(Color(nsColor: .labelColor))
                                    
                                    Spacer()
                                    
                                    Text("\(group.tasks.count) tasks")
                                        .font(.caption)
                                        .foregroundStyle(Color(nsColor: .secondaryLabelColor))
                                        .padding(.horizontal, 8)
                                        .padding(.vertical, 2)
                                        .background(Color(nsColor: .quaternaryLabelColor))
                                        .cornerRadius(8)
                                }
                            }
                            .buttonStyle(.plain)
                            
                            Button(action: { copyToClipboard(for: group) }) {
                                Image(systemName: "doc.on.doc")
                                    .foregroundStyle(.blue)
                            }
                            .buttonStyle(.plain)
                            .help("Copy to Clipboard")
                        }
                        .padding(.vertical, 8)
                    }
                }
            }
            .listStyle(.inset)
            .scrollContentBackground(.hidden)
        }
        .background(Color(nsColor: .textBackgroundColor))
    }
    
    var groupedTasks: [(dateKey: String, date: Date, tasks: [DisciplineTask])] {
        let today = Calendar.current.startOfDay(for: Date())
        
        let historyTasks = tasks.filter { task in
            Calendar.current.startOfDay(for: task.createdAt) <= today
        }
        
        let groupedDictionary = Dictionary(grouping: historyTasks) { task in
            startOfTimeFrame(for: task.createdAt, frame: selectedTimeFrame)
        }
        
        return groupedDictionary.sorted { $0.key > $1.key }
            .map { (date, tasks) in
                let dateKey = ISO8601DateFormatter().string(from: date)
                let sortedTasks = tasks.sorted { $0.createdAt < $1.createdAt }
                return (dateKey: dateKey, date: date, tasks: sortedTasks)
            }
    }
    
    private func startOfTimeFrame(for date: Date, frame: TimeFrame) -> Date {
        let calendar = Calendar.current
        switch frame {
        case .day:
            return calendar.startOfDay(for: date)
        case .week:
            return calendar.date(from: calendar.dateComponents([.yearForWeekOfYear, .weekOfYear], from: date)) ?? date
        case .month:
            return calendar.date(from: calendar.dateComponents([.year, .month], from: date)) ?? date
        }
    }
    
    private func formatDate(_ date: Date, for frame: TimeFrame) -> String {
        let formatter = DateFormatter()
        switch frame {
        case .day:
            formatter.dateFormat = "EEE, M-d"
        case .week:
            formatter.dateFormat = "'W' M-d"
        case .month:
            formatter.dateFormat = "MMM yyyy"
        }
        return formatter.string(from: date)
    }
    
    private func copyToClipboard(for group: (dateKey: String, date: Date, tasks: [DisciplineTask])) {
        var textToCopy = "# \(formatDate(group.date, for: selectedTimeFrame))\n\n"
        for task in group.tasks {
            textToCopy += "- [\(task.isCompleted ? "x" : " ")] \(task.title)\n"
        }
        
        let pasteboard = NSPasteboard.general
        pasteboard.clearContents()
        pasteboard.setString(textToCopy, forType: .string)
    }
}

#Preview {
    HistoryView()
        .modelContainer(for: DisciplineTask.self, inMemory: true)
}
