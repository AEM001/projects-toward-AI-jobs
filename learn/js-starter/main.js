// JavaScript - no types, no compilation needed!

// Variables (types are inferred, can change)
let name = "Albert";
let age = 25;
let isStudent = true;

// Arrays (no type annotations needed)
let scores = [85, 92, 78, 96];
let friends = ["Bob", "Charlie", "Diana"];

// Objects (no interfaces needed)
let alice = {
    name: "Albert",
    age: 25
};

// Functions (no parameter types, no return type annotation)
function greet(person) {
    return `Hello, ${person.name}! You are ${person.age} years old.`;
}

function calculateAverage(numbers) {
    if (numbers.length === 0) return 0;
    const sum = numbers.reduce((acc, n) => acc + n, 0);
    return sum / numbers.length;
}

// Union types (just use |)
function formatId(id) {
    return `ID-${id}`;
}

// Array methods
function getPendingTasks(tasks) {
    return tasks.filter(t => !t.completed);
}

// Render to DOM
document.addEventListener('DOMContentLoaded', () => {
    const output = document.getElementById('output');
    if (!output) return;

    const greeting = greet(alice);
    const avgScore = calculateAverage(scores);
    
    // Tasks example
    const tasks = [
        { title: "Read docs", completed: true },
        { title: "Write code", completed: false },
        { title: "Build project", completed: false }
    ];
    
    const pending = getPendingTasks(tasks);

    output.innerHTML = `
        <section>
            <h2>👋 ${greeting}</h2>
        </section>
        
        <section>
            <h3>📊 Scores</h3>
            <p>Scores: ${scores.join(', ')}</p>
            <p>Average: ${avgScore.toFixed(1)}</p>
        </section>
        
        <section>
            <h3>👥 Friends</h3>
            <ul>${friends.map(f => `<li>${f}</li>`).join('')}</ul>
        </section>
        
        <section>
            <h3>📝 Tasks</h3>
            <ul>${tasks.map(t => `<li>${t.completed ? '✓' : '○'} ${t.title}</li>`).join('')}</ul>
            <p><strong>Pending: ${pending.length}</strong></p>
        </section>
    `;
});
