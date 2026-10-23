using MusicEventManagementSystem.Enums;

namespace MusicEventManagementSystem.API.Models
{
    /// <summary>A creator suggested for / contacted in a campaign. Also the feedback log of the recommender:
    /// which suggestions managers selected and which creators accepted, with the model version that suggested them.</summary>
    public class CampaignCreator
    {
        public int CampaignCreatorId { get; set; }
        public int CampaignId { get; set; }
        public string CreatorId { get; set; } = string.Empty;
        public InfluencerStatus Status { get; set; } = InfluencerStatus.Suggested;

        public int Rank { get; set; }
        public double Score { get; set; }
        public string ReasonsJson { get; set; } = "[]";
        public string ModelVersion { get; set; } = string.Empty;

        public DateTime SuggestedAt { get; set; } = DateTime.UtcNow;
        public DateTime? SelectedAt { get; set; }
        public DateTime? ContactedAt { get; set; }
        public DateTime? RespondedAt { get; set; }
        public string? Note { get; set; }

        public virtual Campaign Campaign { get; set; } = null!;
        public virtual Creator Creator { get; set; } = null!;
        public virtual ICollection<OutreachEmail> Emails { get; set; } = new List<OutreachEmail>();
    }
}
