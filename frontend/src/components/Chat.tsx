import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Message, type MessageProps } from "./Message";

interface QuickAction {
  label: string;
  message: string;
  primary?: boolean;
}

interface ChatProps {
  messages: MessageProps[];
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
  hasDates?: boolean;
  hasGenerated?: boolean;
}

export function Chat({
  messages,
  onSendMessage,
  isLoading = false,
  hasDates = false,
  hasGenerated = false,
}: ChatProps) {
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput("");
    }
  };

  const handleQuickAction = (message: string) => {
    if (!isLoading) {
      onSendMessage(message);
    }
  };

  // Determine which quick actions to show based on current state
  const getQuickActions = (): QuickAction[] => {
    if (!hasDates) {
      return [
        { label: "Nov 20 - Dec 4, 2027", message: "Nov 20 2027 to Dec 4 2027" },
        { label: "Dec 15 - Dec 29, 2027", message: "Dec 15 2027 to Dec 29 2027" },
        { label: "Mar 1 - Mar 15, 2028", message: "Mar 1 2028 to Mar 15 2028" },
      ];
    }

    if (!hasGenerated) {
      return [
        { label: "Generate Plan", message: "generate plan", primary: true },
        { label: "Start at Park Hyatt (default)", message: "start at Park Hyatt" },
        { label: "Start at Andaz", message: "start at Andaz" },
      ];
    }

    return [
      { label: "Switch to Park Hyatt", message: "start at Park Hyatt" },
      { label: "Switch to Andaz", message: "start at Andaz" },
      { label: "Regenerate Plan", message: "generate plan" },
      { label: "New Dates", message: "status" },
    ];
  };

  const quickActions = getQuickActions();

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-muted-foreground py-8">
              <p className="text-lg font-medium mb-2">
                Points Strategy Engine
              </p>
              <p className="text-sm mb-2">
                Plan your Tokyo trip using points and miles.
              </p>
              <div className="inline-block bg-primary/10 text-primary px-3 py-1 rounded-full text-xs font-medium mb-4">
                MSP → Tokyo (HND)
              </div>
              <p className="text-sm font-medium text-foreground">
                Step 1: Select your travel dates
              </p>
            </div>
          )}
          {messages.map((msg, idx) => (
            <Message key={idx} {...msg} />
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-lg px-4 py-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Quick actions */}
      <div className="border-t px-4 py-3 bg-muted/30">
        <p className="text-xs text-muted-foreground mb-2">
          {!hasDates && "Step 1: Select your travel dates for Tokyo"}
          {hasDates && !hasGenerated && "Step 2: Pick your Tokyo hotel, then generate"}
          {hasGenerated && "Plan ready! Make changes:"}
        </p>
        <div className="flex flex-wrap gap-2">
          {quickActions.map((action) => (
            <Button
              key={action.label}
              variant={action.primary ? "default" : "outline"}
              size="sm"
              onClick={() => handleQuickAction(action.message)}
              disabled={isLoading}
              className="text-xs"
            >
              {action.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Input area */}
      <form onSubmit={handleSubmit} className="border-t p-4">
        <div className="flex gap-2">
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              !hasDates
                ? "Or type custom dates (e.g., Jan 5 2028 to Jan 20 2028)..."
                : hasDates && !hasGenerated
                ? "Or type: start at Park Hyatt, generate plan..."
                : "Type: new dates, switch hotel, regenerate..."
            }
            disabled={isLoading}
            className="flex-1"
          />
          <Button type="submit" disabled={!input.trim() || isLoading}>
            Send
          </Button>
        </div>
      </form>
    </div>
  );
}
