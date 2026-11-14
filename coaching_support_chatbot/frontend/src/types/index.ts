// src/types/index.ts
// TypeScript type definitions for the chatbot application

export interface SuggestedAction {
  label: string;
  message: string;
}

export interface ChatMessage {
  id: string;
  sender: 'customer' | 'bot';
  body: string;
  intent?: string;
  created_at: string;
  suggestedActions?: SuggestedAction[];
}

export interface ChatResponse {
  session_token: string;
  reply: string;
  intent: string;
  handover: boolean;
  suggested_actions: SuggestedAction[];
}

export interface EnquiryForm {
  name: string;
  phone: string;
  course_interest?: string;
  preferred_callback_time?: string;
  message?: string;
  consent_to_contact: boolean;
}

export interface DemoRequestForm {
  name: string;
  phone: string;
  course_interest?: string;
  preferred_date?: string;
  preferred_time?: string;
  message?: string;
  consent_to_contact: boolean;
}

export interface ComplaintForm {
  customer_name: string;
  customer_phone?: string;
  category: string;
  description: string;
  priority: string;
}

export interface ComplaintCreated {
  ticket_ref: string;
  lookup_token: string;
  status: string;
  message: string;
}

export interface ComplaintStatus {
  ticket_ref: string;
  status: string;
  created_at: string;
  category: string;
}

export interface HandoverForm {
  session_token?: string;
  customer_name?: string;
  customer_phone?: string;
  preferred_contact_method: string;
}

export interface FeedbackForm {
  session_token?: string;
  message_id?: number;
  rating: 'helpful' | 'not_helpful';
  comment?: string;
  unanswered_question?: string;
}

export interface DashboardStats {
  total_conversations: number;
  open_enquiries: number;
  open_complaints: number;
  pending_demo_requests: number;
  pending_handovers: number;
  published_faqs: number;
  helpful_feedback: number;
  not_helpful_feedback: number;
}

export interface FAQ {
  id: number;
  faq_code: string;
  category: string;
  question: string;
  answer: string;
  source_url?: string;
  source_type: string;
  verification_status: string;
  is_published: boolean;
  internal_notes?: string;
  created_at: string;
  updated_at: string;
  last_checked?: string;
}

export interface Enquiry {
  id: number;
  name: string;
  phone: string;
  course_interest?: string;
  preferred_callback_time?: string;
  message?: string;
  consent_to_contact: boolean;
  status: string;
  admin_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface DemoRequest {
  id: number;
  name: string;
  phone: string;
  course_interest?: string;
  preferred_date?: string;
  preferred_time?: string;
  message?: string;
  consent_to_contact: boolean;
  status: string;
  admin_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ComplaintTicket {
  id: number;
  ticket_ref: string;
  customer_name: string;
  customer_phone?: string;
  category: string;
  description: string;
  priority: string;
  status: string;
  assigned_agent?: string;
  resolution_notes?: string;
  admin_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  page_size: number;
  items: T[];
}

export interface AdminLoginForm {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
