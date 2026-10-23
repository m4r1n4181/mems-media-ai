using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using MusicEventManagementSystem.API.DTOs.Marketing;
using MusicEventManagementSystem.API.Models;
using MusicEventManagementSystem.API.Services.Marketing;
using MusicEventManagementSystem.Data;

namespace MusicEventManagementSystem.API.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class BrandsController : ControllerBase
    {
        private readonly ApplicationDbContext _db;
        private readonly MlServiceClient _ml;

        public BrandsController(ApplicationDbContext db, MlServiceClient ml)
        {
            _db = db; _ml = ml;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<BrandDto>>> GetAll()
        {
            var brands = await _db.Brands.Where(b => b.IsClient).Include(b => b.Campaigns)
                                  .OrderBy(b => b.DisplayName).ToListAsync();
            return brands.Select(ToDto).ToList();
        }

        [HttpGet("{id:int}")]
        public async Task<ActionResult<BrandDto>> Get(int id)
        {
            var b = await _db.Brands.Include(x => x.Campaigns).FirstOrDefaultAsync(x => x.BrandId == id);
            return b == null ? NotFound() : ToDto(b);
        }

        /// <summary>Brands the recommender knows: the choices for "similar brands" of a new client.</summary>
        [HttpGet("known")]
        public async Task<ActionResult<IEnumerable<KnownBrandDto>>> Known()
        {
            try
            {
                var brands = await _ml.BrandsAsync() ?? new List<MlBrand>();
                return brands.OrderBy(b => b.Brand).Select(b => new KnownBrandDto
                {
                    Handle = b.Brand, Niche = b.Niche, Followers = b.Followers, IsClient = b.IsClient,
                }).ToList();
            }
            catch (MlServiceUnavailableException e) { return StatusCode(503, new { message = e.Message }); }
        }

        /// <summary>Add a client brand. If the recommender knows the handle, its data and recommendations are used;
        /// otherwise 1–5 similar known brands are required (cold start).</summary>
        [HttpPost]
        public async Task<ActionResult<BrandDto>> Create(CreateBrandDto dto)
        {
            var handle = BrandRules.NormalizeHandle(dto.Handle);
            if (handle == null)
                return BadRequest(new { message = "Enter the brand's Instagram handle: letters, numbers, dots and underscores." });
            if (await _db.Brands.AnyAsync(b => b.Handle == handle))
                return Conflict(new { message = $"@{handle} is already a client." });

            var similar = dto.SimilarBrands.Select(BrandRules.NormalizeHandle).Where(h => h != null && h != handle)
                             .Select(h => h!).Distinct().ToList();
            if (similar.Count > BrandRules.MaxSimilarBrands)
                return BadRequest(new { message = $"Choose at most {BrandRules.MaxSimilarBrands} similar brands." });

            MlBrand? known;
            List<MlBrand> all;
            try
            {
                known = await _ml.BrandAsync(handle);
                all = similar.Count > 0 ? await _ml.BrandsAsync() ?? new List<MlBrand>() : new List<MlBrand>();
            }
            catch (MlServiceUnavailableException e) { return StatusCode(503, new { message = e.Message }); }

            var unknownSimilar = similar.Where(s => all.All(b => b.Brand != s)).ToList();
            if (unknownSimilar.Count > 0)
                return BadRequest(new { message = $"The recommender does not know: {string.Join(", ", unknownSimilar.Select(s => "@" + s))}." });
            if (known == null && similar.Count == 0)
                return BadRequest(new { message = $"The recommender does not know @{handle}. Choose 1–5 similar brands it knows, so it can suggest creators." });

            var brand = new Brand
            {
                Handle = handle,
                DisplayName = string.IsNullOrWhiteSpace(dto.DisplayName) ? handle : dto.DisplayName.Trim(),
                Niche = string.IsNullOrWhiteSpace(dto.Niche) ? known?.Niche : dto.Niche.Trim(),
                Followers = dto.Followers ?? known?.Followers ?? 0,
                TypicalPartnerFollowers = dto.TypicalPartnerFollowers ?? known?.TypicalPartnerFollowers,
                IsClient = true,
                KnownToModel = known != null,
                SimilarBrands = similar.Count > 0 ? string.Join(",", similar) : null,
            };
            _db.Brands.Add(brand);
            await _db.SaveChangesAsync();
            return CreatedAtAction(nameof(Get), new { id = brand.BrandId }, ToDto(brand));
        }

        private static BrandDto ToDto(Brand b) => new()
        {
            BrandId = b.BrandId, Handle = b.Handle, DisplayName = b.DisplayName, Niche = b.Niche,
            Followers = b.Followers, TypicalPartnerFollowers = b.TypicalPartnerFollowers,
            CampaignCount = b.Campaigns.Count, KnownToModel = b.KnownToModel,
            SimilarBrands = BrandRules.SplitSimilar(b.SimilarBrands),
        };
    }
}
