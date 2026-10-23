import type { Brand } from '../types/api/marketing';

const API_BASE_URL = 'http://localhost:5255/api';

export class BrandService {
  private static readonly BASE_URL = `${API_BASE_URL}/Brands`;

  // GET: api/Brands
  static async getAllBrands(): Promise<Brand[]> {
    const response = await fetch(this.BASE_URL);
    if (!response.ok) {
      throw new Error(`Could not load brands (HTTP ${response.status}).`);
    }
    return await response.json();
  }
}
