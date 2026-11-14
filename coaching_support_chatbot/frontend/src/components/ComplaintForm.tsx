// src/components/ComplaintForm.tsx
import React, { useState } from 'react';
import { complaintApi } from '../services/api';
import type { ComplaintStatus } from '../types';

export const ComplaintForm: React.FC = () => {
  const [tab, setTab] = useState<'submit' | 'lookup'>('submit');

  // Submit form state
  const [form, setForm] = useState({
    customer_name: '',
    customer_phone: '',
    category: 'general',
    description: '',
    priority: 'normal',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [ticket, setTicket] = useState<{ ticket_ref: string; lookup_token: string; message: string } | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);

  // Lookup state
  const [lookupRef, setLookupRef] = useState('');
  const [lookupToken, setLookupToken] = useState('');
  const [lookupResult, setLookupResult] = useState<ComplaintStatus | null>(null);
  const [lookupError, setLookupError] = useState<string | null>(null);
  const [lookupLoading, setLookupLoading] = useState(false);

  const validate = () => {
    const errs: Record<string, string> = {};
    if (!form.customer_name.trim()) errs.customer_name = 'Name is required.';
    if (form.customer_phone) {
      const cleaned = form.customer_phone.replace(/[\s-]/g, '');
      if (!/^\+?[6-9]\d{9}$/.test(cleaned)) errs.customer_phone = 'Enter a valid Indian mobile number.';
    }
    if (form.description.length < 10) errs.description = 'Please describe your issue in at least 10 characters.';
    return errs;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);
    const errs = validate();
    if (Object.keys(errs).length > 0) { setErrors(errs); return; }
    setErrors({});
    setIsLoading(true);
    try {
      const result = await complaintApi.create(form) as { ticket_ref: string; lookup_token: string; message: string };
      setTicket(result);
      setForm({ customer_name: '', customer_phone: '', category: 'general', description: '', priority: 'normal' });
    } catch (err: unknown) {
      setApiError(err instanceof Error ? err.message : 'Failed to submit complaint.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLookup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLookupError(null);
    if (!lookupRef.trim() || !lookupToken.trim()) {
      setLookupError('Both ticket reference and lookup token are required.');
      return;
    }
    setLookupLoading(true);
    try {
      const result = await complaintApi.lookup(lookupRef.trim(), lookupToken.trim()) as ComplaintStatus;
      setLookupResult(result);
    } catch (err: unknown) {
      setLookupError(err instanceof Error ? err.message : 'Could not find ticket with those credentials.');
    } finally {
      setLookupLoading(false);
    }
  };

  return (
    <div>
      {/* Tabs */}
      <div className="flex gap-2 mb-6" role="tablist">
        <button
          role="tab"
          id="tab-submit"
          aria-selected={tab === 'submit'}
          aria-controls="panel-submit"
          className={`btn btn--sm ${tab === 'submit' ? 'btn--primary' : 'btn--outline'}`}
          onClick={() => setTab('submit')}
        >
          Submit Complaint
        </button>
        <button
          role="tab"
          id="tab-lookup"
          aria-selected={tab === 'lookup'}
          aria-controls="panel-lookup"
          className={`btn btn--sm ${tab === 'lookup' ? 'btn--primary' : 'btn--outline'}`}
          onClick={() => setTab('lookup')}
        >
          Check Ticket Status
        </button>
      </div>

      {/* Submit tab */}
      {tab === 'submit' && (
        <div id="panel-submit" role="tabpanel" aria-labelledby="tab-submit">
          {ticket ? (
            <div className="alert alert--success" role="alert">
              <span style={{ fontSize: '1.25rem' }}>🎫</span>
              <div>
                <strong>Complaint Registered</strong>
                <p className="mt-4"><strong>Ticket Reference:</strong> {ticket.ticket_ref}</p>
                <p className="text-small text-muted mt-4">
                  Save your lookup token to check status later:{' '}
                  <code style={{ background: '#f1f5f9', padding: '2px 6px', borderRadius: 4, fontSize: '0.8rem', wordBreak: 'break-all' }}>
                    {ticket.lookup_token}
                  </code>
                </p>
                <p className="text-small mt-4">{ticket.message}</p>
                <button className="btn btn--outline btn--sm mt-4" onClick={() => setTicket(null)}>
                  Submit Another
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} noValidate aria-label="Complaint submission form">
              {apiError && <div className="alert alert--error mb-4" role="alert">⚠️ {apiError}</div>}

              <div className="grid-2" style={{ gap: '1rem' }}>
                <div className="form-group">
                  <label className="form-label form-label--required" htmlFor="comp-name">Full Name</label>
                  <input
                    id="comp-name"
                    className={`form-input ${errors.customer_name ? 'error' : ''}`}
                    type="text"
                    value={form.customer_name}
                    onChange={e => setForm({ ...form, customer_name: e.target.value })}
                    placeholder="Your name"
                    maxLength={120}
                  />
                  {errors.customer_name && <p className="form-error" role="alert">⚠️ {errors.customer_name}</p>}
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="comp-phone">Mobile Number (Optional)</label>
                  <input
                    id="comp-phone"
                    className={`form-input ${errors.customer_phone ? 'error' : ''}`}
                    type="tel"
                    value={form.customer_phone}
                    onChange={e => setForm({ ...form, customer_phone: e.target.value })}
                    placeholder="For follow-up only"
                  />
                  {errors.customer_phone && <p className="form-error" role="alert">⚠️ {errors.customer_phone}</p>}
                </div>
              </div>

              <div className="grid-2" style={{ gap: '1rem' }}>
                <div className="form-group">
                  <label className="form-label" htmlFor="comp-category">Issue Category</label>
                  <select
                    id="comp-category"
                    className="form-select"
                    value={form.category}
                    onChange={e => setForm({ ...form, category: e.target.value })}
                  >
                    <option value="general">General</option>
                    <option value="billing">Billing / Fees</option>
                    <option value="teaching_quality">Teaching Quality</option>
                    <option value="behaviour">Staff Behaviour</option>
                    <option value="facilities">Facilities</option>
                    <option value="scheduling">Scheduling</option>
                    <option value="refund">Refund</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="comp-priority">Priority</label>
                  <select
                    id="comp-priority"
                    className="form-select"
                    value={form.priority}
                    onChange={e => setForm({ ...form, priority: e.target.value })}
                  >
                    <option value="low">Low</option>
                    <option value="normal">Normal</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label form-label--required" htmlFor="comp-description">Describe Your Issue</label>
                <textarea
                  id="comp-description"
                  className={`form-textarea ${errors.description ? 'error' : ''}`}
                  value={form.description}
                  onChange={e => setForm({ ...form, description: e.target.value })}
                  placeholder="Please describe your issue in detail (minimum 10 characters)…"
                  minLength={10}
                  maxLength={3000}
                  rows={4}
                />
                {errors.description && <p className="form-error" role="alert">⚠️ {errors.description}</p>}
                <p className="form-hint">{form.description.length}/3000 characters</p>
              </div>

              <div className="alert alert--info mb-4" role="note">
                🛡️ <span>All submissions are reviewed by the Future Vision Classes administration for prompt resolution.</span>
              </div>

              <button type="submit" id="comp-submit" className="btn btn--primary btn--full" disabled={isLoading}>
                {isLoading ? 'Submitting…' : 'Submit Complaint'}
              </button>
            </form>
          )}
        </div>
      )}

      {/* Lookup tab */}
      {tab === 'lookup' && (
        <div id="panel-lookup" role="tabpanel" aria-labelledby="tab-lookup">
          <form onSubmit={handleLookup} noValidate aria-label="Ticket status lookup form">
            {lookupError && <div className="alert alert--error mb-4" role="alert">⚠️ {lookupError}</div>}

            <div className="form-group">
              <label className="form-label form-label--required" htmlFor="lookup-ref">Ticket Reference</label>
              <input
                id="lookup-ref"
                className="form-input"
                type="text"
                value={lookupRef}
                onChange={e => setLookupRef(e.target.value)}
                placeholder="e.g. TKT-20241028-AB3X"
              />
            </div>

            <div className="form-group">
              <label className="form-label form-label--required" htmlFor="lookup-token">Lookup Token</label>
              <input
                id="lookup-token"
                className="form-input"
                type="text"
                value={lookupToken}
                onChange={e => setLookupToken(e.target.value)}
                placeholder="Token provided when you submitted your complaint"
              />
              <p className="form-hint">Keep this token private — it verifies ownership of your ticket.</p>
            </div>

            <button type="submit" id="lookup-submit" className="btn btn--primary btn--full" disabled={lookupLoading}>
              {lookupLoading ? 'Looking up…' : 'Check Status'}
            </button>
          </form>

          {lookupResult && (
            <div className="alert alert--info mt-6" role="region" aria-label="Ticket status">
              <span style={{ fontSize: '1.25rem' }}>🎫</span>
              <div>
                <strong>Ticket: {lookupResult.ticket_ref}</strong>
                <p>Status: <span className={`badge badge--${lookupResult.status}`}>{lookupResult.status.replace('_', ' ')}</span></p>
                <p>Category: {lookupResult.category}</p>
                <p>Submitted: {new Date(lookupResult.created_at).toLocaleDateString('en-IN')}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
