// TypeScript Basics - A gentle introduction

// 1. TYPES: Define what kind of data something is
// TypeScript adds types to JavaScript

let name: string = "Alice";
let age: number = 25;
let isStudent: boolean = true;

// 2. ARRAYS: Lists with typed elements
let scores: number[] = [85, 92, 78, 96];
let friends: string[] = ["Bob", "Charlie", "Diana"];

// 3. OBJECTS: Structured data with types
interface Person {
    name: string;
    age: number;
    isStudent?: boolean; // Optional property (note the ?)
}

let alice: Person = {
    name: "Alice",
    age: 25
};

// 4. FUNCTIONS: With typed parameters and return values
function greet(person: Person): string {
    return `Hello, ${person.name}! You are ${person.age} years old.`;
}

function calculateAverage(numbers: number[]): number {
    if (numbers.length === 0) return 0;
    const sum = numbers.reduce((acc, n) => acc + n, 0);
    return sum / numbers.length;
}

// 5. UNION TYPES: A value can be one of several types
function formatId(id: string | number): string {
    return `ID-${id}`;
}

// 6. TYPE INFERENCE: TypeScript often figures out the type for you
let message = "Hello TypeScript!"; // TypeScript knows this is a string
let count = 42; // TypeScript knows this is a number

// Export for use in browser
export { name, age, isStudent, scores, friends, alice, greet, calculateAverage, formatId, message, count };
export type { Person };
