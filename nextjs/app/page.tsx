"use client";

import { useState } from "react";
import Image from "next/image";

export default function Home() {
  const [count, setCount] = useState(0);
  const name="Albert"
  
  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <Image
        src="/next.svg"
        alt="Next logo"
        width={120}
        height={30}
      />
      <h1 className="text-4xl font-bold mt-6">
        Welcome to Next.js
      </h1>
      <h1 className="text-4xl font-bold">
        I am {name}
      </h1>

      <p className="mt-4 text-purple-600">
        The time now is {new Date().toLocaleTimeString()}
      </p>

      <h1 className="text-3xl font-bold mt-8">
        Count: {count}
      </h1>

      <button
        onClick={() => setCount(count + 1)}
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
      >
        Increase
      </button>
    </div>
  );
}
