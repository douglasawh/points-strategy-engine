/**
 * API client for Points Strategy Engine backend
 */

const API_BASE = 'http://localhost:8000/api';

export interface SessionState {
  session_id: string;
  origin: string;
  destination: string;
  start_date: string | null;
  end_date: string | null;
  prefer_nonstop: boolean;
  hotel_primary: string;
  hotel_alternates: string[];
}

export interface FlightOption {
  carrier: string;
  flight_numbers: string[];
  cabin: string;
  nonstop: boolean;
  origin: string;
  destination: string;
  depart_time_local: string | null;
  arrive_time_local: string | null;
  duration_minutes: number | null;
  score: number;
  rationale: string;
}

export interface HotelNight {
  date: string;
  hotel_name: string;
  program: string;
  points_price: number | null;
  cash_price: number | null;
  is_peak: boolean | null;
  notes: string;
}

export interface StayPlan {
  nights: HotelNight[];
  total_points: number;
  total_cash: number;
}

export interface GeneratePlanResponse {
  message: string;
  markdown: string;
  flights: FlightOption[];
  stay: StayPlan;
  state: SessionState;
}

export interface CreateSessionResponse {
  session_id: string;
  state: SessionState;
}

export interface SetDatesResponse {
  message: string;
  state: SessionState;
}

export interface SetHotelResponse {
  message: string;
  state: SessionState;
}

export interface SetNonstopResponse {
  message: string;
  state: SessionState;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export async function createSession(): Promise<CreateSessionResponse> {
  const response = await fetch(`${API_BASE}/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  return handleResponse<CreateSessionResponse>(response);
}

export async function getSession(sessionId: string): Promise<SessionState> {
  const response = await fetch(`${API_BASE}/session/${sessionId}`);
  return handleResponse<SessionState>(response);
}

export async function setDates(
  sessionId: string,
  startDate: string,
  endDate: string
): Promise<SetDatesResponse> {
  const response = await fetch(`${API_BASE}/session/${sessionId}/dates`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ start_date: startDate, end_date: endDate }),
  });
  return handleResponse<SetDatesResponse>(response);
}

export async function setHotel(
  sessionId: string,
  hotel: string
): Promise<SetHotelResponse> {
  const response = await fetch(`${API_BASE}/session/${sessionId}/hotel`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ hotel }),
  });
  return handleResponse<SetHotelResponse>(response);
}

export async function setNonstop(
  sessionId: string,
  preferNonstop: boolean
): Promise<SetNonstopResponse> {
  const response = await fetch(`${API_BASE}/session/${sessionId}/nonstop`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prefer_nonstop: preferNonstop }),
  });
  return handleResponse<SetNonstopResponse>(response);
}

export async function generatePlan(sessionId: string): Promise<GeneratePlanResponse> {
  const response = await fetch(`${API_BASE}/session/${sessionId}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  return handleResponse<GeneratePlanResponse>(response);
}

export async function healthCheck(): Promise<{ status: string; service: string }> {
  const response = await fetch(`${API_BASE}/health`);
  return handleResponse<{ status: string; service: string }>(response);
}
