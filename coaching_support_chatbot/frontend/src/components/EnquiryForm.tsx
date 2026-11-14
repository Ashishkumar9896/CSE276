// src/components/EnquiryForm.tsx
import React, { useState } from 'react';
import { enquiryApi } from '../services/api';

export const EnquiryForm: React.FC = () => {
  const [form, setForm] = useState({
    name: '',
    phone: '',
    course_interest: '',
    preferred_callback_time: '',
    message: '',
    consent_to_contact: false,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState<{ id: number; message: string } | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!form.name.trim()) newErrors.name = 'Name is required.';
    if (form.name.trim().length > 120) newErrors.name = 'Name must be under 120 characters.';
    if (!form.phone.trim()) newErrors.phone = 'Phone number is required.';
    else {
      const cleaned = form.phone.replace(/[\s-]/g, '');
      if (!/^\+?[6-9]\d{9}$/.test(cleaned)) {
        newErrors.phone = 'Enter a valid 10-digit Indian mobile number (starting with 6-9).';
      }
    }
    if (!form.consent_to_contact) newErrors.consent = 'You must consent to be contacted.';
    return newErrors;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);
    const errs = validate();
    if (Object.keys(errs).length > 0) { setErrors(errs); return; }
    setErrors({});
    setIsLoading(true);

    try {
      const result = await enquiryApi.create(form) as { id: number; message: string };
      setSuccess(result);
      setForm({ name: '', phone: '', course_interest: '', preferred_callback_time: '', message: '', consent_to_contact: false });
    } catch (err: unknown) {
      setApiError(err instanceof Error ? err.message : 'Failed to submit. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="alert alert--success mt-4" role="alert">
        <span style={{ fontSize: '1.25rem' }}>✅</span>
        <div>
          <strong>Enquiry Submitted (Ref #{success.id})</strong>
          <p style={{ marginTop: '0.25rem', fontSize: '0.875rem' }}>{success.message}</p>
          <button
            className="btn btn--outline btn--sm mt-4"
            onClick={() => setSuccess(null)}
          >
            Submit Another Enquiry
          </button>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} noValidate aria-label="Admission enquiry form">
      {apiError && (
        <div className="alert alert--error mb-4" role="alert">
          ⚠️ {apiError}
        </div>
      )}

      <div className="grid-2" style={{ gap: '1rem' }}>
        <div className="form-group">
          <label className="form-label form-label--required" htmlFor="enq-name">Full Name</label>
          <input
            id="enq-name"
            className={`form-input ${errors.name ? 'error' : ''}`}
            type="text"
            value={form.name}
            onChange={e => setForm({ ...form, name: e.target.value })}
            placeholder="Your full name"
            maxLength={120}
            aria-required="true"
            aria-describedby={errors.name ? 'enq-name-error' : undefined}
          />
          {errors.name && <p className="form-error" id="enq-name-error" role="alert">⚠️ {errors.name}</p>}
        </div>

        <div className="form-group">
          <label className="form-label form-label--required" htmlFor="enq-phone">Mobile Number</label>
          <input
            id="enq-phone"
            className={`form-input ${errors.phone ? 'error' : ''}`}
            type="tel"
            value={form.phone}
            onChange={e => setForm({ ...form, phone: e.target.value })}
            placeholder="10-digit mobile number"
            aria-required="true"
            aria-describedby={errors.phone ? 'enq-phone-error' : undefined}
          />
          {errors.phone && <p className="form-error" id="enq-phone-error" role="alert">⚠️ {errors.phone}</p>}
        </div>
      </div>

      <div className="grid-2" style={{ gap: '1rem' }}>
        <div className="form-group">
          <label className="form-label" htmlFor="enq-course">Course Interest</label>
          <select
            id="enq-course"
            className="form-select"
            value={form.course_interest}
            onChange={e => setForm({ ...form, course_interest: e.target.value })}
          >
            <option value="">Select a course…</option>
            <option value="JEE Main">JEE Main</option>
            <option value="NEET">NEET</option>
            <option value="Both JEE & NEET">Both JEE & NEET</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="enq-callback">Preferred Callback Time</label>
          <input
            id="enq-callback"
            className="form-input"
            type="text"
            value={form.preferred_callback_time}
            onChange={e => setForm({ ...form, preferred_callback_time: e.target.value })}
            placeholder="e.g. Morning 9-11 AM, Any evening"
            maxLength={120}
          />
        </div>
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="enq-message">Message (Optional)</label>
        <textarea
          id="enq-message"
          className="form-textarea"
          value={form.message}
          onChange={e => setForm({ ...form, message: e.target.value })}
          placeholder="Any specific questions or requirements…"
          maxLength={2000}
          rows={3}
        />
      </div>

      <div className="form-group">
        <label className="checkbox-wrapper">
          <input
            id="enq-consent"
            type="checkbox"
            checked={form.consent_to_contact}
            onChange={e => setForm({ ...form, consent_to_contact: e.target.checked })}
            aria-required="true"
            aria-describedby={errors.consent ? 'enq-consent-error' : undefined}
          />
          <span className="checkbox-label">
            I consent to be contacted by Future Vision Classes regarding my enquiry.
          </span>
        </label>
        {errors.consent && <p className="form-error" id="enq-consent-error" role="alert">⚠️ {errors.consent}</p>}
      </div>

      <div className="alert alert--info mb-4" role="note">
        ℹ️ <span>Our senior academic counselors typically call back within 24 business hours to guide you.</span>
      </div>

      <button
        type="submit"
        id="enq-submit"
        className="btn btn--primary btn--full"
        disabled={isLoading}
      >
        {isLoading ? 'Submitting…' : 'Submit Enquiry Request'}
      </button>
    </form>
  );
};
