import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import {
  AlertTriangle,
  ArrowLeft,
  Calendar,
  Check,
  CheckCircle2,
  DollarSign,
  Mail,
  RefreshCw,
  Send,
  ShieldCheck,
  Sparkles,
  Tag,
  User,
  Users,
  X,
  XCircle,
} from 'lucide-react';
import { CampaignService } from '../services/campaignService';
import { BrandService } from '../services/brandService';
import { InfluencerService } from '../services/influencerService';
import type { Campaign } from '../types/api/campaign';
import type {
  AiStatus,
  Brand,
  CampaignInfluencer,
  CreatorProfile,
  EmailDraft,
  InfluencerStatus,
  Sender,
} from '../types/api/marketing';

const NICHES = [
  'fashion blogging',
  'beauty & makeup',
  'fitness',
  'food',
  'travel',
  'parenting',
  'shoppable fashion (LTK)',
  'home & interior',
];

const SIZES: { label: string; min?: number; max?: number }[] = [
  { label: 'Any size' },
  { label: 'Nano (under 10K)', max: 10_000 },
  { label: 'Micro (10K–50K)', min: 10_000, max: 50_000 },
  { label: 'Mid (50K–250K)', min: 50_000, max: 250_000 },
  { label: 'Macro (250K+)', min: 250_000 },
];

const TABS: { status: InfluencerStatus; label: string }[] = [
  { status: 'Suggested', label: 'Suggested' },
  { status: 'Selected', label: 'Selected' },
  { status: 'Contacted', label: 'Contacted' },
  { status: 'Accepted', label: 'Accepted' },
  { status: 'Declined', label: 'Declined' },
  { status: 'Dismissed', label: 'Dismissed' },
];

const formatFollowers = (n: number) =>
  n >= 1_000_000 ? `${(n / 1_000_000).toFixed(1)}M` : n >= 1_000 ? `${(n / 1_000).toFixed(1)}K` : `${n}`;

const formatDate = (iso: string | null) =>
  iso ? new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : '';

const shortId = (creatorId: string) => creatorId.replace(/^c_/, '').slice(0, 6);

const getSender = (): { sender: Sender; userId?: string } => {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const name = [user.firstName, user.lastName].filter(Boolean).join(' ') || 'Marketing Manager';
    return { sender: { name, email: user.email || undefined }, userId: user.id };
  } catch {
    return { sender: { name: 'Marketing Manager' } };
  }
};

const CampaignInfluencers = () => {
  const { campaignId } = useParams();
  const id = Number(campaignId);
  const navigate = useNavigate();

  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [brand, setBrand] = useState<Brand | null>(null);
  const [influencers, setInfluencers] = useState<CampaignInfluencer[]>([]);
  const [aiStatus, setAiStatus] = useState<AiStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<InfluencerStatus>('Suggested');

  // find creators form
  const [count, setCount] = useState(20);
  const [sizeIndex, setSizeIndex] = useState(0);
  const [niche, setNiche] = useState('');
  const [suggesting, setSuggesting] = useState(false);
  const [busyId, setBusyId] = useState<number | null>(null);

  // e-mail modal
  const [emailFor, setEmailFor] = useState<CampaignInfluencer | null>(null);
  const [draft, setDraft] = useState<EmailDraft | null>(null);
  const [drafting, setDrafting] = useState(false);
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [edited, setEdited] = useState(false);
  const [sending, setSending] = useState(false);

  // other modals
  const [profile, setProfile] = useState<CreatorProfile | null>(null);
  const [viewEmail, setViewEmail] = useState<CampaignInfluencer | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [c, brands, list] = await Promise.all([
          CampaignService.getCampaignById(id),
          BrandService.getAllBrands(),
          InfluencerService.getForCampaign(id),
        ]);
        setCampaign(c);
        setBrand(brands.find((b) => b.brandId === c.brandId) ?? null);
        setInfluencers(list);
        const firstWithItems = TABS.find((t) => list.some((i) => i.status === t.status));
        if (firstWithItems) setActiveTab(firstWithItems.status);
      } catch (error) {
        toast.error(error instanceof Error ? error.message : 'Could not load the campaign.');
      } finally {
        setLoading(false);
      }
      InfluencerService.getAiStatus().then(setAiStatus).catch(() => setAiStatus(null));
    };
    if (Number.isFinite(id)) load();
  }, [id]);

  const counts = useMemo(() => {
    const c: Record<string, number> = {};
    influencers.forEach((i) => (c[i.status] = (c[i.status] || 0) + 1));
    return c;
  }, [influencers]);

  const visible = influencers.filter((i) => i.status === activeTab);

  const replace = (updated: CampaignInfluencer) =>
    setInfluencers((prev) => prev.map((i) => (i.campaignCreatorId === updated.campaignCreatorId ? updated : i)));

  const handleSuggest = async () => {
    setSuggesting(true);
    try {
      const size = SIZES[sizeIndex];
      const list = await InfluencerService.suggest(id, {
        count,
        minFollowers: size.min,
        maxFollowers: size.max,
        niche: niche || undefined,
      });
      setInfluencers(list);
      setActiveTab('Suggested');
      const n = list.filter((i) => i.status === 'Suggested').length;
      if (n === 0) toast.info('No creators match these filters. Try a wider audience size or another niche.');
      else toast.success(`${n} creators suggested for this campaign.`);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Could not get suggestions.');
    } finally {
      setSuggesting(false);
    }
  };

  const handleStatus = async (item: CampaignInfluencer, action: 'select' | 'unselect' | 'dismiss') => {
    setBusyId(item.campaignCreatorId);
    try {
      replace(await InfluencerService.changeStatus(item.campaignCreatorId, action));
      if (action === 'select') toast.success(`Creator ${shortId(item.creatorId)} added to Selected.`);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Could not update the creator.');
    } finally {
      setBusyId(null);
    }
  };

  const loadDraft = async (item: CampaignInfluencer) => {
    setDrafting(true);
    setDraft(null);
    try {
      const d = await InfluencerService.draftEmail(item.campaignCreatorId, getSender().sender);
      setDraft(d);
      setSubject(d.subject);
      setBody(d.body);
      setEdited(false);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Could not write the e-mail.');
      setEmailFor(null);
    } finally {
      setDrafting(false);
    }
  };

  const openEmail = (item: CampaignInfluencer) => {
    setEmailFor(item);
    loadDraft(item);
  };

  const closeEmail = () => {
    if (sending) return;
    setEmailFor(null);
    setDraft(null);
  };

  const handleSend = async () => {
    if (!emailFor || !draft) return;
    setSending(true);
    try {
      const { sender, userId } = getSender();
      const updated = await InfluencerService.sendEmail(emailFor.campaignCreatorId, {
        subject: subject.trim(),
        body: body.trim(),
        provider: draft.provider,
        model: draft.model,
        checksPassed: draft.checksPassed && !edited,
        editedByUser: edited,
        sender,
        sentByUserId: userId,
      });
      replace(updated);
      toast.success(`E-mail sent to ${updated.email}.`);
      setEmailFor(null);
      setDraft(null);
      setActiveTab('Contacted');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'The e-mail could not be sent.');
    } finally {
      setSending(false);
    }
  };

  const handleResponse = async (item: CampaignInfluencer, accepted: boolean) => {
    setBusyId(item.campaignCreatorId);
    try {
      replace(await InfluencerService.recordResponse(item.campaignCreatorId, accepted));
      toast.success(accepted ? 'Marked as accepted.' : 'Marked as declined.');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Could not save the response.');
    } finally {
      setBusyId(null);
    }
  };

  const openProfile = async (item: CampaignInfluencer) => {
    try {
      setProfile(await InfluencerService.getCreator(item.creatorId));
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Could not load the creator profile.');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400"></div>
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="p-12 text-center">
        <h3 className="text-xl font-semibold text-white mb-2">Campaign not found</h3>
        <button
          onClick={() => navigate('/media-campaign/campaigns')}
          className="px-6 py-3 bg-purple-500 hover:bg-purple-600 text-white rounded-xl transition-colors"
        >
          Back to campaigns
        </button>
      </div>
    );
  }

  const aiProblem =
    aiStatus === null
      ? 'The recommendation service status is unknown.'
      : !aiStatus.serviceAvailable
        ? aiStatus.message || 'The recommendation service is not running.'
        : !aiStatus.llmAvailable
          ? aiStatus.message
          : null;

  return (
    <>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <button
            onClick={() => navigate('/media-campaign/campaigns')}
            className="flex items-center gap-2 text-sm text-neutral-400 hover:text-white mb-3 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Campaigns
          </button>
          <h1 className="text-3xl font-bold text-white mb-2">{campaign.name}</h1>
          <div className="flex flex-wrap items-center gap-4 text-sm text-neutral-400">
            {campaign.brandHandle && (
              <span className="flex items-center gap-1">
                <Tag className="w-4 h-4" />@{campaign.brandHandle}
                {brand?.niche && <span className="text-neutral-500">· {brand.niche}</span>}
              </span>
            )}
            <span className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              {formatDate(campaign.startDate)} – {formatDate(campaign.endDate)}
            </span>
            <span className="flex items-center gap-1">
              <DollarSign className="w-4 h-4" />
              {new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(campaign.totalBudget)}
            </span>
          </div>
          {campaign.brief && <p className="text-neutral-300 mt-3 max-w-3xl">{campaign.brief}</p>}
        </div>

        {aiProblem && (
          <div className="flex items-start gap-3 p-4 bg-amber-400/10 border border-amber-400/30 rounded-2xl text-amber-200 text-sm">
            <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <span>{aiProblem}</span>
          </div>
        )}

        {!campaign.brandId && (
          <div className="p-4 bg-amber-400/10 border border-amber-400/30 rounded-2xl text-amber-200 text-sm">
            This campaign has no brand yet. Edit the campaign and choose a brand to get creator suggestions.
          </div>
        )}

        {/* Find creators */}
        <div className="p-6 bg-neutral-800/50 backdrop-blur-sm border border-neutral-700 rounded-2xl">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-purple-400/20 rounded-xl">
              <Sparkles className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Find creators</h2>
              <p className="text-sm text-neutral-400">
                Ranked for @{campaign.brandHandle ?? 'brand'} by the recommendation model. New suggestions replace the
                ones you have not acted on.
              </p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
            <div>
              <label htmlFor="size" className="block text-sm text-neutral-300 mb-2">Audience size</label>
              <select
                id="size"
                value={sizeIndex}
                onChange={(e) => setSizeIndex(Number(e.target.value))}
                className="w-full p-3 bg-neutral-700 border border-neutral-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent cursor-pointer"
              >
                {SIZES.map((s, i) => (
                  <option key={s.label} value={i}>{s.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="niche" className="block text-sm text-neutral-300 mb-2">Niche</label>
              <select
                id="niche"
                value={niche}
                onChange={(e) => setNiche(e.target.value)}
                className="w-full p-3 bg-neutral-700 border border-neutral-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent cursor-pointer"
              >
                <option value="">Any niche</option>
                {NICHES.map((n) => (
                  <option key={n} value={n}>{n}</option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="count" className="block text-sm text-neutral-300 mb-2">How many</label>
              <select
                id="count"
                value={count}
                onChange={(e) => setCount(Number(e.target.value))}
                className="w-full p-3 bg-neutral-700 border border-neutral-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent cursor-pointer"
              >
                {[10, 20, 30, 50].map((n) => (
                  <option key={n} value={n}>{n} creators</option>
                ))}
              </select>
            </div>
            <button
              onClick={handleSuggest}
              disabled={suggesting || !campaign.brandId}
              className="flex items-center justify-center gap-2 px-6 py-3 bg-purple-500 hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl transition-all duration-200 font-medium"
            >
              {suggesting ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
              {suggesting ? 'Finding creators…' : 'Find creators'}
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex flex-wrap gap-2" role="tablist">
          {TABS.map((t) => (
            <button
              key={t.status}
              role="tab"
              aria-selected={activeTab === t.status}
              onClick={() => setActiveTab(t.status)}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                activeTab === t.status
                  ? 'bg-purple-500 text-white'
                  : 'bg-neutral-800/50 border border-neutral-700 text-neutral-300 hover:text-white'
              }`}
            >
              {t.label} <span className="ml-1 opacity-70">{counts[t.status] || 0}</span>
            </button>
          ))}
        </div>

        {/* List */}
        <div className="bg-neutral-800/50 backdrop-blur-sm border border-neutral-700 rounded-2xl overflow-hidden">
          {visible.length > 0 ? (
            <div className="divide-y divide-neutral-700">
              {visible.map((item) => (
                <div key={item.campaignCreatorId} className="p-6 hover:bg-neutral-700/30 transition-colors">
                  <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                    <div className="flex items-start gap-4 min-w-0">
                      <div className="w-12 h-12 flex-shrink-0 rounded-xl bg-purple-400/20 text-purple-300 flex items-center justify-center font-semibold uppercase">
                        {shortId(item.creatorId).slice(0, 2)}
                      </div>
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2 mb-1">
                          <h3 className="text-lg font-semibold text-white">Creator {shortId(item.creatorId)}</h3>
                          {item.status === 'Suggested' && (
                            <span className="text-xs px-2 py-0.5 rounded-full bg-neutral-700 text-neutral-300">#{item.rank} match</span>
                          )}
                        </div>
                        <div className="flex flex-wrap items-center gap-3 text-sm text-neutral-400 mb-3">
                          <span className="flex items-center gap-1">
                            <Users className="w-4 h-4" />
                            {formatFollowers(item.followers)} followers
                          </span>
                          {item.sizeTier && <span className="capitalize">{item.sizeTier}</span>}
                          {item.niche && <span>· {item.niche}</span>}
                          <span className="flex items-center gap-1">
                            <Mail className="w-4 h-4" />
                            {item.email}
                          </span>
                        </div>
                        {item.reasons.length > 0 && (
                          <ul className="space-y-1">
                            {item.reasons.map((r) => (
                              <li key={r.code} className="flex items-start gap-2 text-sm text-neutral-300">
                                <Check className="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" />
                                {r.text}
                              </li>
                            ))}
                          </ul>
                        )}
                        {item.lastEmail && (
                          <p className="text-sm text-neutral-400 mt-3">
                            Last e-mail: “{item.lastEmail.subject}” · {formatDate(item.lastEmail.sentAt)}
                          </p>
                        )}
                        {item.respondedAt && (
                          <p className="text-sm text-neutral-400 mt-1">Answer recorded {formatDate(item.respondedAt)}</p>
                        )}
                      </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-2 lg:justify-end">
                      <button
                        onClick={() => openProfile(item)}
                        className="p-2 text-neutral-400 hover:text-blue-400 hover:bg-blue-400/20 rounded-lg transition-all duration-200"
                        title="Creator profile"
                        aria-label={`Profile of creator ${shortId(item.creatorId)}`}
                      >
                        <User className="w-5 h-5" />
                      </button>
                      {item.status === 'Suggested' && (
                        <>
                          <button
                            onClick={() => handleStatus(item, 'dismiss')}
                            disabled={busyId === item.campaignCreatorId}
                            className="px-3 py-2 text-sm text-neutral-300 hover:text-white hover:bg-neutral-700 rounded-lg transition-colors"
                          >
                            Dismiss
                          </button>
                          <button
                            onClick={() => handleStatus(item, 'select')}
                            disabled={busyId === item.campaignCreatorId}
                            className="px-4 py-2 text-sm bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition-colors font-medium"
                          >
                            Select
                          </button>
                        </>
                      )}
                      {item.status === 'Selected' && (
                        <>
                          <button
                            onClick={() => handleStatus(item, 'unselect')}
                            disabled={busyId === item.campaignCreatorId}
                            className="px-3 py-2 text-sm text-neutral-300 hover:text-white hover:bg-neutral-700 rounded-lg transition-colors"
                          >
                            Unselect
                          </button>
                          <button
                            onClick={() => openEmail(item)}
                            className="flex items-center gap-2 px-4 py-2 text-sm bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition-colors font-medium"
                          >
                            <Sparkles className="w-4 h-4" /> Write e-mail
                          </button>
                        </>
                      )}
                      {item.status === 'Contacted' && (
                        <>
                          {item.lastEmail && (
                            <button
                              onClick={() => setViewEmail(item)}
                              className="px-3 py-2 text-sm text-neutral-300 hover:text-white hover:bg-neutral-700 rounded-lg transition-colors"
                            >
                              View e-mail
                            </button>
                          )}
                          <button
                            onClick={() => handleResponse(item, false)}
                            disabled={busyId === item.campaignCreatorId}
                            className="flex items-center gap-1 px-3 py-2 text-sm text-red-300 hover:text-white hover:bg-red-500/80 rounded-lg transition-colors"
                          >
                            <XCircle className="w-4 h-4" /> Declined
                          </button>
                          <button
                            onClick={() => handleResponse(item, true)}
                            disabled={busyId === item.campaignCreatorId}
                            className="flex items-center gap-1 px-4 py-2 text-sm bg-green-600 hover:bg-green-500 text-white rounded-lg transition-colors font-medium"
                          >
                            <CheckCircle2 className="w-4 h-4" /> Accepted
                          </button>
                        </>
                      )}
                      {(item.status === 'Accepted' || item.status === 'Declined') && item.lastEmail && (
                        <button
                          onClick={() => setViewEmail(item)}
                          className="px-3 py-2 text-sm text-neutral-300 hover:text-white hover:bg-neutral-700 rounded-lg transition-colors"
                        >
                          View e-mail
                        </button>
                      )}
                      {item.status === 'Dismissed' && (
                        <button
                          onClick={() => handleStatus(item, 'select')}
                          disabled={busyId === item.campaignCreatorId}
                          className="px-4 py-2 text-sm bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition-colors font-medium"
                        >
                          Select instead
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center">
              <Users className="w-16 h-16 text-neutral-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No {activeTab.toLowerCase()} creators</h3>
              <p className="text-neutral-400">
                {activeTab === 'Suggested'
                  ? 'Use “Find creators” to get creators ranked for this brand.'
                  : activeTab === 'Selected'
                    ? 'Select creators from the Suggested tab to contact them.'
                    : 'Creators move here as you work through the outreach.'}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* E-mail composer */}
      {emailFor && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="email-title"
            className="bg-neutral-800 border border-neutral-700 rounded-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 id="email-title" className="text-xl font-semibold text-white">
                E-mail to creator {shortId(emailFor.creatorId)}
              </h2>
              <button
                onClick={closeEmail}
                className="p-2 text-neutral-400 hover:text-white rounded-lg transition-colors"
                aria-label="Close"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {drafting || !draft ? (
              <div className="py-16 flex flex-col items-center gap-4 text-neutral-300">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-purple-400"></div>
                <p>Writing a personal e-mail from the campaign brief and the creator's profile…</p>
                <p className="text-sm text-neutral-500">With a local model this can take up to a minute.</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2 text-xs">
                  {draft.provider === 'template' ? (
                    <span className="flex items-center gap-1 px-2 py-1 rounded-full bg-amber-400/15 text-amber-200">
                      <AlertTriangle className="w-3.5 h-3.5" /> Template e-mail
                      {draft.fallbackReason ? ` — ${draft.fallbackReason}` : ''}
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 px-2 py-1 rounded-full bg-purple-400/15 text-purple-200">
                      <Sparkles className="w-3.5 h-3.5" /> Written by AI{draft.model ? ` (${draft.model})` : ''}
                    </span>
                  )}
                  {draft.checksPassed && !edited ? (
                    <span className="flex items-center gap-1 px-2 py-1 rounded-full bg-green-400/15 text-green-200">
                      <ShieldCheck className="w-3.5 h-3.5" /> Checked: no invented numbers, prices or handles
                    </span>
                  ) : edited ? (
                    <span className="px-2 py-1 rounded-full bg-neutral-700 text-neutral-300">Edited by you</span>
                  ) : null}
                </div>
                {draft.issues.length > 0 && (
                  <ul className="text-sm text-amber-200 list-disc pl-5">
                    {draft.issues.map((i) => <li key={i}>{i}</li>)}
                  </ul>
                )}

                <div>
                  <label htmlFor="email-to" className="block text-sm text-neutral-300 mb-2">To</label>
                  <input
                    id="email-to"
                    readOnly
                    value={draft.toEmail}
                    className="w-full p-3 bg-neutral-700/50 border border-neutral-600 rounded-xl text-neutral-300"
                  />
                </div>
                <div>
                  <label htmlFor="email-subject" className="block text-sm text-neutral-300 mb-2">Subject</label>
                  <input
                    id="email-subject"
                    value={subject}
                    maxLength={200}
                    onChange={(e) => { setSubject(e.target.value); setEdited(true); }}
                    className="w-full p-3 bg-neutral-700 border border-neutral-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent"
                  />
                </div>
                <div>
                  <label htmlFor="email-body" className="block text-sm text-neutral-300 mb-2">Message</label>
                  <textarea
                    id="email-body"
                    rows={12}
                    value={body}
                    maxLength={5000}
                    onChange={(e) => { setBody(e.target.value); setEdited(true); }}
                    className="w-full p-3 bg-neutral-700 border border-neutral-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent resize-y"
                  />
                </div>

                <div className="flex flex-wrap justify-between gap-3 pt-2">
                  <button
                    onClick={() => loadDraft(emailFor)}
                    disabled={sending}
                    className="flex items-center gap-2 px-4 py-2 text-neutral-300 hover:text-white hover:bg-neutral-700 rounded-xl transition-colors"
                  >
                    <RefreshCw className="w-4 h-4" /> Write again
                  </button>
                  <div className="flex gap-3">
                    <button onClick={closeEmail} className="px-4 py-2 text-neutral-400 hover:text-white transition-colors">
                      Cancel
                    </button>
                    <button
                      onClick={handleSend}
                      disabled={sending || !subject.trim() || !body.trim()}
                      className="flex items-center gap-2 px-6 py-2 bg-purple-500 hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl transition-colors font-medium"
                    >
                      {sending ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                      {sending ? 'Sending…' : 'Send e-mail'}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Sent e-mail */}
      {viewEmail?.lastEmail && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div role="dialog" aria-modal="true" aria-labelledby="sent-title"
               className="bg-neutral-800 border border-neutral-700 rounded-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 id="sent-title" className="text-xl font-semibold text-white">{viewEmail.lastEmail.subject}</h2>
              <button onClick={() => setViewEmail(null)} className="p-2 text-neutral-400 hover:text-white rounded-lg transition-colors" aria-label="Close">
                <X className="w-5 h-5" />
              </button>
            </div>
            <p className="text-sm text-neutral-400 mb-4">
              To {viewEmail.lastEmail.toEmail} · {formatDate(viewEmail.lastEmail.sentAt)} ·{' '}
              {viewEmail.lastEmail.provider === 'template' ? 'template' : `AI (${viewEmail.lastEmail.provider})`}
              {viewEmail.lastEmail.editedByUser ? ', edited' : ''}
            </p>
            <p className="text-neutral-200 whitespace-pre-line">{viewEmail.lastEmail.body}</p>
          </div>
        </div>
      )}

      {/* Creator profile */}
      {profile && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div role="dialog" aria-modal="true" aria-labelledby="profile-title"
               className="bg-neutral-800 border border-neutral-700 rounded-2xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-6">
              <h2 id="profile-title" className="text-xl font-semibold text-white">Creator {shortId(profile.creatorId)}</h2>
              <button onClick={() => setProfile(null)} className="p-2 text-neutral-400 hover:text-white rounded-lg transition-colors" aria-label="Close">
                <X className="w-5 h-5" />
              </button>
            </div>
            <dl className="grid grid-cols-2 gap-4 text-sm">
              <div><dt className="text-neutral-400">Followers</dt><dd className="text-white font-medium">{formatFollowers(profile.followers)}</dd></div>
              <div><dt className="text-neutral-400">Size</dt><dd className="text-white font-medium capitalize">{profile.sizeTier ?? '—'}</dd></div>
              <div><dt className="text-neutral-400">Niche</dt><dd className="text-white font-medium">{profile.niche ?? '—'}</dd></div>
              <div><dt className="text-neutral-400">Last post</dt><dd className="text-white font-medium">{profile.lastPost ? formatDate(profile.lastPost) : '—'}</dd></div>
              <div><dt className="text-neutral-400">Paid collaborations</dt><dd className="text-white font-medium">{profile.paidBrandsTotal} brands</dd></div>
              <div><dt className="text-neutral-400">In the last 6 months</dt><dd className="text-white font-medium">{profile.paidBrands180d} brands</dd></div>
            </dl>
            {profile.recentBrands.length > 0 && (
              <div className="mt-6">
                <p className="text-sm text-neutral-400 mb-2">Recent brand collaborations</p>
                <div className="flex flex-wrap gap-2">
                  {profile.recentBrands.map((b) => (
                    <span key={b} className="text-xs px-2 py-1 rounded-full bg-neutral-700 text-neutral-200">@{b}</span>
                  ))}
                </div>
              </div>
            )}
            <p className="text-xs text-neutral-500 mt-6">
              Creators are shown under pseudonyms; data comes from a public research dataset (2017–2019).
            </p>
          </div>
        </div>
      )}
    </>
  );
};

export default CampaignInfluencers;
