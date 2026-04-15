/**
 * Typed API client for the Vuurkorf Personalisatie backend.
 * Uses relative /api paths — works on Vercel (serverless) and localhost alike.
 */

const API_BASE =
  typeof window !== "undefined"
    ? "" // browser: relative paths resolve against current origin
    : process.env.NEXT_PUBLIC_API_URL || ""; // SSR: use env var or empty (relative)

// ─── Types ───────────────────────────────────────────────────────────────────

export type JobStatus = "pending" | "processing" | "completed" | "failed";

export interface UploadResponse {
  job_id: string;
  filename: string;
  size_bytes: number;
  message: string;
}

export interface ProcessResponse {
  job_id: string;
  status: string;
  validation: ValidationResult;
  pricing: PricingResult;
  complexity_score: number;
  material: string;
  thickness: number;
  message: string;
}

export interface ValidationResult {
  status: "green" | "orange" | "red";
  issues: string[];
  island_count: number;
  parameters: {
    thickness: number;
    min_hole_diameter: number;
    min_slot_width: number;
    min_bridge_width: number;
    min_corner_radius: number;
  };
}

export interface PricingResult {
  material_price: number;
  complexity_surcharge: number;
  setup_fee: number;
  total: number;
  currency: string;
}

export interface PreviewResponse {
  job_id: string;
  status: JobStatus;
  step?: string;
  error: string | null;
  svg?: string;
  validation?: ValidationResult;
  pricing?: PricingResult;
  complexity_score?: number;
  material?: string;
  thickness?: number;
}

export interface OrderPayload {
  job_id: string;
  name: string;
  email: string;
  material: string;
  thickness: number;
  scale: number;
  offset_x: number;
  offset_y: number;
  price?: number;
}

export interface OrderResponse {
  order_id: string;
  status: string;
  price: number | null;
  message: string;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(body?.error || body?.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// ─── API calls ───────────────────────────────────────────────────────────────

/**
 * Upload an image file. Returns job_id.
 */
export async function uploadImage(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: form,
  });
  return handleResponse<UploadResponse>(res);
}

/**
 * Run the full AI processing pipeline synchronously.
 * Returns validation + pricing when complete.
 */
export async function startProcessing(
  jobId: string,
  material: string,
  thickness: number
): Promise<ProcessResponse> {
  const params = new URLSearchParams({
    job_id: jobId,
    material,
    thickness: String(thickness),
  });
  const res = await fetch(`${API_BASE}/api/process?${params}`, {
    method: "POST",
  });
  return handleResponse<ProcessResponse>(res);
}

/**
 * Fetch merged SVG preview + job result.
 */
export async function getPreview(jobId: string): Promise<PreviewResponse> {
  const res = await fetch(`${API_BASE}/api/preview?job_id=${jobId}`);
  return handleResponse<PreviewResponse>(res);
}

/**
 * Submit an order.
 */
export async function createOrder(
  payload: OrderPayload
): Promise<OrderResponse> {
  const res = await fetch(`${API_BASE}/api/orders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse<OrderResponse>(res);
}

// ─── Admin ────────────────────────────────────────────────────────────────────

export interface AdminOrder {
  id: string;
  job_id: string;
  name: string;
  email: string;
  material: string;
  thickness: number;
  scale: number;
  offset_x: number;
  offset_y: number;
  price: number | null;
  status: string;
  created_at: string;
}

/**
 * Fetch all orders (admin).
 */
export async function listOrders(): Promise<AdminOrder[]> {
  const res = await fetch(`${API_BASE}/api/orders`);
  return handleResponse<AdminOrder[]>(res);
}
