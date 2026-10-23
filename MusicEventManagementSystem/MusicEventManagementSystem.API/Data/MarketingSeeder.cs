using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using MusicEventManagementSystem.API.Models;
using MusicEventManagementSystem.Data;

namespace MusicEventManagementSystem.API.Data
{
    /// <summary>Seeds the client brands (exported by ml/scripts/export_service.py into Data/Seed/client_brands.json)
    /// and turns campaigns without a brand (the old event campaigns) into brand campaigns. Safe to run on every start.</summary>
    public static class MarketingSeeder
    {
        private record SeedBrand(string Brand, int Followers, string? Niche, int? TypicalPartnerFollowers);

        private static readonly (string Name, string Brief)[] CampaignTemplates =
        {
            ("Spring Launch", "Introduce our new spring collection to a younger audience with authentic, everyday content."),
            ("Summer Essentials", "Show our bestsellers in real summer moments: travel, outdoors and weekend plans."),
            ("Back to Routine", "Help followers build a simple daily routine around our products after the holidays."),
            ("Holiday Gift Guide", "Feature our products as thoughtful holiday gifts, with honest personal recommendations."),
            ("Brand Awareness Push", "Reach new audiences in our niche and grow followers with creator-led storytelling."),
        };

        public static async Task SeedAsync(ApplicationDbContext context, string contentRoot, ILogger logger)
        {
            if (!await context.Brands.AnyAsync())
            {
                var file = Path.Combine(contentRoot, "Data", "Seed", "client_brands.json");
                if (!File.Exists(file))
                {
                    logger.LogWarning("No client brands seed file at {File}; brands were not seeded.", file);
                    return;
                }
                var brands = JsonSerializer.Deserialize<List<SeedBrand>>(await File.ReadAllTextAsync(file),
                                 new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower }) ?? new();
                context.Brands.AddRange(brands.Select(b => new Brand
                {
                    Handle = b.Brand,
                    DisplayName = b.Brand,
                    Niche = b.Niche,
                    Followers = b.Followers,
                    TypicalPartnerFollowers = b.TypicalPartnerFollowers,
                    IsClient = true,
                }));
                await context.SaveChangesAsync();
                logger.LogInformation("Seeded {Count} client brands.", brands.Count);
            }

            var orphan = await context.Campaigns.Where(c => c.BrandId == null).OrderBy(c => c.CampaignId).ToListAsync();
            if (orphan.Count == 0) return;
            var clients = await context.Brands.Where(b => b.IsClient).OrderByDescending(b => b.Followers).ToListAsync();
            if (clients.Count == 0) return;
            for (int i = 0; i < orphan.Count; i++)
            {
                var brand = clients[(i * 7) % clients.Count];                 // spread campaigns over different niches
                var (name, brief) = CampaignTemplates[i % CampaignTemplates.Length];
                orphan[i].BrandId = brand.BrandId;
                orphan[i].Name = name;
                orphan[i].Brief ??= brief;
            }
            await context.SaveChangesAsync();
            logger.LogInformation("Assigned brands to {Count} campaigns that had none.", orphan.Count);
        }
    }
}
