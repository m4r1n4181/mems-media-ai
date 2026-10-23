using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using MusicEventManagementSystem.API.DTOs.Marketing;
using MusicEventManagementSystem.Data;

namespace MusicEventManagementSystem.API.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class BrandsController : ControllerBase
    {
        private readonly ApplicationDbContext _db;
        public BrandsController(ApplicationDbContext db) => _db = db;

        [HttpGet]
        public async Task<ActionResult<IEnumerable<BrandDto>>> GetAll() =>
            await _db.Brands.Where(b => b.IsClient).OrderBy(b => b.DisplayName).Select(b => new BrandDto
            {
                BrandId = b.BrandId, Handle = b.Handle, DisplayName = b.DisplayName, Niche = b.Niche,
                Followers = b.Followers, TypicalPartnerFollowers = b.TypicalPartnerFollowers,
                CampaignCount = b.Campaigns.Count,
            }).ToListAsync();

        [HttpGet("{id:int}")]
        public async Task<ActionResult<BrandDto>> Get(int id)
        {
            var b = await _db.Brands.Include(x => x.Campaigns).FirstOrDefaultAsync(x => x.BrandId == id);
            if (b == null) return NotFound();
            return new BrandDto
            {
                BrandId = b.BrandId, Handle = b.Handle, DisplayName = b.DisplayName, Niche = b.Niche,
                Followers = b.Followers, TypicalPartnerFollowers = b.TypicalPartnerFollowers, CampaignCount = b.Campaigns.Count,
            };
        }
    }
}
