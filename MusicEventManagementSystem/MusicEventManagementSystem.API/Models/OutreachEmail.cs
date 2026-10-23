namespace MusicEventManagementSystem.API.Models
{
    /// <summary>An outreach e-mail that was sent, with how it was written (LLM or template) and whether it passed checks.</summary>
    public class OutreachEmail
    {
        public int OutreachEmailId { get; set; }
        public int CampaignCreatorId { get; set; }
        public string ToEmail { get; set; } = string.Empty;
        public string FromEmail { get; set; } = string.Empty;
        public string Subject { get; set; } = string.Empty;
        public string Body { get; set; } = string.Empty;
        public string Provider { get; set; } = string.Empty;   // ollama | openai | anthropic | template | manual
        public string? Model { get; set; }
        public bool ChecksPassed { get; set; }
        public bool EditedByUser { get; set; }
        public string? SentByUserId { get; set; }
        public DateTime SentAt { get; set; } = DateTime.UtcNow;

        public virtual CampaignCreator CampaignCreator { get; set; } = null!;
    }
}
