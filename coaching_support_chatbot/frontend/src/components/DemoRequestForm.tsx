// src/components/DemoRequestForm.tsx
import React, { useState } from 'react';
import { demoApi } from '../services/api';

export const DemoRequestForm: React.FC = () => {
  const today = new Date().toISOString().split('T')[0];
  const [form, setForm] = useState({
    name: '',
    phone: '',
    course_interest: '',
    preferred_date: '',
    preferred_time: '',
    message: '',
    consent_to_contact: false,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState<{ id: number; message: string } | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);

  const validate = () => {
    const errs: Record<string, string> = {};
    if (!form.name.trim()) errs.name = 'Name is required.';
    if (!form.phone.trim()) errs.phone = 'Phone number is required.';
    else {
      const cleaned = form.phone.replace(/[\s-]/g, '');
      if (!/^\+?[6-9]\d{9}$/.test(cleaned)) errs.phone = 'Enter a valid 10-digit Indian mobile number.';
    }
    if (form.preferred_date && form.preferred_date < today) {
      errs.preferred_date = 'Preferred date cannot be in the past.';
    }
    if (!form.consent_to_contact) errs.consent = 'You must consent to be contacted.';
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
      const result = await demoApi.create(form) as { id: number; message: string };
      setSuccess(result);
      setForm({ name: '', phone: '', course_interest: '', preferred_date: '', preferred_time: '', message: '', consent_to_contact: false });
    } catch (err: unknown) {
      setApiError(err instanceof Error ? err.message : 'Submission failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="alert alert--success mt-4" role="alert">
        <span style={{ fontSize: '1.25rem' }}>✅</span>
        <div>
          <strong>Demo Request Recorded (Ref #{success.id})</strong>
          <p style={{ marginTop: '0.25rem', fontSize: '0.875rem' }}>{success.message}</p>
          <button className="btn btn--outline btn--sm mt-4" onClick={() => setSuccess(null)}>
            Submit Another Request
          </button>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} noValidate aria-label="Demo class request form">
      {apiError && <div className="alert alert--error mb-4" role="alert">⚠️ {apiError}</div>}

      <div className="grid-2" style={{ gap: '1rem' }}>
        <div className="form-group">
          <label className="form-label form-label--required" htmlFor="demo-name">Full Name</label>
          <input
            id="demo-name"
            className={`form-input ${errors.name ? 'error' : ''}`}
            type="text"
            value={form.name}
            onChange={e => setForm({ ...form, name: e.target.value })}
            placeholder="Your full name"
            maxLength={120}
          />
          {errors.name && <p className="form-error" role="alert">⚠️ {errors.name}</p>}
        </div>

        <div className="form-group">
          <label className="form-label form-label--required" htmlFor="demo-phone">Mobile Number</label>
          <input
            id="demo-phone"
            className={`form-input ${errors.phone ? 'error' : ''}`}
            type="tel"
            value={form.phone}
            onChange={e => setForm({ ...form, phone: e.target.value })}
            placeholder="10-digit mobile number"
          />
          {errors.phone && <p className="form-error" role="alert">⚠️ {errors.phone}</p>}
        </div>
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="demo-course">Course Interest</label>
        <select
          id="demo-course"
          className="form-select"
          value={form.course_interest}
          onChange={e => setForm({ ...form, course_interest: e.target.value })}
        >
          <option value="">Select a course…</option>
          <option value="JEE Main">JEE Main</option>
          <option value="NEET">NEET</option>
          <option value="Both JEE & NEET">Both JEE & NEET</option>
          <option value="Counselling only">Counselling only</option>
          <option value="Other">Other</option>
        </select>
      </div>

      <div className="grid-2" style={{ gap: '1rem' }}>
        <div className="form-group">
          <label className="form-label" htmlFor="demo-date">Preferred Date</label>
          <input
            id="demo-date"
            className={`form-input ${errors.preferred_date ? 'error' : ''}`}
            type="date"
            value={form.preferred_date}
            min={today}
            onChange={e => setForm({ ...form, preferred_date: e.target.value })}
          />
          {errors.preferred_date && <p className="form-error" role="alert">⚠️ {errors.preferred_date}</p>}
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="demo-time">Preferred Time</label>
          <select
            id="demo-time"
            className="form-select"
            value={form.preferred_time}
            onChange={e => setForm({ ...form, preferred_time: e.target.value })}
          >
            <option value="">Select a time…</option>
            <option value="Morning (9-11 AM)">Morning (9–11 AM)</option>
            <option value="Late Morning (11 AM-1 PM)">Late Morning (11 AM–1 PM)</option>
            <option value="Afternoon (2-4 PM)">Afternoon (2–4 PM)</option>
            <option value="Evening (5-7 PM)">Evening (5–7 PM)</option>
          </select>
          <p className="form-hint">⚠️ Times shown are preferences, not confirmed slots.</p>
        </div>
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="demo-message">Additional Notes</label>
        <textarea
          id="demo-message"
          className="form-textarea"
          value={form.message}
          onChange={e => setForm({ ...form, message: e.target.value })}
          placeholder="Any specific questions or requirements for the demo…"
          maxLength={2000}
          rows={3}
        />
      </div>

      <div className="form-group">
        <label className="checkbox-wrapper">
          <input
            id="demo-consent"
            type="checkbox"
            checked={form.consent_to_contact}
            onChange={e => setForm({ ...form, consent_to_contact: e.target.checked })}
          />
          <span className="checkbox-label">
            I consent to be contacted by Future Vision Classes to confirm my demo class request.
          </span>
        </label>
        {errors.consent && <p className="form-error" role="alert">⚠️ {errors.consent}</p>}
      </div>

      <div className="alert alert--info mb-4" role="note">
        ℹ️ <span>Our admissions desk will contact you within 24 hours to confirm your trial slot and provide the lecture schedule.</span>
      </div>

      <button type="submit" id="demo-submit" className="btn btn--primary btn--full" disabled={isLoading}>
        {isLoading ? 'Submitting…' : 'Request Demo Class'}
      </button>
    </form>
  );
};
