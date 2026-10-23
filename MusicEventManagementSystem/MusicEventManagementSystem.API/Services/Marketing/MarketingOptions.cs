namespace MusicEventManagementSystem.API.Services.Marketing
{
    public class MlServiceOptions
    {
        public string BaseUrl { get; set; } = "http://localhost:8000";
        public int TimeoutSeconds { get; set; } = 300;    // > 2 LLM attempts x LLM_TIMEOUT_S (120 s) in ml-service
    }

    public class EmailOptions
    {
        /// <summary>"pickup" writes each e-mail as an .eml file (default, works without a mail server);
        /// "smtp" sends through an SMTP server, e.g. Mailpit on localhost:1025 during development.</summary>
        public string Mode { get; set; } = "pickup";
        public string PickupDirectory { get; set; } = "sent-emails";
        public string SmtpHost { get; set; } = "localhost";
        public int SmtpPort { get; set; } = 1025;
        public bool SmtpSsl { get; set; } = false;
        public string? SmtpUser { get; set; }
        public string? SmtpPassword { get; set; }
        public string FromAddress { get; set; } = "campaigns@mems-agency.example.com";
        public string FromName { get; set; } = "MEMS Agency";
    }

    public class AgencyOptions
    {
        public string Name { get; set; } = "MEMS Agency";
        public string CreatorEmailDomain { get; set; } = "creators.example.com";   // reserved domain: never delivered
    }
}
