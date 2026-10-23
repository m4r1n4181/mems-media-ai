export interface CreateCampaignForm {
  brandId: number;
  name: string;
  brief?: string;
  startDate: string; // ISO date string
  endDate: string; // ISO date string
  totalBudget: number;
  adIds?: number[];
}

export interface UpdateCampaignForm {
  brandId?: number;
  name?: string;
  brief?: string;
  startDate?: string; // ISO date string
  endDate?: string; // ISO date string
  totalBudget?: number;
  adIds?: number[];
}
