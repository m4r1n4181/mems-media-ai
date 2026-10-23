// MusicEventManagementSystem.API/Models/Campaign.cs
namespace MusicEventManagementSystem.API.Models
{
    public class Campaign
    {
        public int CampaignId { get; set; }
        // The client brand this campaign is run for (was: EventId, before the app became a marketing tool)
        public int? BrandId { get; set; }
        public string Name { get; set; }
        public string? Brief { get; set; }
        public DateTime StartDate { get; set; }
        public DateTime EndDate { get; set; }
        public decimal TotalBudget { get; set; }


        public virtual ICollection<Ad> Ads { get; set; } = new List<Ad>();
        public virtual Brand? Brand { get; set; }
        public virtual ICollection<CampaignCreator> Influencers { get; set; } = new List<CampaignCreator>();
    }
}