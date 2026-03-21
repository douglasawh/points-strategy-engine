import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { FlightOption, StayPlan, SessionState } from "@/lib/api";

interface PlanViewProps {
  flights: FlightOption[];
  stay: StayPlan;
  state: SessionState;
  markdown?: string;
}

export function PlanView({ flights, stay, state, markdown }: PlanViewProps) {
  const hasData = flights.length > 0 || stay.nights.length > 0;

  if (!hasData) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        <p>Set dates and generate a plan to see results here.</p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-4 space-y-6">
        {/* Trip Summary */}
        <Card>
          <CardHeader>
            <CardTitle>Trip Summary</CardTitle>
            <CardDescription>
              {state.origin} to {state.destination}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium">Dates:</span>{" "}
                {state.start_date} to {state.end_date}
              </div>
              <div>
                <span className="font-medium">Nonstop:</span>{" "}
                {state.prefer_nonstop ? "Yes" : "No"}
              </div>
              <div>
                <span className="font-medium">Primary Hotel:</span>{" "}
                {state.hotel_primary}
              </div>
              <div>
                <span className="font-medium">Alternates:</span>{" "}
                {state.hotel_alternates.join(", ")}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Flights */}
        {flights.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Flights</CardTitle>
              <CardDescription>
                {flights.length} option{flights.length > 1 ? "s" : ""} found
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {flights.map((flight, idx) => (
                  <div
                    key={idx}
                    className="border border-border/50 rounded-xl p-4 bg-secondary/30 hover:bg-secondary/50 transition-colors"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium">
                          {flight.carrier} {flight.flight_numbers.join(", ")}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {flight.origin} to {flight.destination} |{" "}
                          {flight.nonstop ? "Nonstop" : "1-stop"} | {flight.cabin}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-lg text-primary">
                          {flight.score.toFixed(1)}
                        </p>
                        <p className="text-xs text-muted-foreground">score</p>
                      </div>
                    </div>
                    {flight.rationale && (
                      <p className="text-sm mt-2 text-muted-foreground">
                        {flight.rationale}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Hotel Nights */}
        {stay.nights.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Hotel Nights</CardTitle>
              <CardDescription>
                {stay.nights.length} nights | {stay.total_points.toLocaleString()} points total
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {stay.nights.map((night, idx) => (
                  <div
                    key={idx}
                    className="flex justify-between items-center py-2 border-b last:border-0"
                  >
                    <div>
                      <p className="font-medium">{night.date}</p>
                      <p className="text-sm text-muted-foreground">
                        {night.hotel_name}
                        {night.is_peak && (
                          <span className="ml-2 text-xs bg-accent/20 text-accent px-2 py-0.5 rounded-full">
                            peak
                          </span>
                        )}
                      </p>
                    </div>
                    <div className="text-right">
                      {night.points_price ? (
                        <p className="font-medium">
                          {night.points_price.toLocaleString()} pts
                        </p>
                      ) : (
                        <p className="text-muted-foreground">--</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 pt-4 border-t border-border/50">
                <div className="flex justify-between font-bold">
                  <span>Total Points</span>
                  <span className="text-primary">{stay.total_points.toLocaleString()}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Raw Markdown (collapsible) */}
        {markdown && (
          <Card>
            <CardHeader>
              <CardTitle>Full Plan (Markdown)</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-xs whitespace-pre-wrap bg-muted p-4 rounded-lg overflow-auto">
                {markdown}
              </pre>
            </CardContent>
          </Card>
        )}
      </div>
    </ScrollArea>
  );
}
