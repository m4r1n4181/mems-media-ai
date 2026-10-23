namespace MusicEventManagementSystem.API.Models
{
    /// <summary>A client brand the agency runs campaigns for.</summary>
    public class Brand
    {
        public int BrandId { get; set; }
        public string Handle { get; set; } = string.Empty;      // Instagram handle, also the key in ml-service
        public string DisplayName { get; set; } = string.Empty;
        public string? Niche { get; set; }
        public int Followers { get; set; }
        public int? TypicalPartnerFollowers { get; set; }
        public bool IsClient { get; set; } = true;
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        public virtual ICollection<Campaign> Campaigns { get; set; } = new List<Campaign>();
    }
}
