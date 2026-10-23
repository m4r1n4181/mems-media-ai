using System.Text.RegularExpressions;

namespace MusicEventManagementSystem.API.Services.Marketing
{
    /// <summary>Small shared rules for brand handles and their list of similar brands.</summary>
    public static class BrandRules
    {
        public const int MaxSimilarBrands = 5;

        // Instagram usernames: letters, digits, dots and underscores, at most 30 characters.
        private static readonly Regex HandlePattern = new("^[a-z0-9._]{1,30}$", RegexOptions.Compiled);

        /// <summary>"@GlowSkin " -> "glowskin"; null if it cannot be an Instagram handle.</summary>
        public static string? NormalizeHandle(string? raw)
        {
            var h = (raw ?? "").Trim().TrimStart('@').ToLowerInvariant();
            return HandlePattern.IsMatch(h) ? h : null;
        }

        public static List<string> SplitSimilar(string? stored) =>
            string.IsNullOrWhiteSpace(stored)
                ? new List<string>()
                : stored.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries).ToList();
    }
}
