using MusicEventManagementSystem.API.DTOs.MediaCampaign;

namespace MusicEventManagementSystem.API.Services.IService
{
    public interface ICampaignService
    {
        Task<IEnumerable<CampaignResponseDto>> GetAllCampaignsAsync();
        Task<CampaignResponseDto?> GetCampaignByIdAsync(int id);
        Task<CampaignResponseDto> CreateCampaignAsync(CampaignCreateDto createDto);
        Task<CampaignResponseDto?> UpdateCampaignAsync(int id, CampaignUpdateDto updateDto);
        Task<bool> DeleteCampaignAsync(int id);

        Task<IEnumerable<CampaignResponseDto>> GetByBrandIdAsync(int brandId);
        Task<IEnumerable<CampaignResponseDto>> GetByNameAsync(string name);
        Task<IEnumerable<CampaignResponseDto>> GetByStartDateAsync(DateTime startDate);
        Task<IEnumerable<CampaignResponseDto>> GetByEndDateAsync(DateTime endDate);
        Task<IEnumerable<CampaignResponseDto>> GetByTotalBudgetAsync(decimal totalBudget);
    }
}