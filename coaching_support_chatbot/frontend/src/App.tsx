// src/App.tsx
import React, { useState } from 'react';
import { ChatWidget } from './components/ChatWidget';
import { EnquiryForm } from './components/EnquiryForm';
import { DemoRequestForm } from './components/DemoRequestForm';
import { ComplaintForm } from './components/ComplaintForm';

export const App: React.FC = () => {
  const [activeModal, setActiveModal] = useState<'enquiry' | 'demo' | 'complaint' | null>(null);

  const openChat = () => {
    const toggle = document.querySelector('.chat-toggle') as HTMLButtonElement | null;
    toggle?.click();
  };

  return (
    <div className="app-container">
      {/* Top Notification Announcement Bar */}
      <div style={{
        background: 'linear-gradient(90deg, #081530 0%, #0f2044 50%, #1d4ed8 100%)',
        color: '#f8fafc',
        padding: '8px 16px',
        fontSize: '0.8125rem',
        fontWeight: 500,
        textAlign: 'center',
        borderBottom: '1px solid rgba(255,255,255,0.1)'
      }}>
        <span>🌟 <strong>Admissions Open for Session 2026–27</strong> — Classes 9th to 12th, IIT-JEE & NEET-UG | Merit Scholarships up to 90% | Sector 16, Sonipat Campus</span>
      </div>

      {/* Main Navigation */}
      <header className="navbar">
        <div className="container navbar__inner">
          <a href="#" className="navbar__brand">
            <div className="navbar__logo-icon">🎓</div>
            <div>
              <div className="navbar__title">Future Vision Classes</div>
              <div className="navbar__subtitle">Premier Coaching Institute • Sonipat</div>
            </div>
          </a>
          <nav className="navbar__nav">
            <a href="#programs" className="navbar__link">Programs & Fees</a>
            <a href="#why-us" className="navbar__link">Why Us</a>
            <a href="#timings" className="navbar__link">Batch Timings</a>
            <a href="#campus" className="navbar__link">Campus</a>
            <button
              className="navbar__link"
              style={{ background: 'none', border: 'none', cursor: 'pointer' }}
              onClick={() => setActiveModal('complaint')}
            >
              Support Portal
            </button>
            <button
              className="btn btn--secondary btn--sm"
              style={{ marginLeft: 'var(--space-2)' }}
              onClick={() => setActiveModal('enquiry')}
            >
              Enquire
            </button>
            <button
              className="btn btn--primary btn--sm"
              onClick={() => setActiveModal('demo')}
            >
              Book Free Demo
            </button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="container hero__content">
          <div className="hero__badge">🏆 Premier Coaching for IIT-JEE, NEET & Boards</div>
          <h1 className="hero__title">
            Empowering Ambitions. <span>Inspiring Rankers.</span>
          </h1>
          <p className="hero__desc" style={{ maxWidth: '720px', margin: '0 auto var(--space-8)' }}>
            Structured classroom coaching for Classes 9, 10, 11, and 12 with senior faculty,
            comprehensive study packages, Daily Practice Problem (DPP) sets, and national-level mock tests.
          </p>

          <div className="hero__cta-group" style={{ display: 'flex', gap: 'var(--space-4)', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button className="btn btn--primary btn--lg" onClick={() => setActiveModal('demo')}>
              📅 Book Free Demo Class
            </button>
            <button className="btn btn--secondary btn--lg" onClick={() => setActiveModal('enquiry')}>
              📋 Admission Enquiry
            </button>
            <button
              className="btn btn--outline btn--lg"
              style={{ color: '#fff', borderColor: 'rgba(255,255,255,0.4)' }}
              onClick={openChat}
            >
              💬 Talk to AI Advisor
            </button>
          </div>

          {/* Quick Metrics Bar */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: 'var(--space-4)',
            maxWidth: '860px',
            margin: 'var(--space-12) auto 0',
            padding: 'var(--space-4)',
            background: 'rgba(255, 255, 255, 0.08)',
            borderRadius: 'var(--radius-xl)',
            backdropFilter: 'blur(8px)',
            border: '1px solid rgba(255, 255, 255, 0.15)'
          }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#60a5fa' }}>95%+</div>
              <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.8)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Board Success Rate</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#34d399' }}>15+ Years</div>
              <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.8)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Teaching Legacy</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#fbbf24' }}>1:20</div>
              <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.8)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Personalized Batch Ratio</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#a78bfa' }}>50+ Tests</div>
              <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.8)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Mock Exams & DPPs</div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main className="container" style={{ padding: 'var(--space-12) var(--space-4)' }}>
        {/* Quick Action Services */}
        <section style={{ marginBottom: 'var(--space-16)' }}>
          <div className="section-title-group">
            <div className="section-kicker">Student & Parent Desk</div>
            <h2 className="section-title">How Can We Help You Today?</h2>
            <p className="section-desc">Select an option below or chat with our 24/7 AI Academic Advisor.</p>
          </div>

          <div className="features-grid">
            <div className="feature-card" onClick={() => setActiveModal('enquiry')}>
              <div className="feature-icon">📝</div>
              <div className="feature-title">Admission Enquiry</div>
              <div className="feature-desc">Request course prospectuses, fee installment options, and scholarship info.</div>
            </div>
            <div className="feature-card" onClick={() => setActiveModal('demo')}>
              <div className="feature-icon">🎯</div>
              <div className="feature-title">Book a Free Demo</div>
              <div className="feature-desc">Experience a live classroom lecture with our senior faculty before joining.</div>
            </div>
            <div className="feature-card" onClick={() => setActiveModal('complaint')}>
              <div className="feature-icon">🛡️</div>
              <div className="feature-title">Grievance & Support</div>
              <div className="feature-desc">Submit a concern or track an existing ticket with secure reference ID.</div>
            </div>
            <div className="feature-card" onClick={openChat}>
              <div className="feature-icon">🤖</div>
              <div className="feature-title">AI Academic Advisor</div>
              <div className="feature-desc">Instant real-time answers about batch timings, syllabus, fees, and campus location.</div>
            </div>
          </div>
        </section>

        {/* Flagship Programs & Fee Structure */}
        <section id="programs" style={{ marginBottom: 'var(--space-16)' }}>
          <div className="section-title-group">
            <div className="section-kicker" id="fees">Curriculum & Transparent Pricing</div>
            <h2 className="section-title">Our Programs & Fee Structure</h2>
            <p className="section-desc">Structured learning pathways for competitive success and board excellence.</p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 'var(--space-6)' }}>
            {/* 2-Year Integrated Program */}
            <div className="card card--hover" style={{ borderTop: '4px solid var(--clr-blue)' }}>
              <div className="card__header">
                <span className="badge badge--primary" style={{ marginBottom: 'var(--space-2)' }}>Flagship 2-Year Program</span>
                <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--clr-navy)' }}>2-Year Integrated (10th Passed)</h3>
                <div style={{ marginTop: 'var(--space-2)', fontSize: '1.35rem', fontWeight: 800, color: 'var(--clr-blue)' }}>
                  ₹1.75 Lakh <span style={{ fontSize: '0.75rem', fontWeight: 500, color: 'var(--clr-gray-500)' }}>/ Total 2 Years</span>
                </div>
              </div>
              <div className="card__body">
                <p style={{ color: 'var(--clr-gray-600)', fontSize: '0.875rem', lineHeight: '1.6' }}>
                  Comprehensive IIT-JEE & NEET-UG preparation for students transitioning from Class 10 to 11.
                </p>
                <ul style={{ paddingLeft: 'var(--space-4)', margin: 'var(--space-3) 0', color: 'var(--clr-gray-600)', fontSize: '0.8125rem', lineHeight: '1.7' }}>
                  <li>Class 11th & 12th Board + Competitive Syllabus</li>
                  <li>Daily Practice Problem (DPP) Booklets</li>
                  <li>50+ All-India Test Series (AITS) Mock Exams</li>
                  <li>1-on-1 Faculty Doubts & Performance Tracking</li>
                </ul>
              </div>
              <div className="card__footer" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--clr-gray-500)' }}>JEE / NEET Track</span>
                <button className="btn btn--outline btn--sm" onClick={() => setActiveModal('demo')}>Book Trial</button>
              </div>
            </div>

            {/* 1-Year Target Batch */}
            <div className="card card--hover" style={{ borderTop: '4px solid var(--clr-success)' }}>
              <div className="card__header">
                <span className="badge badge--success" style={{ marginBottom: 'var(--space-2)' }}>Target / Dropper</span>
                <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--clr-navy)' }}>1-Year Intensive JEE & NEET</h3>
                <div style={{ marginTop: 'var(--space-2)', fontSize: '1.35rem', fontWeight: 800, color: 'var(--clr-blue)' }}>
                  ₹90,000 <span style={{ fontSize: '0.75rem', fontWeight: 500, color: 'var(--clr-gray-500)' }}>/ 1 Year</span>
                </div>
              </div>
              <div className="card__body">
                <p style={{ color: 'var(--clr-gray-600)', fontSize: '0.875rem', lineHeight: '1.6' }}>
                  High-intensity fast-track coaching for Class 12th appearing and dropper/repeater students.
                </p>
                <ul style={{ paddingLeft: 'var(--space-4)', margin: 'var(--space-3) 0', color: 'var(--clr-gray-600)', fontSize: '0.8125rem', lineHeight: '1.7' }}>
                  <li>Daily 4-Hour Rigorous Classroom Sessions</li>
                  <li>Speed & Accuracy Problem Solving Clinics</li>
                  <li>National Rank Percentile Benchmark Testing</li>
                  <li>Special Formula Sheets & Revision Notes</li>
                </ul>
              </div>
              <div className="card__footer" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--clr-gray-500)' }}>Morning / Evening</span>
                <button className="btn btn--outline btn--sm" onClick={() => setActiveModal('demo')}>Book Trial</button>
              </div>
            </div>

            {/* Classes 11 & 12 PCM / PCB */}
            <div className="card card--hover" style={{ borderTop: '4px solid var(--clr-warning)' }}>
              <div className="card__header">
                <span className="badge badge--warning" style={{ marginBottom: 'var(--space-2)' }}>Classes 11 & 12</span>
                <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--clr-navy)' }}>Board + Competitive (PCM / PCB)</h3>
                <div style={{ marginTop: 'var(--space-2)', fontSize: '1.35rem', fontWeight: 800, color: 'var(--clr-blue)' }}>
                  ₹20,000 <span style={{ fontSize: '0.75rem', fontWeight: 500, color: 'var(--clr-gray-500)' }}>/ Subject / Year</span>
                </div>
              </div>
              <div className="card__body">
                <p style={{ color: 'var(--clr-gray-600)', fontSize: '0.875rem', lineHeight: '1.6' }}>
                  Modular subject coaching in Physics, Chemistry, Mathematics, and Biology for Board & competitive mastery.
                </p>
                <ul style={{ paddingLeft: 'var(--space-4)', margin: 'var(--space-3) 0', color: 'var(--clr-gray-600)', fontSize: '0.8125rem', lineHeight: '1.7' }}>
                  <li>PCM for Engineering or PCB for Medical</li>
                  <li>NCERT Line-by-Line & Advanced Numericals</li>
                  <li>Weekly Board Style Subjective Exam Practice</li>
                  <li>Dedicated Evening Batches for School Students</li>
                </ul>
              </div>
              <div className="card__footer" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--clr-gray-500)' }}>PCM / PCB Options</span>
                <button className="btn btn--outline btn--sm" onClick={() => setActiveModal('demo')}>Book Trial</button>
              </div>
            </div>

            {/* Classes 9 & 10 Foundation */}
            <div className="card card--hover" style={{ borderTop: '4px solid #6366f1' }}>
              <div className="card__header">
                <span className="badge" style={{ background: '#e0e7ff', color: '#4338ca', marginBottom: 'var(--space-2)' }}>Classes 9 & 10</span>
                <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--clr-navy)' }}>Foundation & Boards (9th & 10th)</h3>
                <div style={{ marginTop: 'var(--space-2)', fontSize: '1.35rem', fontWeight: 800, color: 'var(--clr-blue)' }}>
                  ₹10,000 <span style={{ fontSize: '0.75rem', fontWeight: 500, color: 'var(--clr-gray-500)' }}>/ Subject / Year</span>
                </div>
              </div>
              <div className="card__body">
                <p style={{ color: 'var(--clr-gray-600)', fontSize: '0.875rem', lineHeight: '1.6' }}>
                  Targeted board preparation and Olympiad foundation in Science, Maths, and English.
                </p>
                <ul style={{ paddingLeft: 'var(--space-4)', margin: 'var(--space-3) 0', color: 'var(--clr-gray-600)', fontSize: '0.8125rem', lineHeight: '1.7' }}>
                  <li>Science, Maths & English (₹10,000 / subject / yr)</li>
                  <li>Full 3-Subject Package Available at ₹30,000 / yr</li>
                  <li>NCERT Concept Depth & Board Distinction Focus</li>
                  <li>NTSE, PRMO & Junior Olympiad Guidance</li>
                </ul>
              </div>
              <div className="card__footer" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--clr-gray-500)' }}>Evening Batches</span>
                <button className="btn btn--outline btn--sm" onClick={() => setActiveModal('demo')}>Book Trial</button>
              </div>
            </div>
          </div>
        </section>

        {/* Why Choose Future Vision Classes */}
        <section id="why-us" style={{ marginBottom: 'var(--space-16)' }}>
          <div className="section-title-group">
            <div className="section-kicker">The FVC Advantage</div>
            <h2 className="section-title">Why Students Choose Future Vision Classes</h2>
            <p className="section-desc">Our proven 4-pillar methodology turns dedication into measurable academic ranks.</p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 'var(--space-6)' }}>
            <div style={{ background: '#fff', padding: 'var(--space-6)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--clr-gray-100)', boxShadow: 'var(--shadow-sm)' }}>
              <div style={{ fontSize: '2rem', marginBottom: 'var(--space-3)' }}>📚</div>
              <h3 style={{ fontSize: '1.1rem', marginBottom: 'var(--space-2)' }}>Comprehensive Study Material</h3>
              <p style={{ color: 'var(--clr-gray-600)', fontSize: '0.875rem', lineHeight: '1.6' }}>
                Chapter-wise theory booklets, graded problem sets (Level 1, 2, and Advanced), and quick summary mind-maps.
              </p>
            </div>

            <div style={{ background: '#fff', padding: 'var(--space-6)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--clr-gray-100)', boxShadow: 'var(--shadow-sm)' }}>
              <div style={{ fontSize: '2rem', marginBottom: 'var(--space-3)' }}>📝</div>
              <h3 style={{ fontSize: '1.1rem', marginBottom: 'var(--space-2)' }}>Daily Practice Problem (DPP)</h3>
              <p style={{ color: 'var(--clr-gray-600)', fontSize: '0.875rem', lineHeight: '1.6' }}>
                Every single lecture is paired with a focused problem sheet to solidify concepts before moving to the next topic.
              </p>
            </div>

            <div style={{ background: '#fff', padding: 'var(--space-6)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--clr-gray-100)', boxShadow: 'var(--shadow-sm)' }}>
              <div style={{ fontSize: '2rem', marginBottom: 'var(--space-3)' }}>📊</div>
              <h3 style={{ fontSize: '1.1rem', marginBottom: 'var(--space-2)' }}>All-India Mock Test Series</h3>
              <p style={{ color: 'var(--clr-gray-600)', fontSize: '0.875rem', lineHeight: '1.6' }}>
                Simulated CBT testing matching actual JEE & NEET difficulty, detailed error analysis reports, and percentiles.
              </p>
            </div>

            <div style={{ background: '#fff', padding: 'var(--space-6)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--clr-gray-100)', boxShadow: 'var(--shadow-sm)' }}>
              <div style={{ fontSize: '2rem', marginBottom: 'var(--space-3)' }}>👨‍🏫</div>
              <h3 style={{ fontSize: '1.1rem', marginBottom: 'var(--space-2)' }}>1-on-1 Doubt Clinics</h3>
              <p style={{ color: 'var(--clr-gray-600)', fontSize: '0.875rem', lineHeight: '1.6' }}>
                Dedicated faculty hours after every lecture so no student goes home with unanswered doubts or confusion.
              </p>
            </div>
          </div>
        </section>

        {/* Timings & Campus Location */}
        <section id="timings" style={{ marginBottom: 'var(--space-16)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-6)' }}>
            {/* Batch Schedules Card */}
            <div style={{ background: '#fff', padding: 'var(--space-8)', borderRadius: 'var(--radius-xl)', border: '1px solid var(--clr-gray-200)', boxShadow: 'var(--shadow-md)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
                <span style={{ fontSize: '1.75rem' }}>⏰</span>
                <h3 style={{ margin: 0, fontSize: '1.25rem' }}>Structured Batch Timings</h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                <div style={{ padding: 'var(--space-3)', background: 'var(--clr-gray-50)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontWeight: 700, color: 'var(--clr-blue)' }}>🌅 Morning Batches (8:00 AM – 12:00 PM)</div>
                  <div style={{ fontSize: '0.8125rem', color: 'var(--clr-gray-600)', marginTop: '4px' }}>
                    Dedicated 1-Year Dropper / Repeater intensive batches and full-time competitive aspirants.
                  </div>
                </div>
                <div style={{ padding: 'var(--space-3)', background: 'var(--clr-gray-50)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontWeight: 700, color: 'var(--clr-navy)' }}>🌇 Evening Batches (4:00 PM – 7:30 PM)</div>
                  <div style={{ fontSize: '0.8125rem', color: 'var(--clr-gray-600)', marginTop: '4px' }}>
                    Designed for school-going students in Classes 9, 10, 11, and 12 with convenient transit hours.
                  </div>
                </div>
                <div style={{ padding: 'var(--space-3)', background: 'var(--clr-gray-50)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontWeight: 700, color: 'var(--clr-accent)' }}>📅 Weekend Sessions (9:00 AM – 2:00 PM)</div>
                  <div style={{ fontSize: '0.8125rem', color: 'var(--clr-gray-600)', marginTop: '4px' }}>
                    All-India Mock Test Series, personal doubt clinics, and booster lectures.
                  </div>
                </div>
              </div>
            </div>

            {/* Campus Card */}
            <div id="campus" style={{ background: '#fff', padding: 'var(--space-8)', borderRadius: 'var(--radius-xl)', border: '1px solid var(--clr-gray-200)', boxShadow: 'var(--shadow-md)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
                <span style={{ fontSize: '1.75rem' }}>📍</span>
                <h3 style={{ margin: 0, fontSize: '1.25rem' }}>Sonipat Campus & Admissions Desk</h3>
              </div>
              <p style={{ color: 'var(--clr-gray-700)', fontSize: '0.9375rem', lineHeight: '1.6', marginBottom: 'var(--space-4)' }}>
                <strong>SCO No. 21–22, Rangoli Green, Sector 16, Sonipat, Haryana 131001</strong><br />
                <span style={{ fontSize: '0.8125rem', color: 'var(--clr-gray-500)' }}>(Easily accessible near Sector 15 and main arterial roads).</span>
              </p>
              <div style={{ padding: 'var(--space-4)', background: 'var(--clr-blue-pale)', borderRadius: 'var(--radius-md)', marginBottom: 'var(--space-4)' }}>
                <div style={{ fontWeight: 700, fontSize: '0.875rem', color: 'var(--clr-navy)' }}>🕒 Visiting & Counseling Hours:</div>
                <div style={{ fontSize: '0.8125rem', color: 'var(--clr-gray-700)', marginTop: '4px' }}>
                  • Monday – Saturday: <strong>9:00 AM – 7:00 PM</strong><br />
                  • Sunday: <strong>10:00 AM – 2:00 PM</strong>
                </div>
              </div>
              <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
                <button className="btn btn--primary btn--sm" onClick={() => setActiveModal('demo')}>
                  Book Campus Visit
                </button>
                <button className="btn btn--outline btn--sm" onClick={() => setActiveModal('enquiry')}>
                  Request Callback
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Student Support Banner */}
        <section style={{
          background: 'linear-gradient(135deg, var(--clr-navy) 0%, var(--clr-navy-dark) 100%)',
          color: '#fff',
          borderRadius: 'var(--radius-xl)',
          padding: 'var(--space-8)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 'var(--space-6)',
          marginBottom: 'var(--space-12)'
        }}>
          <div>
            <h3 style={{ color: '#fff', margin: '0 0 var(--space-2)' }}>Student & Parent Grievance Desk</h3>
            <p style={{ color: 'rgba(255,255,255,0.8)', margin: 0, fontSize: '0.9375rem', maxWidth: '580px' }}>
              Enrolled students and parents can register issues or track the status of existing tickets in real-time.
            </p>
          </div>
          <button className="btn btn--secondary" onClick={() => setActiveModal('complaint')}>
            🎫 Track / File Support Ticket
          </button>
        </section>
      </main>

      {/* Modal Dialogs */}
      {activeModal && (
        <div className="modal-overlay" onClick={() => setActiveModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-4)' }}>
              <h3 style={{ margin: 0 }}>
                {activeModal === 'enquiry' && 'Admission Enquiry'}
                {activeModal === 'demo' && 'Book a Free Demo Class'}
                {activeModal === 'complaint' && 'Student Grievance & Support'}
              </h3>
              <button
                className="btn btn--sm"
                style={{ background: 'var(--clr-gray-100)', border: 'none', borderRadius: '50%', width: '32px', height: '32px', padding: 0 }}
                onClick={() => setActiveModal(null)}
              >
                ✕
              </button>
            </div>

            {activeModal === 'enquiry' && <EnquiryForm />}
            {activeModal === 'demo' && <DemoRequestForm />}
            {activeModal === 'complaint' && <ComplaintForm />}
          </div>
        </div>
      )}

      {/* Persistent Floating AI Chatbot Widget */}
      <ChatWidget
        onOpenEnquiry={() => setActiveModal('enquiry')}
        onOpenDemo={() => setActiveModal('demo')}
        onOpenComplaint={() => setActiveModal('complaint')}
      />

      {/* Professional Footer */}
      <footer style={{ background: 'var(--clr-navy-dark)', color: 'rgba(255,255,255,0.7)', padding: 'var(--space-12) 0 var(--space-6)', fontSize: '0.875rem' }}>
        <div className="container">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 'var(--space-8)', marginBottom: 'var(--space-8)' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: 'var(--space-3)' }}>
                <span style={{ fontSize: '1.25rem' }}>🎓</span>
                <span style={{ color: '#fff', fontWeight: 700, fontSize: '1.0625rem' }}>Future Vision Classes</span>
              </div>
              <p style={{ color: 'rgba(255,255,255,0.7)', lineHeight: '1.6', fontSize: '0.8125rem' }}>
                Sonipat's premier academic destination for IIT-JEE, NEET-UG, and Classes 9th to 12th Board excellence.
              </p>
            </div>
            <div>
              <h4 style={{ color: '#fff', fontSize: '0.9375rem', marginBottom: 'var(--space-3)' }}>Programs</h4>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.8125rem' }}>
                <li><a href="#programs" style={{ color: 'rgba(255,255,255,0.7)', textDecoration: 'none' }}>2-Year Integrated (10th Passed)</a></li>
                <li><a href="#programs" style={{ color: 'rgba(255,255,255,0.7)', textDecoration: 'none' }}>1-Year Intensive JEE & NEET</a></li>
                <li><a href="#programs" style={{ color: 'rgba(255,255,255,0.7)', textDecoration: 'none' }}>Classes 11 & 12 (PCM / PCB)</a></li>
                <li><a href="#programs" style={{ color: 'rgba(255,255,255,0.7)', textDecoration: 'none' }}>Classes 9 & 10 (Science, Maths, English)</a></li>
              </ul>
            </div>
            <div>
              <h4 style={{ color: '#fff', fontSize: '0.9375rem', marginBottom: 'var(--space-3)' }}>Campus Address</h4>
              <p style={{ color: 'rgba(255,255,255,0.7)', lineHeight: '1.6', fontSize: '0.8125rem' }}>
                SCO No. 21–22, Rangoli Green,<br />
                Sector 16, Sonipat, Haryana 131001<br />
                Near Sector 15 Main Road
              </p>
            </div>
            <div>
              <h4 style={{ color: '#fff', fontSize: '0.9375rem', marginBottom: 'var(--space-3)' }}>Admissions & Office</h4>
              <p style={{ color: 'rgba(255,255,255,0.7)', lineHeight: '1.6', fontSize: '0.8125rem' }}>
                Mon – Sat: 9:00 AM – 7:00 PM<br />
                Sunday: 10:00 AM – 2:00 PM<br />
                Walk-ins & 1-on-1 counseling welcome
              </p>
            </div>
          </div>
          <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: 'var(--space-6)', textAlign: 'center', fontSize: '0.8125rem', color: 'rgba(255,255,255,0.5)' }}>
            <p style={{ margin: 0 }}>© 2026 Future Vision Classes. All Rights Reserved. • Designed for Academic & Student Excellence.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};
