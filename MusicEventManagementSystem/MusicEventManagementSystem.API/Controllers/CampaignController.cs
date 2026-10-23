using Microsoft.AspNetCore.Mvc;
using MusicEventManagementSystem.API.DTOs.MediaCampaign;
using MusicEventManagementSystem.API.Services.IService;

namespace MusicEventManagementSystem.API.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class CampaignController : ControllerBase
    {
        private readonly ICampaignService _campaignService;

        public CampaignController(ICampaignService campaignService)
        {
            _campaignService = campaignService;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<CampaignResponseDto>>> GetAllCampaigns()
        {
            var campaigns = await _campaignService.GetAllCampaignsAsync();
            return Ok(campaigns);
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<CampaignResponseDto>> GetCampaignById(int id)
        {
            var campaign = await _campaignService.GetCampaignByIdAsync(id);
            if (campaign == null)
                return NotFound($"Campaign with ID {id} not found.");
            return Ok(campaign);
        }

        [HttpPost]
        public async Task<ActionResult<CampaignResponseDto>> CreateCampaign([FromBody] CampaignCreateDto dto)
        {
            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            var createdCampaign = await _campaignService.CreateCampaignAsync(dto);
            return CreatedAtAction(nameof(GetCampaignById), new { id = createdCampaign.CampaignId }, createdCampaign);
        }

        [HttpPut("{id}")]
        public async Task<ActionResult<CampaignResponseDto>> UpdateCampaign(int id, [FromBody] CampaignUpdateDto dto)
        {
            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            var updatedCampaign = await _campaignService.UpdateCampaignAsync(id, dto);
            if (updatedCampaign == null)
                return NotFound($"Campaign with ID {id} not found.");
            return Ok(updatedCampaign);
        }

        [HttpDelete("{id}")]
        public async Task<ActionResult> DeleteCampaign(int id)
        {
            var isDeleted = await _campaignService.DeleteCampaignAsync(id);
            if (!isDeleted)
                return NotFound($"Campaign with ID {id} not found.");
            return NoContent();
        }

        [HttpGet("brandId/{brandId}")]
        public async Task<ActionResult<IEnumerable<CampaignResponseDto>>> GetByBrandId(int brandId)
        {
            var campaigns = await _campaignService.GetByBrandIdAsync(brandId);
            return Ok(campaigns);
        }

        [HttpGet("name/{name}")]
        public async Task<ActionResult<IEnumerable<CampaignResponseDto>>> GetByName(string name)
        {
            var campaigns = await _campaignService.GetByNameAsync(name);
            return Ok(campaigns);
        }

        [HttpGet("startDate/{startDate}")]
        public async Task<ActionResult<IEnumerable<CampaignResponseDto>>> GetByStartDate(DateTime startDate)
        {
            var campaigns = await _campaignService.GetByStartDateAsync(startDate);
            return Ok(campaigns);
        }

        [HttpGet("endDate/{endDate}")]
        public async Task<ActionResult<IEnumerable<CampaignResponseDto>>> GetByEndDate(DateTime endDate)
        {
            var campaigns = await _campaignService.GetByEndDateAsync(endDate);
            return Ok(campaigns);
        }

        [HttpGet("totalBudget/{totalBudget}")]
        public async Task<ActionResult<IEnumerable<CampaignResponseDto>>> GetByTotalBudget(decimal totalBudget)
        {
            var campaigns = await _campaignService.GetByTotalBudgetAsync(totalBudget);
            return Ok(campaigns);
        }
    }
}