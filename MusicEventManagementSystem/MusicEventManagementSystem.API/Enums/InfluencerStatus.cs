namespace MusicEventManagementSystem.Enums
{
    /// <summary>Where a recommended creator is in a campaign's influencer outreach.</summary>
    public enum InfluencerStatus
    {
        Suggested = 1,   // recommended by the model, nobody has acted on it yet
        Selected = 2,    // the manager wants to contact this creator
        Contacted = 3,   // an outreach e-mail was sent
        Accepted = 4,    // the creator agreed to collaborate
        Declined = 5,    // the creator said no
        Dismissed = 6    // the manager rejected the suggestion
    }
}
