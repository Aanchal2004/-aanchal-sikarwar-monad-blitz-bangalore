import { Sidebar } from "@/components/Sidebar";
import { ChatInterface } from "@/components/ChatInterface";

export default function ChatPage() {
  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar />
      <div className="flex flex-1 flex-col p-6 lg:p-8">
        <h1 className="mb-2 text-2xl font-bold">Agent Chat</h1>
        <p className="mb-6 text-muted-foreground">
          Talk to your agent. Connects to POST /chat on the backend.
        </p>
        <div className="flex-1 min-h-[500px]">
          <ChatInterface className="h-full min-h-[500px]" />
        </div>
      </div>
    </div>
  );
}
