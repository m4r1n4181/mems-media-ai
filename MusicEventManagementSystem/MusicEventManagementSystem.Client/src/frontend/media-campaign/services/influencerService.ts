import type {
  AiStatus,
  CampaignInfluencer,
  CreatorProfile,
  EmailDraft,
  Sender,
  SuggestRequest,
} from '../types/api/marketing';

const API_BASE_URL = 'http://localhost:5255/api';

// The API answers errors with { message }, so the UI can show what actually went wrong.
export async function request<T>(url: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    });
  } catch {
    throw new Error('Cannot reach the API. Check that it is running on port 5255.');
  }
  if (!response.ok) {
    let message = `Request failed (HTTP ${response.status}).`;
    try {
      const data = await response.json();
      if (data?.message) message = data.message;
      else if (data?.errors) message = Object.values(data.errors).flat().join(' ');
    } catch {
      // keep the generic message
    }
    throw new Error(message);
  }
  return await response.json();
}

export class InfluencerService {
  static getForCampaign(campaignId: number): Promise<CampaignInfluencer[]> {
    return request(`${API_BASE_URL}/campaigns/${campaignId}/influencers`);
  }

  static suggest(campaignId: number, body: SuggestRequest): Promise<CampaignInfluencer[]> {
    return request(`${API_BASE_URL}/campaigns/${campaignId}/influencers/suggest`, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  static changeStatus(id: number, action: 'select' | 'unselect' | 'dismiss'): Promise<CampaignInfluencer> {
    return request(`${API_BASE_URL}/campaign-influencers/${id}/${action}`, { method: 'POST' });
  }

  static draftEmail(id: number, sender: Sender): Promise<EmailDraft> {
    return request(`${API_BASE_URL}/campaign-influencers/${id}/draft-email`, {
      method: 'POST',
      body: JSON.stringify(sender),
    });
  }

  static sendEmail(
    id: number,
    body: {
      subject: string;
      body: string;
      provider: string;
      model: string | null;
      checksPassed: boolean;
      editedByUser: boolean;
      sender: Sender;
      sentByUserId?: string;
    }
  ): Promise<CampaignInfluencer> {
    return request(`${API_BASE_URL}/campaign-influencers/${id}/send-email`, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  static recordResponse(id: number, accepted: boolean, note?: string): Promise<CampaignInfluencer> {
    return request(`${API_BASE_URL}/campaign-influencers/${id}/response`, {
      method: 'POST',
      body: JSON.stringify({ accepted, note }),
    });
  }

  static getCreator(creatorId: string): Promise<CreatorProfile> {
    return request(`${API_BASE_URL}/creators/${encodeURIComponent(creatorId)}`);
  }

  static getAiStatus(): Promise<AiStatus> {
    return request(`${API_BASE_URL}/ai/status`);
  }
}
