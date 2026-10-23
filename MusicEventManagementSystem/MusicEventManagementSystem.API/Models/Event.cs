using MusicEventManagementSystem.Enums;

namespace MusicEventManagementSystem.API.Models
{
    public class Event
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public DateTime EventInterval { get; set; }
        public EventStatus Status { get; set; } 
        public Guid CreatedById { get; set; }
        public int LocationId { get; set; }
        //public Location Location { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime UpdatedAt { get; set; }
        public DateTime? DeletedAt { get; set; }

        // Navigation property - Event - (1,N) -> TicketType
        public ICollection<TicketType> TicketTypes { get; set; } = new List<TicketType>();

        // Navigation property - Event - (1,N) -> PricingRule
        public ICollection<PricingRule> PricingRules { get; set; } = new List<PricingRule>();
    }

}
