using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;
using MusicEventManagementSystem.API.DTOs.Marketing;
using MusicEventManagementSystem.API.Models;
using MusicEventManagementSystem.Data;
using MusicEventManagementSystem.Enums;

namespace MusicEventManagementSystem.API.Services.Marketing
{
    public class NotFoundException : Exception { public NotFoundException(string m) : base(m) { } }
    public class InvalidStateException : Exception { public InvalidStateException(string m) : base(m) { } }

    public interface IInfluencerService
    {
        Task<List<CampaignInfluencerDto>> ListAsync(int campaignId);
        Task<List<CampaignInfluencerDto>> SuggestAsync(int campaignId, SuggestRequestDto req);
        Task<CampaignInfluencerDto> ChangeStatusAsync(int campaignCreatorId, string action);
        Task<EmailDraftDto> DraftEmailAsync(int campaignCreatorId, SenderDto sender);
        Task<CampaignInfluencerDto> SendEmailAsync(int campaignCreatorId, SendEmailRequestDto req);
        Task<CampaignInfluencerDto> RecordResponseAsync(int campaignCreatorId, ResponseRequestDto req);
        Task<CreatorProfileDto?> GetCreatorAsync(string creatorId);
        Task<AiStatusDto> GetAiStatusAsync();
    }

    /// <summary>Influencer outreach inside a campaign:
    /// suggest (ml-service) → select → AI-drafted e-mail → send → record the creator's answer.</summary>
    public class InfluencerService : IInfluencerService
    {
        private readonly ApplicationDbContext _db;
        private readonly MlServiceClient _ml;
        private readonly IEmailSender _email;
        private readonly AgencyOptions _agency;
        private readonly EmailOptions _emailOpt;

        public InfluencerService(ApplicationDbContext db, MlServiceClient ml, IEmailSender email,
                                 IOptions<AgencyOptions> agency, IOptions<EmailOptions> emailOpt)
        {
            _db = db; _ml = ml; _email = email; _agency = agency.Value; _emailOpt = emailOpt.Value;
        }

        public async Task<List<CampaignInfluencerDto>> ListAsync(int campaignId)
        {
            await GetCampaignAsync(campaignId);
            var rows = await Query().Where(cc => cc.CampaignId == campaignId).ToListAsync();
            return rows.OrderBy(r => StatusOrder(r.Status)).ThenBy(r => r.Rank).Select(ToDto).ToList();
        }

        public async Task<List<CampaignInfluencerDto>> SuggestAsync(int campaignId, SuggestRequestDto req)
        {
            var campaign = await GetCampaignAsync(campaignId);
            if (campaign.Brand == null)
                throw new InvalidStateException("This campaign has no brand. Choose a brand for the campaign first.");

            var existing = await _db.CampaignCreators.Where(cc => cc.CampaignId == campaignId).ToListAsync();
            // New suggestions replace the old ones nobody acted on; creators already handled are never suggested again.
            _db.CampaignCreators.RemoveRange(existing.Where(e => e.Status == InfluencerStatus.Suggested));
            var keep = existing.Where(e => e.Status != InfluencerStatus.Suggested).Select(e => e.CreatorId).ToHashSet();

            var brand = campaign.Brand;
            MlRecommendations? recs = null;
            var modelVersionTag = "";
            if (brand.KnownToModel)
                recs = await _ml.RecommendAsync(brand.Handle, req.Count, req.MinFollowers, req.MaxFollowers, req.Niche, keep);
            if (recs == null)
            {
                // Cold start: the model has never seen this brand, so fuse the lists of brands it resembles.
                var similar = BrandRules.SplitSimilar(brand.SimilarBrands);
                if (similar.Count == 0)
                    throw new InvalidStateException(
                        $"The recommender does not know @{brand.Handle} yet. Add similar brands to it on the Brands page.");
                recs = await _ml.LookalikeAsync(similar, req.Count, req.MinFollowers, req.MaxFollowers, req.Niche, keep,
                                                brand.Niche)
                       ?? throw new InvalidStateException("None of this brand's similar brands is known to the recommender.");
                modelVersionTag = "+lookalike";
            }

            var ids = recs.Items.Select(i => i.CreatorId).ToList();
            var known = await _db.Creators.Where(c => ids.Contains(c.CreatorId)).ToDictionaryAsync(c => c.CreatorId);
            foreach (var item in recs.Items)
            {
                if (!known.ContainsKey(item.CreatorId))
                {
                    var c = new Creator
                    {
                        CreatorId = item.CreatorId,
                        Followers = item.Creator.Followers,
                        SizeTier = item.Creator.SizeTier,
                        Niche = item.Creator.Niche,
                        Email = $"{item.CreatorId}@{_agency.CreatorEmailDomain}",
                    };
                    _db.Creators.Add(c);
                    known[c.CreatorId] = c;
                }
                _db.CampaignCreators.Add(new CampaignCreator
                {
                    CampaignId = campaignId,
                    CreatorId = item.CreatorId,
                    Status = InfluencerStatus.Suggested,
                    Rank = item.Rank,
                    Score = item.Score,
                    ReasonsJson = JsonSerializer.Serialize(item.Reasons),
                    ModelVersion = recs.ModelVersion + modelVersionTag,
                });
            }
            await _db.SaveChangesAsync();
            return await ListAsync(campaignId);
        }

        public async Task<CampaignInfluencerDto> ChangeStatusAsync(int id, string action)
        {
            var cc = await GetRowAsync(id);
            (InfluencerStatus[] from, InfluencerStatus to) = action switch
            {
                "select" => (new[] { InfluencerStatus.Suggested, InfluencerStatus.Dismissed }, InfluencerStatus.Selected),
                "unselect" => (new[] { InfluencerStatus.Selected }, InfluencerStatus.Suggested),
                "dismiss" => (new[] { InfluencerStatus.Suggested, InfluencerStatus.Selected }, InfluencerStatus.Dismissed),
                _ => throw new InvalidStateException($"Unknown action '{action}'."),
            };
            if (!from.Contains(cc.Status))
                throw new InvalidStateException($"Cannot {action} a creator who is {cc.Status}.");
            cc.Status = to;
            cc.SelectedAt = to == InfluencerStatus.Selected ? DateTime.UtcNow : cc.SelectedAt;
            await _db.SaveChangesAsync();
            return ToDto(cc);
        }

        public async Task<EmailDraftDto> DraftEmailAsync(int id, SenderDto sender)
        {
            var cc = await GetRowAsync(id);
            if (cc.Status is not (InfluencerStatus.Selected or InfluencerStatus.Contacted))
                throw new InvalidStateException("Select the creator before writing an e-mail.");
            var campaign = cc.Campaign;
            if (campaign.Brand == null) throw new InvalidStateException("This campaign has no brand.");

            var draft = await _ml.DraftAsync(new
            {
                brand = campaign.Brand.Handle,
                creator_id = cc.CreatorId,
                // used by ml-service only when it does not know the brand (cold start)
                brand_niche = campaign.Brand.Niche,
                similar_brands = campaign.Brand.KnownToModel ? null : BrandRules.SplitSimilar(campaign.Brand.SimilarBrands),
                campaign = new
                {
                    name = campaign.Name,
                    brief = campaign.Brief,
                    // Stored in UTC; the app shows campaign dates in local time, so the e-mail must too
                    // (otherwise a campaign that starts just after midnight is a day off).
                    start_date = campaign.StartDate.ToLocalTime().ToString("yyyy-MM-dd"),
                    end_date = campaign.EndDate.ToLocalTime().ToString("yyyy-MM-dd"),
                },
                sender = new { name = sender.Name, company = _agency.Name, email = sender.Email },
            });
            return new EmailDraftDto
            {
                Subject = draft.Subject,
                Body = draft.Body,
                Provider = draft.Provider,
                Model = draft.Model,
                ChecksPassed = draft.Checks.Passed,
                Issues = draft.Checks.Issues ?? new List<string>(),
                FallbackReason = draft.FallbackReason,
                ToEmail = cc.Creator.Email,
            };
        }

        public async Task<CampaignInfluencerDto> SendEmailAsync(int id, SendEmailRequestDto req)
        {
            var cc = await GetRowAsync(id);
            if (cc.Status is not (InfluencerStatus.Selected or InfluencerStatus.Contacted))
                throw new InvalidStateException("Only selected creators can be contacted.");

            await _email.SendAsync(cc.Creator.Email, req.Subject, req.Body, req.Sender.Email, req.Sender.Name);
            cc.Emails.Add(new OutreachEmail
            {
                ToEmail = cc.Creator.Email,
                FromEmail = _emailOpt.FromAddress,
                Subject = req.Subject,
                Body = req.Body,
                Provider = req.Provider,
                Model = req.Model,
                ChecksPassed = req.ChecksPassed,
                EditedByUser = req.EditedByUser,
                SentByUserId = req.SentByUserId,
            });
            cc.Status = InfluencerStatus.Contacted;
            cc.ContactedAt = DateTime.UtcNow;
            await _db.SaveChangesAsync();
            return ToDto(cc);
        }

        public async Task<CampaignInfluencerDto> RecordResponseAsync(int id, ResponseRequestDto req)
        {
            var cc = await GetRowAsync(id);
            if (cc.Status is not (InfluencerStatus.Contacted or InfluencerStatus.Accepted or InfluencerStatus.Declined))
                throw new InvalidStateException("Record a response only after the creator was contacted.");
            cc.Status = req.Accepted ? InfluencerStatus.Accepted : InfluencerStatus.Declined;
            cc.RespondedAt = DateTime.UtcNow;
            cc.Note = req.Note;
            await _db.SaveChangesAsync();
            return ToDto(cc);
        }

        public async Task<CreatorProfileDto?> GetCreatorAsync(string creatorId)
        {
            var c = await _ml.CreatorAsync(creatorId);
            return c == null ? null : new CreatorProfileDto
            {
                CreatorId = c.CreatorId, Followers = c.Followers, SizeTier = c.SizeTier, Niche = c.Niche,
                PaidBrandsTotal = c.PaidBrandsTotal, PaidBrands180d = c.PaidBrands180d,
                MedianRelEngagement = c.MedianRelEngagement, LastPost = c.LastPost, RecentBrands = c.RecentBrands ?? new(),
            };
        }

        public async Task<AiStatusDto> GetAiStatusAsync()
        {
            try
            {
                var h = await _ml.HealthAsync();
                return new AiStatusDto
                {
                    ServiceAvailable = h?.Data.Loaded == true,
                    ModelVersion = h?.Data.ModelVersion,
                    LlmProvider = h?.Llm.Provider,
                    LlmModel = h?.Llm.Model,
                    LlmAvailable = h?.Llm.Available == true,
                    Message = h?.Data.Loaded == true
                        ? (h.Llm.Available ? null : $"AI writing is off ({h.Llm.Error ?? "no model"}); e-mails use a template.")
                        : h?.Data.Error,
                };
            }
            catch (MlServiceUnavailableException e)
            {
                return new AiStatusDto { ServiceAvailable = false, Message = e.Message };
            }
        }

        // ---------- helpers ----------
        private IQueryable<CampaignCreator> Query() =>
            _db.CampaignCreators.Include(cc => cc.Creator).Include(cc => cc.Emails)
               .Include(cc => cc.Campaign).ThenInclude(c => c.Brand);

        private async Task<Campaign> GetCampaignAsync(int id) =>
            await _db.Campaigns.Include(c => c.Brand).FirstOrDefaultAsync(c => c.CampaignId == id)
            ?? throw new NotFoundException($"Campaign {id} not found.");

        private async Task<CampaignCreator> GetRowAsync(int id) =>
            await Query().FirstOrDefaultAsync(cc => cc.CampaignCreatorId == id)
            ?? throw new NotFoundException($"Campaign influencer {id} not found.");

        private static int StatusOrder(InfluencerStatus s) => s switch
        {
            InfluencerStatus.Accepted => 0, InfluencerStatus.Contacted => 1, InfluencerStatus.Selected => 2,
            InfluencerStatus.Suggested => 3, InfluencerStatus.Declined => 4, _ => 5,
        };

        private static CampaignInfluencerDto ToDto(CampaignCreator cc)
        {
            var reasons = new List<ReasonDto>();
            try
            {
                foreach (var r in JsonSerializer.Deserialize<List<JsonElement>>(cc.ReasonsJson) ?? new())
                    reasons.Add(new ReasonDto
                    {
                        Code = r.TryGetProperty("code", out var code) ? code.GetString() ?? "" : "",
                        Text = r.TryGetProperty("text", out var text) ? text.GetString() ?? "" : "",
                    });
            }
            catch (JsonException) { }
            var last = cc.Emails.OrderByDescending(e => e.SentAt).FirstOrDefault();
            return new CampaignInfluencerDto
            {
                CampaignCreatorId = cc.CampaignCreatorId, CampaignId = cc.CampaignId, CreatorId = cc.CreatorId,
                Status = cc.Status.ToString(), Rank = cc.Rank, Score = cc.Score, Reasons = reasons,
                ModelVersion = cc.ModelVersion, Email = cc.Creator?.Email ?? "", Followers = cc.Creator?.Followers ?? 0,
                SizeTier = cc.Creator?.SizeTier, Niche = cc.Creator?.Niche, SuggestedAt = cc.SuggestedAt,
                ContactedAt = cc.ContactedAt, RespondedAt = cc.RespondedAt, Note = cc.Note,
                LastEmail = last == null ? null : new OutreachEmailDto
                {
                    OutreachEmailId = last.OutreachEmailId, ToEmail = last.ToEmail, Subject = last.Subject,
                    Body = last.Body, Provider = last.Provider, ChecksPassed = last.ChecksPassed,
                    EditedByUser = last.EditedByUser, SentAt = last.SentAt,
                },
            };
        }
    }
}
