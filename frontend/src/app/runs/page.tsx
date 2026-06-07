import Link from 'next/link';
export default function RunsIndex() {
  return (
    <div className="mx-auto max-w-xl px-6 py-16 text-center text-sm text-gray-500">
      <p>Select a run ID from the Operations Console to view its receipt.</p>
      <Link href="/console" className="mt-4 inline-block text-indigo-600 hover:underline">Go to Console</Link>
    </div>
  );
}
