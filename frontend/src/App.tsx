import { useState, useEffect, useCallback } from "react";
import { Chat } from "@/components/Chat";
import { PlanView } from "@/components/PlanView";
import type { MessageProps } from "@/components/Message";
import {
  createSession,
  setDates,
  setHotel,
  setNonstop,
  generatePlan,
  type SessionState,
  type FlightOption,
  type StayPlan,
} from "@/lib/api";

function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionState, setSessionState] = useState<SessionState | null>(null);
  const [messages, setMessages] = useState<MessageProps[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [flights, setFlights] = useState<FlightOption[]>([]);
  const [stay, setStay] = useState<StayPlan>({ nights: [], total_points: 0, total_cash: 0 });
  const [markdown, setMarkdown] = useState<string>("");

  // Initialize session on mount
  useEffect(() => {
    const initSession = async () => {
      try {
        const response = await createSession();
        setSessionId(response.session_id);
        setSessionState(response.state);
        addAssistantMessage(
          "Session created. You can set dates, choose a hotel, and generate a plan."
        );
      } catch (error) {
        addAssistantMessage(
          `Failed to connect to backend. Make sure the API is running on port 8000.`
        );
      }
    };
    initSession();
  }, []);

  const addUserMessage = (content: string) => {
    setMessages((prev) => [
      ...prev,
      { content, role: "user" as const, timestamp: new Date() },
    ]);
  };

  const addAssistantMessage = (content: string) => {
    setMessages((prev) => [
      ...prev,
      { content, role: "assistant" as const, timestamp: new Date() },
    ]);
  };

  // Parse user input and determine intent
  const parseIntent = (
    input: string
  ): { action: string; params: Record<string, string> } => {
    const lower = input.toLowerCase().trim();

    // Date pattern: "Nov 20 2027 to Dec 4 2027" or "2027-11-20 to 2027-12-04"
    const datePattern =
      /(\w+\s+\d+\s+\d{4}|\d{4}-\d{2}-\d{2})\s+(?:to|-)\s+(\w+\s+\d+\s+\d{4}|\d{4}-\d{2}-\d{2})/i;
    const dateMatch = input.match(datePattern);
    if (dateMatch) {
      return {
        action: "set_dates",
        params: { start: dateMatch[1], end: dateMatch[2] },
      };
    }

    // Hotel pattern
    if (lower.includes("start at") || lower.includes("hotel")) {
      if (lower.includes("andaz")) {
        return { action: "set_hotel", params: { hotel: "Andaz Tokyo Toranomon Hills" } };
      }
      if (lower.includes("park hyatt") || lower.includes("hyatt")) {
        return { action: "set_hotel", params: { hotel: "Park Hyatt Tokyo" } };
      }
    }

    // Nonstop preference
    if (lower.includes("nonstop") || lower.includes("direct")) {
      const prefer = !lower.includes("no ") && !lower.includes("don't");
      return { action: "set_nonstop", params: { prefer: String(prefer) } };
    }

    // Generate plan
    if (
      lower.includes("generate") ||
      lower.includes("show plan") ||
      lower.includes("create plan") ||
      lower.includes("make plan")
    ) {
      return { action: "generate", params: {} };
    }

    // Status
    if (lower.includes("status") || lower.includes("current")) {
      return { action: "status", params: {} };
    }

    return { action: "unknown", params: {} };
  };

  // Parse natural language date to ISO format
  const parseDate = (dateStr: string): string => {
    // If already ISO format
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
      return dateStr;
    }

    // Parse "Nov 20 2027" format
    const months: Record<string, string> = {
      jan: "01", feb: "02", mar: "03", apr: "04",
      may: "05", jun: "06", jul: "07", aug: "08",
      sep: "09", oct: "10", nov: "11", dec: "12",
    };

    const match = dateStr.match(/(\w+)\s+(\d+)\s+(\d{4})/i);
    if (match) {
      const month = months[match[1].toLowerCase().slice(0, 3)];
      const day = match[2].padStart(2, "0");
      const year = match[3];
      if (month) {
        return `${year}-${month}-${day}`;
      }
    }

    return dateStr; // Return as-is if parsing fails
  };

  const handleSendMessage = useCallback(
    async (input: string) => {
      if (!sessionId) {
        addAssistantMessage("No session available. Please refresh the page.");
        return;
      }

      addUserMessage(input);
      setIsLoading(true);

      try {
        const { action, params } = parseIntent(input);

        switch (action) {
          case "set_dates": {
            const startDate = parseDate(params.start);
            const endDate = parseDate(params.end);
            const response = await setDates(sessionId, startDate, endDate);
            setSessionState(response.state);
            addAssistantMessage(response.message);
            break;
          }

          case "set_hotel": {
            const response = await setHotel(sessionId, params.hotel);
            setSessionState(response.state);
            addAssistantMessage(response.message);
            break;
          }

          case "set_nonstop": {
            const prefer = params.prefer === "true";
            const response = await setNonstop(sessionId, prefer);
            setSessionState(response.state);
            addAssistantMessage(response.message);
            break;
          }

          case "generate": {
            const response = await generatePlan(sessionId);
            setSessionState(response.state);
            setFlights(response.flights);
            setStay(response.stay);
            setMarkdown(response.markdown);
            addAssistantMessage(
              `${response.message}\n\n` +
                `Found ${response.flights.length} flight options and ` +
                `${response.stay.nights.length} hotel nights ` +
                `(${response.stay.total_points.toLocaleString()} points total).`
            );
            break;
          }

          case "status": {
            if (sessionState) {
              addAssistantMessage(
                `Current session:\n` +
                  `- Route: ${sessionState.origin} to ${sessionState.destination}\n` +
                  `- Dates: ${sessionState.start_date || "not set"} to ${sessionState.end_date || "not set"}\n` +
                  `- Hotel: ${sessionState.hotel_primary}\n` +
                  `- Nonstop: ${sessionState.prefer_nonstop ? "Yes" : "No"}`
              );
            }
            break;
          }

          default:
            addAssistantMessage(
              `I didn't understand that. Try:\n` +
                `- Setting dates: "Nov 20 2027 to Dec 4 2027"\n` +
                `- Setting hotel: "start at Andaz" or "start at Park Hyatt"\n` +
                `- Flight preference: "prefer nonstop" or "no nonstop"\n` +
                `- Generate plan: "generate plan" or "show plan"`
            );
        }
      } catch (error) {
        const message = error instanceof Error ? error.message : "An error occurred";
        addAssistantMessage(`Error: ${message}`);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId, sessionState]
  );

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="border-b border-border/50 px-6 py-4 bg-gradient-to-r from-primary/10 via-accent/5 to-transparent">
        <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
          Points Strategy Engine
        </h1>
        <p className="text-sm text-muted-foreground">
          Plan your Tokyo trip with points and miles
        </p>
      </header>

      {/* Main content */}
      <main className="flex-1 flex overflow-hidden">
        {/* Chat panel */}
        <div className="w-1/2 border-r flex flex-col">
          <Chat
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            hasDates={!!(sessionState?.start_date && sessionState?.end_date)}
            hasGenerated={flights.length > 0 || stay.nights.length > 0}
          />
        </div>

        {/* Plan view panel */}
        <div className="w-1/2">
          {sessionState && (
            <PlanView
              flights={flights}
              stay={stay}
              state={sessionState}
              markdown={markdown}
            />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
