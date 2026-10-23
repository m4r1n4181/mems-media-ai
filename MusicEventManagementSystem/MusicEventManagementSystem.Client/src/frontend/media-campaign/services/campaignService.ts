import type { Campaign } from '../types/api/campaign';
import type { CreateCampaignForm, UpdateCampaignForm } from '../types/form/campaign';

const API_BASE_URL = 'http://localhost:5255/api'; // Promeni na svoj API URL

export class CampaignService {
  private static readonly BASE_URL = `${API_BASE_URL}/Campaign`;

  // GET: api/Campaign
  static async getAllCampaigns(): Promise<Campaign[]> {
    try {
      const response = await fetch(this.BASE_URL);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching campaigns:', error);
      throw new Error('Failed to fetch campaigns');
    }
  }

  // GET: api/Campaign/{id}
  static async getCampaignById(id: number): Promise<Campaign> {
    try {
      const response = await fetch(`${this.BASE_URL}/${id}`);
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Campaign with ID ${id} not found`);
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Error fetching campaign ${id}:`, error);
      throw error;
    }
  }

  // POST: api/Campaign
  static async createCampaign(createForm: CreateCampaignForm): Promise<Campaign> {
    try {
      const response = await fetch(this.BASE_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(createForm),
      });

      if (!response.ok) {
        if (response.status === 400) {
          const errorData = await response.json();
          throw new Error(`Validation error: ${JSON.stringify(errorData)}`);
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating campaign:', error);
      throw new Error('Failed to create campaign');
    }
  }

  // PUT: api/Campaign/{id}
  static async updateCampaign(id: number, updateForm: UpdateCampaignForm): Promise<Campaign> {
    try {
      const response = await fetch(`${this.BASE_URL}/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateForm),
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Campaign with ID ${id} not found`);
        }
        if (response.status === 400) {
          const errorData = await response.json();
          throw new Error(`Validation error: ${JSON.stringify(errorData)}`);
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Error updating campaign ${id}:`, error);
      throw error;
    }
  }

  // DELETE: api/Campaign/{id}
  static async deleteCampaign(id: number): Promise<void> {
    try {
      const response = await fetch(`${this.BASE_URL}/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Campaign with ID ${id} not found`);
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error(`Error deleting campaign ${id}:`, error);
      throw error;
    }
  }

  // GET: api/Campaign/brandId/{brandId}
  static async getByBrandId(brandId: number): Promise<Campaign[]> {
    try {
      const response = await fetch(`${this.BASE_URL}/brandId/${brandId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching campaigns by brand ID:', error);
      throw new Error('Failed to fetch campaigns by brand ID');
    }
  }

  // GET: api/Campaign/name/{name}
  static async getByName(name: string): Promise<Campaign[]> {
    try {
      const response = await fetch(`${this.BASE_URL}/name/${encodeURIComponent(name)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching campaigns by name:', error);
      throw new Error('Failed to fetch campaigns by name');
    }
  }

  // GET: api/Campaign/startDate/{startDate}
  static async getByStartDate(startDate: Date): Promise<Campaign[]> {
    try {
      const response = await fetch(`${this.BASE_URL}/startDate/${startDate.toISOString()}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching campaigns by start date:', error);
      throw new Error('Failed to fetch campaigns by start date');
    }
  }

  // GET: api/Campaign/endDate/{endDate}
  static async getByEndDate(endDate: Date): Promise<Campaign[]> {
    try {
      const response = await fetch(`${this.BASE_URL}/endDate/${endDate.toISOString()}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching campaigns by end date:', error);
      throw new Error('Failed to fetch campaigns by end date');
    }
  }

  // GET: api/Campaign/totalBudget/{totalBudget}
  static async getByTotalBudget(totalBudget: number): Promise<Campaign[]> {
    try {
      const response = await fetch(`${this.BASE_URL}/totalBudget/${totalBudget}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching campaigns by total budget:', error);
      throw new Error('Failed to fetch campaigns by total budget');
    }
  }
}