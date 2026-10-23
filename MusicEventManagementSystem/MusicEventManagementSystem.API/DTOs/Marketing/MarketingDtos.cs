using System.ComponentModel.DataAnnotations;
using System.Text.Json;

namespace MusicEventManagementSystem.API.DTOs.Marketing
{
    public class BrandDto
    {
        public int BrandId { get; set; }
        public string Handle { get; set; } = string.Empty;
        public string DisplayName { get; set; } = string.Empty;
        public string? Niche { get; set; }
        public int Followers { get; set; }
        public int? TypicalPartnerFollowers { get; set; }
        public int CampaignCount { get; set; }
    }

    public class CreatorProfileDto
    {
        public string CreatorId { get; set; } = string.Empty;
        public int Followers { get; set; }
        public string? SizeTier { get; set; }
        public string? Niche { get; set; }
        public int PaidBrandsTotal { get; set; }
        public int PaidBrands180d { get; set; }
        public double? MedianRelEngagement { get; set; }
        public string? LastPost { get; set; }
        public List<string> RecentBrands { get; set; } = new();
    }

    public class ReasonDto
    {
        public string Code { get; set; } = string.Empty;
        public string Text { get; set; } = string.Empty;
    }

    public class OutreachEmailDto
    {
        public int OutreachEmailId { get; set; }
        public string ToEmail { get; set; } = string.Empty;
        public string Subject { get; set; } = string.Empty;
        public string Body { get; set; } = string.Empty;
        public string Provider { get; set; } = string.Empty;
        public bool ChecksPassed { get; set; }
        public bool EditedByUser { get; set; }
        public DateTime SentAt { get; set; }
    }

    public class CampaignInfluencerDto
    {
        public int CampaignCreatorId { get; set; }
        public int CampaignId { get; set; }
        public string CreatorId { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;
        public int Rank { get; set; }
        public double Score { get; set; }
        public List<ReasonDto> Reasons { get; set; } = new();
        public string ModelVersion { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public int Followers { get; set; }
        public string? SizeTier { get; set; }
        public string? Niche { get; set; }
        public DateTime SuggestedAt { get; set; }
        public DateTime? ContactedAt { get; set; }
        public DateTime? RespondedAt { get; set; }
        public string? Note { get; set; }
        public OutreachEmailDto? LastEmail { get; set; }
    }

    public class SuggestRequestDto
    {
        [Range(1, 100)] public int Count { get; set; } = 20;
        [Range(0, int.MaxValue)] public int? MinFollowers { get; set; }
        [Range(0, int.MaxValue)] public int? MaxFollowers { get; set; }
        public string? Niche { get; set; }
    }

    public class SenderDto
    {
        [Required, StringLength(120)] public string Name { get; set; } = string.Empty;
        [EmailAddress, StringLength(200)] public string? Email { get; set; }
    }

    public class EmailDraftDto
    {
        public string Subject { get; set; } = string.Empty;
        public string Body { get; set; } = string.Empty;
        public string Provider { get; set; } = string.Empty;
        public string? Model { get; set; }
        public bool ChecksPassed { get; set; }
        public List<string> Issues { get; set; } = new();
        public string? FallbackReason { get; set; }
        public string ToEmail { get; set; } = string.Empty;
    }

    public class SendEmailRequestDto
    {
        [Required, StringLength(200, MinimumLength = 1)] public string Subject { get; set; } = string.Empty;
        [Required, StringLength(5000, MinimumLength = 1)] public string Body { get; set; } = string.Empty;
        [StringLength(20)] public string Provider { get; set; } = "manual";
        [StringLength(100)] public string? Model { get; set; }
        public bool ChecksPassed { get; set; }
        public bool EditedByUser { get; set; }
        [Required] public SenderDto Sender { get; set; } = new();
        public string? SentByUserId { get; set; }
    }

    public class ResponseRequestDto
    {
        public bool Accepted { get; set; }
        [StringLength(1000)] public string? Note { get; set; }
    }

    public class AiStatusDto
    {
        public bool ServiceAvailable { get; set; }
        public string? ModelVersion { get; set; }
        public string? LlmProvider { get; set; }
        public string? LlmModel { get; set; }
        public bool LlmAvailable { get; set; }
        public string? Message { get; set; }
    }
}
