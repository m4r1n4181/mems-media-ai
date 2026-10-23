using MusicEventManagementSystem.API.Models;

namespace MusicEventManagementSystem.API.Repositories.IRepositories
{
    public interface ICampaignRepository : IRepository<Campaign>
    {
        Task<IEnumerable<Campaign>> GetByBrandIdAsync(int brandId);
        Task<IEnumerable<Campaign>> GetByNameAsync(string name);
        Task<IEnumerable<Campaign>> GetByStartDateAsync(DateTime startDate);
        Task<IEnumerable<Campaign>> GetByEndDateAsync(DateTime endDate);
        Task<IEnumerable<Campaign>> GetByTotalBudgetAsync(decimal totalBudget);
    }
}