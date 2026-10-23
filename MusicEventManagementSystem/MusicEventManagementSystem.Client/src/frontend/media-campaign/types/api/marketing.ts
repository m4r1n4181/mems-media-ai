export interface Brand {
  brandId: number;
  handle: string;
  displayName: string;
  niche: string | null;
  followers: number;
  typicalPartnerFollowers: number | null;
  campaignCount: number;
}

export type InfluencerStatus = 'Suggested' | 'Selected' | 'Contacted' | 'Accepted' | 'Declined' | 'Dismissed';

export interface Reason {
  code: string;
  text: string;
}

export interface OutreachEmail {
  outreachEmailId: number;
  toEmail: string;
  subject: string;
  body: string;
  provider: string;
  checksPassed: boolean;
  editedByUser: boolean;
  sentAt: string;
}

export interface CampaignInfluencer {
  campaignCreatorId: number;
  campaignId: number;
  creatorId: string;
  status: InfluencerStatus;
  rank: number;
  score: number;
  reasons: Reason[];
  modelVersion: string;
  email: string;
  followers: number;
  sizeTier: string | null;
  niche: string | null;
  suggestedAt: string;
  contactedAt: string | null;
  respondedAt: string | null;
  note: string | null;
  lastEmail: OutreachEmail | null;
}

export interface CreatorProfile {
  creatorId: string;
  followers: number;
  sizeTier: string | null;
  niche: string | null;
  paidBrandsTotal: number;
  paidBrands180d: number;
  medianRelEngagement: number | null;
  lastPost: string | null;
  recentBrands: string[];
}

export interface EmailDraft {
  subject: string;
  body: string;
  provider: string;
  model: string | null;
  checksPassed: boolean;
  issues: string[];
  fallbackReason: string | null;
  toEmail: string;
}

export interface AiStatus {
  serviceAvailable: boolean;
  modelVersion: string | null;
  llmProvider: string | null;
  llmModel: string | null;
  llmAvailable: boolean;
  message: string | null;
}

export interface SuggestRequest {
  count: number;
  minFollowers?: number;
  maxFollowers?: number;
  niche?: string;
}

export interface Sender {
  name: string;
  email?: string;
}
