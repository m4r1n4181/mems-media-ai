using System.ComponentModel.DataAnnotations;
using MusicEventManagementSystem.API.DTOs.MediaCampaign;

namespace MusicEventManagementSystem.API.DTOs.MediaCampaign
{
    public class CampaignResponseDto
    {
        public int CampaignId { get; set; }
        public int? BrandId { get; set; }
        public string? BrandHandle { get; set; }
        public string Name { get; set; }
        public string? Brief { get; set; }
        public DateTime StartDate { get; set; }
        public DateTime EndDate { get; set; }
        public decimal TotalBudget { get; set; }
        public ICollection<int>? AdIds { get; set; }
    }

    public class CampaignCreateDto
    {
        [Required]
        public int BrandId { get; set; }

        [Required]
        [StringLength(200)]
        public string Name { get; set; }

        [StringLength(2000)]
        public string? Brief { get; set; }

        [Required]
        public DateTime StartDate { get; set; }

        [Required]
        public DateTime EndDate { get; set; }

        [Required]
        [Range(0, double.MaxValue)]
        public decimal TotalBudget { get; set; }

    }

    public class CampaignUpdateDto
    {
        public int? BrandId { get; set; }

        [StringLength(200)]
        public string? Name { get; set; }

        [StringLength(2000)]
        public string? Brief { get; set; }

        public DateTime? StartDate { get; set; }
        public DateTime? EndDate { get; set; }
        [Range(0, double.MaxValue)]
        public decimal? TotalBudget { get; set; }
        [Range(0, 100)]
        public ICollection<int>? AdIds { get; set; }    
    }
}