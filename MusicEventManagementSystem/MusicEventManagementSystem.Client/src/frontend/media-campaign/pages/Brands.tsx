import { useEffect, useMemo, useState } from 'react';
import { toast } from 'react-toastify';
import { Check, Megaphone, Plus, Search, Sparkles, Tag, Users, X } from 'lucide-react';
import { BrandService } from '../services/brandService';
import type { Brand, KnownBrand } from '../types/api/marketing';

const formatFollowers = (n: number) =>
  n >= 1_000_000 ? `${(n / 1_000_000).toFixed(1)}M` : n >= 1_000 ? `${(n / 1_000).toFixed(1)}K` : `${n}`;

const normalizeHandle = (raw: string) => raw.trim().replace(/^@/, '').toLowerCase();
const HANDLE_PATTERN = /^[a-z0-9._]{1,30}$/;
const MAX_SIMILAR = 5;

// Typical creator size a brand works with; used to describe the brand and as a default filter later.
const PARTNER_SIZES = [
  { label: 'Not sure', value: '' },
  { label: 'Nano (under 10K followers)', value: '5000' },
  { label: 'Micro (10K–50K)', value: '25000' },
  { label: 'Mid (50K–250K)', value: '100000' },
  { label: 'Macro (250K+)', value: '400000' },
];

const inputClass =
  'w-full p-3 bg-neutral-700 border border-neutral-600 rounded-xl text-white placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent';

interface AddBrandModalProps {
  known: KnownBrand[];
  existing: Brand[];
  onClose: () => void;
  onCreated: (brand: Brand) => void;
}

const AddBrandModal = ({ known, existing, onClose, onCreated }: AddBrandModalProps) => {
  const [handle, setHandle] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [niche, setNiche] = useState('');
  const [partnerSize, setPartnerSize] = useState('');
  const [similar, setSimilar] = useState<string[]>([]);
  const [similarQuery, setSimilarQuery] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const h = normalizeHandle(handle);
  const validHandle = HANDLE_PATTERN.test(h);
  const knownMatch = validHandle ? known.find((k) => k.handle === h) : undefined;
  const alreadyClient = validHandle && existing.some((b) => b.handle === h);
  const niches = useMemo(
    () => Array.from(new Set(known.map((k) => k.niche).filter((n): n is string => !!n))).sort(),
    [known],
  );

  // Similar-brand choices: search by handle; brands from the chosen niche first.
  const choices = useMemo(() => {
    const q = normalizeHandle(similarQuery);
    return known
      .filter((k) => k.handle !== h && !similar.includes(k.handle) && (!q || k.handle.includes(q)))
      .sort((a, b) => Number(b.niche === niche) - Number(a.niche === niche) || b.followers - a.followers)
      .slice(0, 8);
  }, [known, similarQuery, similar, h, niche]);

  const needsSimilar = validHandle && !knownMatch;
  const canSave = validHandle && !alreadyClient && (!needsSimilar || similar.length > 0) && !saving;

  const save = async () => {
    setSaving(true);
    setError(null);
    try {
      const brand = await BrandService.createBrand({
        handle: h,
        displayName: displayName.trim() || undefined,
        niche: niche || undefined,
        typicalPartnerFollowers: partnerSize ? Number(partnerSize) : undefined,
        similarBrands: similar,
      });
      onCreated(brand);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not add the brand.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div role="dialog" aria-modal="true" aria-labelledby="add-brand-title"
           className="bg-neutral-800 border border-neutral-700 rounded-2xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 id="add-brand-title" className="text-xl font-semibold text-white">Add brand</h2>
          <button onClick={onClose} aria-label="Close" className="p-2 text-neutral-400 hover:text-white rounded-lg transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label htmlFor="brand-handle" className="block text-sm text-neutral-300 mb-2">Instagram handle *</label>
            <input id="brand-handle" type="text" placeholder="@brandname" value={handle} autoFocus
                   onChange={(e) => setHandle(e.target.value)} className={inputClass} />
            {handle && !validHandle && (
              <p className="mt-2 text-sm text-red-400">Use letters, numbers, dots and underscores (max 30).</p>
            )}
            {alreadyClient && <p className="mt-2 text-sm text-red-400">@{h} is already a client.</p>}
            {validHandle && !alreadyClient && knownMatch && (
              <p className="mt-2 text-sm text-green-400 flex items-start gap-2">
                <Check className="w-4 h-4 mt-0.5 shrink-0" />
                The recommender knows @{h} ({knownMatch.niche ?? 'no niche'}, {formatFollowers(knownMatch.followers)} followers)
                and will use its own history.
              </p>
            )}
            {needsSimilar && !alreadyClient && (
              <p className="mt-2 text-sm text-neutral-300 flex items-start gap-2">
                <Sparkles className="w-4 h-4 mt-0.5 shrink-0 text-purple-400" />
                New to the recommender. Choose up to five similar brands below (more is better) and the niche:
                their best creators are combined into suggestions for @{h}.
              </p>
            )}
          </div>

          <div>
            <label htmlFor="brand-name" className="block text-sm text-neutral-300 mb-2">Display name</label>
            <input id="brand-name" type="text" placeholder={h || 'Brand name'} value={displayName}
                   onChange={(e) => setDisplayName(e.target.value)} className={inputClass} />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label htmlFor="brand-niche" className="block text-sm text-neutral-300 mb-2">Niche</label>
              <select id="brand-niche" value={niche} onChange={(e) => setNiche(e.target.value)} className={inputClass}>
                <option value="">{knownMatch?.niche ? `From the recommender (${knownMatch.niche})` : 'Not sure'}</option>
                {niches.map((n) => <option key={n} value={n}>{n}</option>)}
              </select>
            </div>
            <div>
              <label htmlFor="brand-size" className="block text-sm text-neutral-300 mb-2">Usually works with</label>
              <select id="brand-size" value={partnerSize} onChange={(e) => setPartnerSize(e.target.value)} className={inputClass}>
                {PARTNER_SIZES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="similar-search" className="block text-sm text-neutral-300 mb-2">
              Similar brands {needsSimilar ? '*' : '(optional)'} <span className="text-neutral-500">· up to {MAX_SIMILAR}</span>
            </label>
            {similar.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-2">
                {similar.map((s) => (
                  <span key={s} className="flex items-center gap-1 px-3 py-1 bg-purple-500/20 text-purple-200 rounded-lg text-sm">
                    @{s}
                    <button onClick={() => setSimilar(similar.filter((x) => x !== s))} aria-label={`Remove @${s}`}
                            className="text-purple-300 hover:text-white">
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </span>
                ))}
              </div>
            )}
            {similar.length < MAX_SIMILAR && (
              <>
                <input id="similar-search" type="text" placeholder="Search brands the recommender knows"
                       value={similarQuery} onChange={(e) => setSimilarQuery(e.target.value)} className={inputClass} />
                <ul className="mt-2 max-h-56 overflow-y-auto divide-y divide-neutral-700 border border-neutral-700 rounded-xl">
                  {choices.map((k) => (
                    <li key={k.handle}>
                      <button
                        onClick={() => { setSimilar([...similar, k.handle]); setSimilarQuery(''); }}
                        className="w-full flex items-center justify-between gap-3 px-3 py-2 text-left hover:bg-neutral-700/60"
                      >
                        <span className="text-white text-sm">@{k.handle}</span>
                        <span className="text-xs text-neutral-400 text-right">
                          {k.niche ?? '—'} · {formatFollowers(k.followers)}
                        </span>
                      </button>
                    </li>
                  ))}
                  {choices.length === 0 && <li className="px-3 py-2 text-sm text-neutral-400">No matching brands.</li>}
                </ul>
              </>
            )}
          </div>

          {error && <p role="alert" className="text-sm text-red-400">{error}</p>}
        </div>

        <div className="flex justify-end gap-3 mt-6">
          <button onClick={onClose} className="px-4 py-2 text-neutral-300 hover:text-white rounded-xl transition-colors">Cancel</button>
          <button onClick={save} disabled={!canSave}
                  className="flex items-center gap-2 px-5 py-2 bg-purple-500 hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl font-medium transition-colors">
            <Plus className="w-4 h-4" /> {saving ? 'Adding…' : 'Add brand'}
          </button>
        </div>
      </div>
    </div>
  );
};

const Brands = () => {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [known, setKnown] = useState<KnownBrand[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAdd, setShowAdd] = useState(false);

  useEffect(() => {
    BrandService.getAllBrands()
      .then(setBrands)
      .catch((error) => toast.error(error instanceof Error ? error.message : 'Could not load brands.'))
      .finally(() => setLoading(false));
  }, []);

  const openAdd = async () => {
    if (known === null) {
      try {
        setKnown(await BrandService.getKnownBrands());
      } catch (error) {
        toast.error(error instanceof Error ? error.message : 'Could not load the brands the recommender knows.');
        return;
      }
    }
    setShowAdd(true);
  };

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
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Brands</h1>
          <p className="text-neutral-400">The client brands your team runs campaigns for</p>
        </div>
        <button onClick={openAdd}
                className="flex items-center gap-2 px-6 py-3 bg-purple-500 hover:bg-purple-600 text-white rounded-xl transition-all duration-200 font-medium">
          <Plus className="w-5 h-5" />
          Add brand
        </button>
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
                      {b.followers > 0 && (
                        <span className="flex items-center gap-1">
                          <Users className="w-4 h-4" />
                          {formatFollowers(b.followers)} followers
                        </span>
                      )}
                      {b.typicalPartnerFollowers && (
                        <span>usually works with ~{formatFollowers(b.typicalPartnerFollowers)} creators</span>
                      )}
                      <span className="flex items-center gap-1">
                        <Megaphone className="w-4 h-4" />
                        {b.campaignCount} {b.campaignCount === 1 ? 'campaign' : 'campaigns'}
                      </span>
                      {!b.knownToModel && (
                        <span className="flex items-center gap-1 text-purple-300">
                          <Sparkles className="w-4 h-4" />
                          New brand · suggestions from {b.similarBrands.map((s) => `@${s}`).join(', ')}
                        </span>
                      )}
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
              {brands.length === 0 ? 'Add your first client brand.' : 'Try another search.'}
            </p>
          </div>
        )}
      </div>

      {showAdd && known && (
        <AddBrandModal
          known={known}
          existing={brands}
          onClose={() => setShowAdd(false)}
          onCreated={(brand) => {
            setBrands([...brands, brand].sort((a, b) => a.displayName.localeCompare(b.displayName)));
            setShowAdd(false);
            toast.success(`@${brand.handle} added.`);
          }}
        />
      )}
    </div>
  );
};

export default Brands;
