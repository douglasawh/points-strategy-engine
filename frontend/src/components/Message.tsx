import { cn } from "@/lib/utils";

export interface MessageProps {
  content: string;
  role: "user" | "assistant";
  timestamp?: Date;
}

export function Message({ content, role, timestamp }: MessageProps) {
  const isUser = role === "user";

  return (
    <div
      className={cn(
        "flex w-full mb-4",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-xl px-4 py-3 shadow-sm",
          isUser
            ? "bg-gradient-to-br from-primary to-accent text-primary-foreground"
            : "bg-card border border-border/50 text-card-foreground"
        )}
      >
        <p className="whitespace-pre-wrap text-sm">{content}</p>
        {timestamp && (
          <p
            className={cn(
              "text-xs mt-1",
              isUser ? "text-primary-foreground/70" : "text-muted-foreground"
            )}
          >
            {timestamp.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </p>
        )}
      </div>
    </div>
  );
}
