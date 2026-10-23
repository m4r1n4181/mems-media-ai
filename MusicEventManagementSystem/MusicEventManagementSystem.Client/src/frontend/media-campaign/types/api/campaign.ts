export interface Campaign {
  campaignId: number;
  brandId: number | null;
  brandHandle: string | null;
  name: string;
  brief: string | null;
  startDate: string; // ISO date string
  endDate: string; // ISO date string
  totalBudget: number;
  adIds?: number[];
}
