using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using MusicEventManagementSystem.API.Data;
using MusicEventManagementSystem.API.Repositories;
using MusicEventManagementSystem.API.Repositories.IRepositories;
using MusicEventManagementSystem.API.Services;
using MusicEventManagementSystem.API.Services.IService;
using MusicEventManagementSystem.API.Services.Marketing;
using MusicEventManagementSystem.Data;
using MusicEventManagementSystem.Models.Auth;
using MusicEventManagementSystem.Services.Auth;
using System.Text.Json.Serialization;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.

// 1. DbContext with PostgreSQL
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

// 2. Identity setup
builder.Services.AddIdentity<ApplicationUser, IdentityRole>(options =>
{
    options.Password.RequireDigit = true;
    options.Password.RequiredLength = 6;
    options.User.RequireUniqueEmail = true;
}).AddEntityFrameworkStores<ApplicationDbContext>()
  .AddDefaultTokenProviders();

// 3. Add CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowReactApp", policy =>
    {
        policy.WithOrigins("http://localhost:5173", "https://localhost:5173", "https://localhost:7050")
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials()
              .SetIsOriginAllowed(_ => true);
    });
});

// 4. Register repositories for Ticket-Sales Subsystem
builder.Services.AddScoped<IVenueRepository, VenueRepository>();
builder.Services.AddScoped<ISegmentRepository, SegmentRepository>();
builder.Services.AddScoped<IZoneRepository, ZoneRepository>();
builder.Services.AddScoped<ISpecialOfferRepository, SpecialOfferRepository>();
builder.Services.AddScoped<ITicketTypeRepository, TicketTypeRepository>();
builder.Services.AddScoped<ITicketRepository, TicketRepository>();
builder.Services.AddScoped<IRecordedSaleRepository, RecordedSaleRepository>();
builder.Services.AddScoped<IPricingRuleRepository, PricingRuleRepository>();
builder.Services.AddScoped<IEventRepository, EventRepository>();
builder.Services.AddScoped<IResourceRepository, ResourceRepository>();
builder.Services.AddScoped<IPerformanceRepository, PerformanceRepository>();
builder.Services.AddScoped<IEquipmentRepository, EquipmentRepository>();
builder.Services.AddScoped<ILocationRepository, LocationRepository>();
builder.Services.AddScoped<IWorkTaskRepository, WorkTaskRepository>();
builder.Services.AddScoped<IPerformerRepository, PerformerRepository>();
builder.Services.AddScoped<IVehicleRepository, VehicleRepository>();
builder.Services.AddScoped<IServiceRepository, ServiceRepository>();
builder.Services.AddScoped<IInfrastructureRepository, InfrastructureRepository>();
builder.Services.AddScoped<IStaffRepository, StaffRepository>();
builder.Services.AddScoped<IPerformanceResourceRepository, PerformanceResourceRepository>();

// 5. Register Media Campaign repositories
builder.Services.AddScoped<ICampaignRepository, CampaignRepository>();
builder.Services.AddScoped<IAdTypeRepository, AdTypeRepository>();
builder.Services.AddScoped<IMediaWorkflowRepository, MediaWorkflowRepository>();
builder.Services.AddScoped<IMediaTaskRepository, MediaTaskRepository>();
builder.Services.AddScoped<IAdRepository, AdRepository>();
builder.Services.AddScoped<IMediaVersionRepository, MediaVersionRepository>();
builder.Services.AddScoped<IMediaChannelRepository, MediaChannelRepository>();
builder.Services.AddScoped<IIntegrationStatusRepository, IntegrationStatusRepository>();
builder.Services.AddScoped<IApprovalRepository, ApprovalRepository>();


// 6. Register services for Ticket-sales Subsystem
// Performer subsystem repositories
builder.Services.AddScoped<IPerformerRepository, PerformerRepository>();
builder.Services.AddScoped<IRequirementRepository, RequirementRepository>();
builder.Services.AddScoped<IPhaseRepository, PhaseRepository>();
builder.Services.AddScoped<INegotiationRepository, NegotiationRepository>();
builder.Services.AddScoped<IContractRepository, ContractRepository>();
builder.Services.AddScoped<IDocumentRepository, DocumentRepository>();
builder.Services.AddScoped<ICommunicationRepository, CommunicationRepository>();

// 5. Register services
builder.Services.AddScoped<IAuthService, AuthService>();
builder.Services.AddScoped<IVenueService, VenueService>();
builder.Services.AddScoped<ISegmentService, SegmentService>();
builder.Services.AddScoped<IZoneService, ZoneService>();
builder.Services.AddScoped<ISpecialOfferService, SpecialOfferService>();
builder.Services.AddScoped<ITicketTypeService, TicketTypeService>();
builder.Services.AddScoped<ITicketService, TicketService>();
builder.Services.AddScoped<IRecordedSaleService, RecordedSaleService>();
builder.Services.AddScoped<IPricingRuleService, PricingRuleService>();
builder.Services.AddScoped<IEventService, EventService>();
builder.Services.AddScoped<IResourceService, ResourceService>();
builder.Services.AddScoped<IPerformanceService, PerformanceService>();
builder.Services.AddScoped<IEquipmentService, EquipmentService>();
builder.Services.AddScoped<ILocationService, LocationService>();
builder.Services.AddScoped<IWorkTaskService, WorkTaskService>();
builder.Services.AddScoped<IPerformerService, PerformerService>();
builder.Services.AddScoped<IVehicleService, VehicleService>();
builder.Services.AddScoped<IServiceService, ServiceService>();
builder.Services.AddScoped<IInfrastructureService, InfrastructureService>();
builder.Services.AddScoped<IStaffService, StaffService>();
builder.Services.AddScoped<IPerformanceResourceService, PerformanceResourceService>();

// 8. Register Media Campaign services
builder.Services.AddScoped<ICampaignService, CampaignService>();

// Influencer marketing: ml-service client, e-mail sending, outreach workflow
builder.Services.Configure<MlServiceOptions>(builder.Configuration.GetSection("MlService"));
builder.Services.Configure<EmailOptions>(builder.Configuration.GetSection("Email"));
builder.Services.Configure<AgencyOptions>(builder.Configuration.GetSection("Agency"));
builder.Services.AddHttpClient<MlServiceClient>((sp, http) =>
{
    var opt = builder.Configuration.GetSection("MlService").Get<MlServiceOptions>() ?? new MlServiceOptions();
    http.BaseAddress = new Uri(opt.BaseUrl.TrimEnd('/') + "/");
    http.Timeout = TimeSpan.FromSeconds(opt.TimeoutSeconds);
});
builder.Services.AddScoped<IEmailSender, EmailSender>();
builder.Services.AddScoped<IInfluencerService, InfluencerService>();
builder.Services.AddScoped<IAdTypeService, AdTypeService>();
builder.Services.AddScoped<IMediaWorkflowService, MediaWorkflowService>();
builder.Services.AddScoped<IMediaTaskService, MediaTaskService>();
builder.Services.AddScoped<IAdService, AdService>();
builder.Services.AddScoped<IMediaVersionService, MediaVersionService>();
builder.Services.AddScoped<IMediaChannelService, MediaChannelService>();
builder.Services.AddScoped<IIntegrationStatusService, IntegrationStatusService>();
builder.Services.AddScoped<IApprovalService, ApprovalService>();

builder.Services.AddControllers();

// Performer subsystem services
builder.Services.AddScoped<IPerformerService, PerformerService>();
builder.Services.AddScoped<IRequirementService, RequirementService>();
builder.Services.AddScoped<IPhaseService, PhaseService>();
builder.Services.AddScoped<INegotiationService, NegotiationService>();
builder.Services.AddScoped<IContractService, ContractService>();
builder.Services.AddScoped<IDocumentService, DocumentService>();
builder.Services.AddScoped<ICommunicationService, CommunicationService>();

// Configure JSON serialization options to handle circular references
builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.ReferenceHandler = ReferenceHandler.IgnoreCycles;
    options.SerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
});

// Configure controllers with JSON options
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.ReferenceHandler = ReferenceHandler.IgnoreCycles;
        options.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
    });

// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Seeding Database
using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
    try
    {
        // Do migrations first
        context.Database.Migrate();

        // Seed data
        await DatabaseSeeder.SeedAsync(context);

        // Client brands for the marketing app; also gives old event campaigns a brand
        var marketingLogger = scope.ServiceProvider.GetRequiredService<ILogger<Program>>();
        await MarketingSeeder.SeedAsync(context, app.Environment.ContentRootPath, marketingLogger);
    }
    catch (Exception ex)
    {
        var logger = scope.ServiceProvider.GetRequiredService<ILogger<Program>>();
        logger.LogError(ex, "An error occurred while seeding the database.");
    }
}

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors("AllowReactApp"); // Move CORS before HTTPS redirection

app.UseHttpsRedirection();

app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

app.Run();