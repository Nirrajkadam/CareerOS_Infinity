export type ApplicationRecord = {
  id: string;
  company?: string;
  role?: string;
  status?: string;
  ats_score?: number | null;
  created_at?: string | null;
  submitted_at?: string | null;
  applied_at?: string | null;
};

const terminalStatuses = new Set(['REJECTED', 'WITHDRAWN', 'CANCELLED', 'CANCELED', 'CLOSED', 'SKIPPED']);
const submittedStatuses = new Set(['SUBMITTED', 'SUBMITTED_VERIFIED', 'SUBMISSION_VERIFIED']);
export const isVerifiedSubmission = (status?: string) => status === 'SUBMITTED_VERIFIED' || status === 'SUBMISSION_VERIFIED';

export function summarizeApplications(applications: ApplicationRecord[], now = Date.now()) {
  const scores = applications.map(app => app.ats_score).filter(
    (score): score is number => typeof score === 'number' && Number.isFinite(score) && score >= 0 && score <= 100,
  );
  const weekStart = now - 7 * 24 * 60 * 60 * 1000;
  return {
    activeApplications: applications.filter(app => app.status && !terminalStatuses.has(app.status)).length,
    avgAtsMatch: scores.length ? Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length) : null,
    appliesThisWeek: applications.filter(app => {
      // Creation of a draft is not evidence of submission.
      const timestamp = app.submitted_at || (submittedStatuses.has(app.status || '') ? app.applied_at : null);
      if (!timestamp) return false;
      const submitted = Date.parse(timestamp);
      return Number.isFinite(submitted) && submitted >= weekStart && submitted <= now;
    }).length,
  };
}

export function recentApplications(applications: ApplicationRecord[]) {
  const time = (app: ApplicationRecord) => Date.parse(app.submitted_at || app.applied_at || app.created_at || '') || 0;
  return [...applications].sort((a, b) => time(b) - time(a)).slice(0, 10);
}
