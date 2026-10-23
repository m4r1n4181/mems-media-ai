using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace MusicEventManagementSystem.API.Services.Marketing
{
    public class MlServiceUnavailableException : Exception
    {
        public MlServiceUnavailableException(string message, Exception? inner = null) : base(message, inner) { }
    }

    // ---- shapes returned by ml-service (snake_case JSON) ----
    public record MlReason(string Code, string? Text);
    public record MlCreator(string CreatorId, int Followers, string? SizeTier, string? Niche, int PaidBrandsTotal,
                            int PaidBrands180d, double? MedianRelEngagement, int PostsInData, string? LastPost,
                            List<string>? RecentBrands);
    public record MlRecommendation(string CreatorId, int Rank, double Score, List<JsonElement> Reasons, MlCreator Creator);
    public record MlRecommendations(string Brand, string ModelVersion, string AsOf, List<MlRecommendation> Items);
    public record MlBrand(string Brand, int Followers, string? Niche, int CreatorsMentioning, int RecentPaidCreators,
                          int? TypicalPartnerFollowers);
    public record MlChecks(bool Passed, List<string>? Issues);
    public record MlDraft(string Subject, string Body, string Provider, string? Model, MlChecks Checks, string? FallbackReason);
    public record MlLlmHealth(string? Provider, string? Model, bool Available, string? Error);
    public record MlDataHealth(bool Loaded, int? ClientBrands, string? ModelVersion, string? Error);
    public record MlHealth(string Status, MlDataHealth Data, MlLlmHealth Llm);

    /// <summary>Typed HttpClient for ml-service. The rest of the API never knows the model runs in Python.</summary>
    public class MlServiceClient
    {
        private static readonly JsonSerializerOptions Json = new()
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            PropertyNameCaseInsensitive = true,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        };

        private readonly HttpClient _http;
        public MlServiceClient(HttpClient http) => _http = http;

        public Task<MlHealth?> HealthAsync(CancellationToken ct = default) => GetAsync<MlHealth>("health", ct);

        public Task<List<MlBrand>?> BrandsAsync(CancellationToken ct = default) => GetAsync<List<MlBrand>>("brands", ct);

        public Task<MlCreator?> CreatorAsync(string creatorId, CancellationToken ct = default) =>
            GetAsync<MlCreator>($"creators/{Uri.EscapeDataString(creatorId)}", ct);

        public Task<MlRecommendations?> RecommendAsync(string brand, int k, int? minFollowers, int? maxFollowers,
                                                       string? niche, IEnumerable<string> exclude, CancellationToken ct = default)
        {
            var q = new List<string> { $"k={k}" };
            if (minFollowers.HasValue) q.Add($"min_followers={minFollowers}");
            if (maxFollowers.HasValue) q.Add($"max_followers={maxFollowers}");
            if (!string.IsNullOrWhiteSpace(niche)) q.Add($"niche={Uri.EscapeDataString(niche)}");
            var ex = string.Join(",", exclude);
            if (ex.Length > 0) q.Add($"exclude={Uri.EscapeDataString(ex)}");
            return GetAsync<MlRecommendations>($"brands/{Uri.EscapeDataString(brand)}/recommendations?{string.Join("&", q)}", ct);
        }

        public async Task<MlDraft> DraftAsync(object request, CancellationToken ct = default)
        {
            try
            {
                var r = await _http.PostAsJsonAsync("outreach/draft", request, Json, ct);
                if (!r.IsSuccessStatusCode)
                    throw new MlServiceUnavailableException($"ml-service returned {(int)r.StatusCode}: {await r.Content.ReadAsStringAsync(ct)}");
                return (await r.Content.ReadFromJsonAsync<MlDraft>(Json, ct))!;
            }
            catch (Exception e) when (e is HttpRequestException or TaskCanceledException)
            {
                throw Unavailable(e, ct);
            }
        }

        // A refused connection means the service is not running; a timeout means it is running but slow
        // (usually the LLM). The two need different fixes, so they get different messages.
        private MlServiceUnavailableException Unavailable(Exception e, CancellationToken ct) =>
            e is TaskCanceledException && !ct.IsCancellationRequested
                ? new MlServiceUnavailableException(
                    $"ml-service did not answer within {_http.Timeout.TotalSeconds:0} s. The LLM is probably slow or unreachable; " +
                    "check the ML service terminal.", e)
                : new MlServiceUnavailableException(
                    $"ml-service is not reachable at {_http.BaseAddress}. Start it with: uvicorn app.main:app --port 8000", e);

        private async Task<T?> GetAsync<T>(string path, CancellationToken ct)
        {
            try
            {
                var r = await _http.GetAsync(path, ct);
                if (r.StatusCode == HttpStatusCode.NotFound) return default;
                if (!r.IsSuccessStatusCode)
                    throw new MlServiceUnavailableException($"ml-service returned {(int)r.StatusCode}: {await r.Content.ReadAsStringAsync(ct)}");
                return await r.Content.ReadFromJsonAsync<T>(Json, ct);
            }
            catch (Exception e) when (e is HttpRequestException or TaskCanceledException)
            {
                throw Unavailable(e, ct);
            }
        }
    }
}
