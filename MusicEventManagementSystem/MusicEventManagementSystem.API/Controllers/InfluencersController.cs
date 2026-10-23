using Microsoft.AspNetCore.Mvc;
using MusicEventManagementSystem.API.DTOs.Marketing;
using MusicEventManagementSystem.API.Services.Marketing;

namespace MusicEventManagementSystem.API.Controllers
{
    /// <summary>Influencer marketing inside a campaign: recommendations, selection, AI e-mail drafts, sending, answers.</summary>
    [Route("api")]
    [ApiController]
    public class InfluencersController : ControllerBase
    {
        private readonly IInfluencerService _svc;
        public InfluencersController(IInfluencerService svc) => _svc = svc;

        [HttpGet("campaigns/{campaignId:int}/influencers")]
        public Task<IActionResult> List(int campaignId) => Run(() => _svc.ListAsync(campaignId));

        [HttpPost("campaigns/{campaignId:int}/influencers/suggest")]
        public Task<IActionResult> Suggest(int campaignId, [FromBody] SuggestRequestDto req) =>
            Run(() => _svc.SuggestAsync(campaignId, req));

        [HttpPost("campaign-influencers/{id:int}/{op:regex(^(select|unselect|dismiss)$)}")]
        public Task<IActionResult> ChangeStatus(int id, string op) => Run(() => _svc.ChangeStatusAsync(id, op));

        [HttpPost("campaign-influencers/{id:int}/draft-email")]
        public Task<IActionResult> Draft(int id, [FromBody] SenderDto sender) => Run(() => _svc.DraftEmailAsync(id, sender));

        [HttpPost("campaign-influencers/{id:int}/send-email")]
        public Task<IActionResult> Send(int id, [FromBody] SendEmailRequestDto req) => Run(() => _svc.SendEmailAsync(id, req));

        [HttpPost("campaign-influencers/{id:int}/response")]
        public Task<IActionResult> Response(int id, [FromBody] ResponseRequestDto req) =>
            Run(() => _svc.RecordResponseAsync(id, req));

        [HttpGet("creators/{creatorId}")]
        public async Task<IActionResult> Creator(string creatorId)
        {
            try
            {
                var c = await _svc.GetCreatorAsync(creatorId);
                return c == null ? NotFound(new { message = $"Creator {creatorId} not found." }) : Ok(c);
            }
            catch (MlServiceUnavailableException e) { return StatusCode(503, new { message = e.Message }); }
        }

        [HttpGet("ai/status")]
        public async Task<IActionResult> AiStatus() => Ok(await _svc.GetAiStatusAsync());

        private async Task<IActionResult> Run<T>(Func<Task<T>> action)
        {
            try { return Ok(await action()); }
            catch (NotFoundException e) { return NotFound(new { message = e.Message }); }
            catch (InvalidStateException e) { return BadRequest(new { message = e.Message }); }
            catch (MlServiceUnavailableException e) { return StatusCode(503, new { message = e.Message }); }
            catch (System.Net.Mail.SmtpException e)
            {
                return StatusCode(502, new { message = $"The e-mail could not be sent: {e.Message}" });
            }
        }
    }
}
