import Image from "next/image";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gradient-to-br from-gray-900 to-black">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-white mb-4">
          Welcome to <span className="text-blue-500">AutoX</span>
        </h1>
        <p className="text-xl text-gray-300">
          X Automation App
        </p>
      </div>
    </main>
  );
}
