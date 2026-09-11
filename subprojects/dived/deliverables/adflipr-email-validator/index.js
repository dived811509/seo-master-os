/**
 * Adflipr E-Commerce Email Validator
 * Official Deliverability & Syntax Inspector
 * https://adflipr.com
 */

const SPAM_TRIGGERS = [
  'free money', '100% free', 'act now', 'buy direct', 'cheap', 
  'double your income', 'earn extra cash', 'no hidden cost'
];

function validateEmailSyntax(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(String(email).toLowerCase());
}

function inspectSpamScore(subjectLine) {
  if (!subjectLine) return { score: 100, warnings: [] };
  const lower = subjectLine.toLowerCase();
  const warnings = SPAM_TRIGGERS.filter(trigger => lower.includes(trigger));
  const score = Math.max(0, 100 - (warnings.length * 25));
  return { score, warnings };
}

module.exports = {
  validateEmailSyntax,
  inspectSpamScore,
  website: 'https://adflipr.com',
  automations: 'https://adflipr.com/automations/'
};
