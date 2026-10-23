namespace MusicEventManagementSystem.API.Models
{
    /// <summary>An influencer the agency may contact. Stored when first suggested for a campaign;
    /// the profile itself comes from ml-service. Ids are pseudonyms (c_...), never real usernames.</summary>
    public class Creator
    {
        public string CreatorId { get; set; } = string.Empty;
        public int Followers { get; set; }
        public string? SizeTier { get; set; }
        public string? Niche { get; set; }
        public string Email { get; set; } = string.Empty;          // demo address on example.com (reserved, never delivered)
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        public virtual ICollection<CampaignCreator> Campaigns { get; set; } = new List<CampaignCreator>();
    }
}
