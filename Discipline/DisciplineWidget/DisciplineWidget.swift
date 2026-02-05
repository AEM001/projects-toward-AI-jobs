//
//  DisciplineWidget.swift
//  DisciplineWidget
//
//  Created by Albert on 2026/2/5.
//

import WidgetKit
import SwiftUI
import SwiftData
import AppIntents

struct DisciplineWidgetProvider: TimelineProvider {
    @MainActor
    func placeholder(in context: Context) -> SimpleEntry {
        SimpleEntry(date: Date(), tasks: [])
    }

    @MainActor
    func getSnapshot(in context: Context, completion: @escaping (SimpleEntry) -> ()) {
        let tasks = fetchTasks()
        let entry = SimpleEntry(date: Date(), tasks: tasks)
        completion(entry)
    }

    @MainActor
    func getTimeline(in context: Context, completion: @escaping (Timeline<Entry>) -> ()) {
        let tasks = fetchTasks()
        let entry = SimpleEntry(date: Date(), tasks: tasks)
        
        let timeline = Timeline(entries: [entry], policy: .atEnd)
        completion(timeline)
    }
    
    @MainActor
    private func fetchTasks() -> [DisciplineTask] {
        let schema = Schema([DisciplineTask.self])
        let modelConfiguration = ModelConfiguration(schema: schema, groupContainer: .identifier("group.albert.Discipline.share"))
        
        guard let container = try? ModelContainer(for: schema, configurations: [modelConfiguration]) else { return [] }
        let context = ModelContext(container)
        
        let descriptor = FetchDescriptor<DisciplineTask>(
            sortBy: [SortDescriptor(\.createdAt)]
        )
        
        if let tasks = try? context.fetch(descriptor) {
            // Filter today's tasks only
            let today = Calendar.current.startOfDay(for: Date())
            let todayTasks = tasks.filter { task in
                Calendar.current.isDate(task.createdAt, inSameDayAs: today)
            }
            
            let sorted = todayTasks.sorted { t1, t2 in
                if t1.isCompleted != t2.isCompleted {
                    return !t1.isCompleted
                }
                return t1.createdAt < t2.createdAt
            }
            return sorted
        }
        return []
    }
}

struct SimpleEntry: TimelineEntry {
    let date: Date
    let tasks: [DisciplineTask]
}

struct DisciplineWidgetEntryView : View {
    var entry: DisciplineWidgetProvider.Entry
    @Environment(\.widgetFamily) var family

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text("Today")
                    .font(.system(size: 15, weight: .semibold))
                Spacer()
                Link(destination: URL(string: "discipline://add")!) {
                    Image(systemName: "plus.circle.fill")
                        .font(.system(size: 17))
                        .foregroundStyle(.blue)
                }
            }
            .padding(.bottom, 2)
            
            if entry.tasks.isEmpty {
                Spacer()
                VStack(spacing: 6) {
                    Image(systemName: "checkmark.circle")
                        .font(.system(size: 28))
                        .foregroundStyle(.secondary)
                    Text("All done!")
                        .font(.system(size: 13))
                        .foregroundStyle(.secondary)
                }
                .frame(maxWidth: .infinity)
                Spacer()
            } else {
                VStack(alignment: .leading, spacing: 3) {
                    ForEach(entry.tasks.prefix(taskLimit)) { task in
                        Button(intent: ToggleTaskIntent(taskId: task.id.uuidString)) {
                            HStack(spacing: 7) {
                                Image(systemName: task.isCompleted ? "checkmark.circle.fill" : "circle")
                                    .font(.system(size: 13))
                                    .foregroundStyle(task.isCompleted ? .green : .secondary)
                                Text(task.title)
                                    .font(.system(size: 12.5))
                                    .strikethrough(task.isCompleted)
                                    .foregroundStyle(task.isCompleted ? .secondary : .primary)
                                    .lineLimit(1)
                            }
                        }
                        .buttonStyle(.plain)
                    }
                }
                Spacer(minLength: 0)
            }
        }
        .padding(10)
        .containerBackground(.fill.tertiary, for: .widget)
    }
    
    private var taskLimit: Int {
        switch family {
        case .systemSmall:
            return 4
        case .systemMedium:
            return 8
        case .systemLarge:
            return 12
        default:
            return 6
        }
    }
}


struct DisciplineWidget: Widget {
    let kind: String = "DisciplineWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: DisciplineWidgetProvider()) { entry in
            DisciplineWidgetEntryView(entry: entry)
        }
        .configurationDisplayName("Discipline Tasks")
        .description("View and manage your daily tasks.")
        .supportedFamilies([.systemSmall, .systemMedium, .systemLarge])
    }
}

#Preview(as: .systemSmall) {
    DisciplineWidget()
} timeline: {
    SimpleEntry(date: .now, tasks: [])
}
