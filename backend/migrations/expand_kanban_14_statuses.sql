-- ============================================================
-- Expand Job Tracker Kanban to 14 Statuses
-- Run in: Supabase Dashboard -> SQL Editor -> New Query -> Run
-- ============================================================

-- Drop existing CHECK constraint and replace with expanded one
ALTER TABLE job_applications DROP CONSTRAINT IF EXISTS job_applications_status_check;

ALTER TABLE job_applications ADD CONSTRAINT job_applications_status_check
    CHECK (status IN (
        'wishlist',
        'networking',
        'saved',
        'applied',
        'phone_screen',
        'assessment',
        'interview_scheduled',
        'interview_completed',
        'reference_check',
        'offer_received',
        'negotiating',
        'job_won',
        'rejected',
        'withdrawn'
    ));
