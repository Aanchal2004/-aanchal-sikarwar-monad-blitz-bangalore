import { Sidebar } from "@/components/Sidebar";
import { DemoPanel } from "@/components/DemoPanel";

export default function DemoPage() {
  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar />
      <div className="flex-1 p-6 lg:p-8">
        <h1 className="mb-2 text-2xl font-bold">Live Demo</h1>
        <p className="mb-8 text-muted-foreground">
          Run the full multi-agent pipeline. Perfect for judge presentations.
        </p>
        <DemoPanel />
      </div>
    </div>
  );
}
