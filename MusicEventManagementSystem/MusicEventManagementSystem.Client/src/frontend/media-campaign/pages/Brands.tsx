import { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { Megaphone, Search, Tag, Users } from 'lucide-react';
import { BrandService } from '../services/brandService';
import type { Brand } from '../types/api/marketing';

const formatFollowers = (n: number) =>
  n >= 1_000_000 ? `${(n / 1_000_000).toFixed(1)}M` : n >= 1_000 ? `${(n / 1_000).toFixed(1)}K` : `${n}`;

const Brands = () => {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    BrandService.getAllBrands()
      .then(setBrands)
      .catch((error) => toast.error(error instanceof Error ? error.message : 'Could not load brands.'))
      .finally(() => setLoading(false));
  }, []);

  const q = searchTerm.toLowerCase();
  const filtered = brands.filter((b) => b.handle.includes(q) || (b.niche ?? '').toLowerCase().includes(q));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Brands</h1>
        <p className="text-neutral-400">The client brands your team runs campaigns for</p>
      </div>

      <div className="flex items-center gap-4 p-4 bg-neutral-800/50 backdrop-blur-sm border border-neutral-700 rounded-2xl">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-neutral-400 w-5 h-5" />
          <input
            type="text"
            aria-label="Search brands"
            placeholder="Search by handle or niche"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-neutral-700/50 border border-neutral-600 rounded-xl text-white placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent"
          />
        </div>
      </div>

      <div className="bg-neutral-800/50 backdrop-blur-sm border border-neutral-700 rounded-2xl overflow-hidden">
        {filtered.length > 0 ? (
          <div className="divide-y divide-neutral-700">
            {filtered.map((b) => (
              <div key={b.brandId} className="p-6 hover:bg-neutral-700/30 transition-colors">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-purple-400/20 rounded-xl">
                    <Tag className="w-6 h-6 text-purple-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-1">@{b.handle}</h3>
                    <div className="flex flex-wrap items-center gap-4 text-sm text-neutral-400">
                      {b.niche && <span>{b.niche}</span>}
                      <span className="flex items-center gap-1">
                        <Users className="w-4 h-4" />
                        {formatFollowers(b.followers)} followers
                      </span>
                      {b.typicalPartnerFollowers && (
                        <span>usually works with ~{formatFollowers(b.typicalPartnerFollowers)} creators</span>
                      )}
                      <span className="flex items-center gap-1">
                        <Megaphone className="w-4 h-4" />
                        {b.campaignCount} {b.campaignCount === 1 ? 'campaign' : 'campaigns'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center">
            <Tag className="w-16 h-16 text-neutral-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">No brands found</h3>
            <p className="text-neutral-400">
              {brands.length === 0
                ? 'Client brands are loaded when the API starts. Check the API log for the seed file.'
                : 'Try another search.'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Brands;
