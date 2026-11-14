// src/services/api.ts
// Centralized API service for all backend communication

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: 'Request failed' }));
    const message = typeof body.detail === 'string'
      ? body.detail
      : JSON.stringify(body.detail) || 'Request failed';
    throw new ApiError(response.status, message);
  }

  if (response.status === 204) return null as T;
  return response.json();
}

// ---------------------------------------------------------------------------
// Chat
// ---------------------------------------------------------------------------

export const chatApi = {
  sendMessage: (payload: {
    message: string;
    session_token?: string;
    customer_name?: string;
    customer_phone?: string;
    consent_to_contact?: boolean;
  }) => request('/api/chat', { method: 'POST', body: JSON.stringify(payload) }),

  getHistory: (sessionToken: string) =>
    request(`/api/chat/history/${sessionToken}`),
};

// ---------------------------------------------------------------------------
// Enquiries
// ---------------------------------------------------------------------------

export const enquiryApi = {
  create: (payload: object) =>
    request('/api/enquiries', { method: 'POST', body: JSON.stringify(payload) }),
};

// ---------------------------------------------------------------------------
// Demo Requests
// ---------------------------------------------------------------------------

export const demoApi = {
  create: (payload: object) =>
    request('/api/demo-requests', { method: 'POST', body: JSON.stringify(payload) }),
};

// ---------------------------------------------------------------------------
// Complaints
// ---------------------------------------------------------------------------

export const complaintApi = {
  create: (payload: object) =>
    request('/api/complaints', { method: 'POST', body: JSON.stringify(payload) }),

  lookup: (ticket_ref: string, lookup_token: string) =>
    request('/api/complaints/lookup', {
      method: 'POST',
      body: JSON.stringify({ ticket_ref, lookup_token }),
    }),
};

// ---------------------------------------------------------------------------
// Feedback
// ---------------------------------------------------------------------------

export const feedbackApi = {
  submit: (payload: object) =>
    request('/api/feedback', { method: 'POST', body: JSON.stringify(payload) }),
};

// ---------------------------------------------------------------------------
// FAQs (public)
// ---------------------------------------------------------------------------

export const faqApi = {
  search: (q: string) => request(`/api/faqs/search?q=${encodeURIComponent(q)}`),
  categories: () => request('/api/faqs/categories'),
};

// ---------------------------------------------------------------------------
// Admin
// ---------------------------------------------------------------------------

export const adminApi = {
  login: (username: string, password: string) =>
    request('/api/admin/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  me: (token: string) => request('/api/admin/auth/me', {}, token),

  dashboard: (token: string) => request('/api/admin/dashboard', {}, token),

  // Enquiries
  listEnquiries: (token: string, page = 1, status?: string) => {
    const params = new URLSearchParams({ page: String(page) });
    if (status) params.set('status', status);
    return request(`/api/enquiries?${params}`, {}, token);
  },
  updateEnquiry: (token: string, id: number, data: object) =>
    request(`/api/enquiries/${id}`, { method: 'PATCH', body: JSON.stringify(data) }, token),

  // Complaints
  listComplaints: (token: string, page = 1, status?: string) => {
    const params = new URLSearchParams({ page: String(page) });
    if (status) params.set('status', status);
    return request(`/api/complaints?${params}`, {}, token);
  },
  updateComplaint: (token: string, id: number, data: object) =>
    request(`/api/complaints/${id}`, { method: 'PATCH', body: JSON.stringify(data) }, token),

  // Demo requests
  listDemoRequests: (token: string, page = 1, status?: string) => {
    const params = new URLSearchParams({ page: String(page) });
    if (status) params.set('status', status);
    return request(`/api/demo-requests?${params}`, {}, token);
  },
  updateDemoRequest: (token: string, id: number, data: object) =>
    request(`/api/demo-requests/${id}`, { method: 'PATCH', body: JSON.stringify(data) }, token),

  // Handovers
  listHandovers: (token: string, page = 1, status?: string) => {
    const params = new URLSearchParams({ page: String(page) });
    if (status) params.set('status', status);
    return request(`/api/handovers?${params}`, {}, token);
  },
  updateHandover: (token: string, id: number, data: object) =>
    request(`/api/handovers/${id}`, { method: 'PATCH', body: JSON.stringify(data) }, token),

  // FAQs
  listFaqs: (token: string, page = 1) =>
    request(`/api/faqs?page=${page}`, {}, token),
  createFaq: (token: string, data: object) =>
    request('/api/faqs', { method: 'POST', body: JSON.stringify(data) }, token),
  updateFaq: (token: string, id: number, data: object) =>
    request(`/api/faqs/${id}`, { method: 'PATCH', body: JSON.stringify(data) }, token),
  deleteFaq: (token: string, id: number) =>
    request(`/api/faqs/${id}`, { method: 'DELETE' }, token),
};

export { ApiError };
