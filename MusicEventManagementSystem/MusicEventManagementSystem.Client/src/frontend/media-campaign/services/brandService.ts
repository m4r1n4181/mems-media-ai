import type { Brand, CreateBrandRequest, KnownBrand } from '../types/api/marketing';
import { request } from './influencerService';

const API_BASE_URL = 'http://localhost:5255/api';

export class BrandService {
  private static readonly BASE_URL = `${API_BASE_URL}/Brands`;

  // GET: api/Brands
  static async getAllBrands(): Promise<Brand[]> {
    return request(this.BASE_URL);
  }

  // GET: api/Brands/known (brands the recommender knows, for "similar brands")
  static async getKnownBrands(): Promise<KnownBrand[]> {
    return request(`${this.BASE_URL}/known`);
  }

  // POST: api/Brands
  static async createBrand(data: CreateBrandRequest): Promise<Brand> {
    return request(this.BASE_URL, { method: 'POST', body: JSON.stringify(data) });
  }
}
