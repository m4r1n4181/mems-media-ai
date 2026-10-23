using Microsoft.EntityFrameworkCore;
using MusicEventManagementSystem.API.Enums.TicketSales;
using MusicEventManagementSystem.API.Models;
using MusicEventManagementSystem.Data;
using MusicEventManagementSystem.Enums;
using MusicEventManagementSystem.Models.Auth;

namespace MusicEventManagementSystem.API.Data
{
    public static class DatabaseSeeder
    {
        public static async Task SeedAsync(ApplicationDbContext context)
        {
            // Checking if dataa aleady exists
            if (context.Venues.Any())
            {
                return; // If its already seeded return
            }

            // 1. Seed ApplicationUsers
            var applicationUsers = new List<ApplicationUser>
            {
                new ApplicationUser
                {
                    Id = Guid.NewGuid().ToString(),
                    UserName = "savo@ticketsales.com",
                    Email = "savo@ticketsales.com",
                    FirstName = "Savo",
                    LastName = "Savić",
                    PhoneNumber = "+381641234568",
                    Department = Department.TicketSales,
                    EmailConfirmed = true
                },
                new ApplicationUser
                {
                    Id = Guid.NewGuid().ToString(),
                    UserName = "tijana@eventorganization.com",
                    Email = "tijana@eventorganization.com",
                    FirstName = "Tijana",
                    LastName = "Lazić",
                    PhoneNumber = "+381641234568",
                    Department = Department.EventOrganization,
                    EmailConfirmed = true
                },
                new ApplicationUser
                {
                    Id = Guid.NewGuid().ToString(),
                    UserName = "marina@mediacampaign.com",
                    Email = "marina@mediacampaign.com",
                    FirstName = "Marina",
                    LastName = "Khan",
                    PhoneNumber = "+381641234569",
                    Department = Department.MediaCampaign,
                    EmailConfirmed = true
                },
                new ApplicationUser
                {
                    Id = Guid.NewGuid().ToString(),
                    UserName = "milos@artistcommunication.com",
                    Email = "milos@artistcommunication.com",
                    FirstName = "Milos",
                    LastName = "Trivković",
                    PhoneNumber = "+381641234570",
                    Department = Department.ArtistCommunication,
                    EmailConfirmed = true
                },
                new ApplicationUser
                {
                    Id = Guid.NewGuid().ToString(),
                    UserName = "stefan@mediacampaign.com",
                    Email = "stefan@mediacampaign.com",
                    FirstName = "Stefan",
                    LastName = "Pavlović",
                    PhoneNumber = "+381641234571",
                    Department = Department.MediaCampaign,
                    EmailConfirmed = true
                }
            };
            context.Users.AddRange(applicationUsers);
            await context.SaveChangesAsync();

            // 1. Seed Venues
            var venues = new List<Venue>
            {
                new Venue
                {
                    Name = "Belgrade Arena",
                    Description = "Serbia's largest indoor arena for major concerts and events",
                    City = "Belgrade",
                    Address = "Bulevar Arsenija Čarnojevića 58",
                    Capacity = 20000,
                    VenueType = VenueType.Arena
                },
                new Venue
                {
                    Name = "Youth Center Belgrade",
                    Description = "Cultural center for intimate performances and indie shows",
                    City = "Belgrade",
                    Address = "Makedonska 22-24",
                    Capacity = 1500,
                    VenueType = VenueType.Club
                },
                new Venue
                {
                    Name = "Stark Arena",
                    Description = "Modern multifunctional arena for sports and entertainment",
                    City = "Belgrade",
                    Address = "Bulevar Milutina Milankovića",
                    Capacity = 18400,
                    VenueType = VenueType.Arena
                },
                new Venue
                {
                    Name = "Exit Festival Main Stage",
                    Description = "Main stage of the famous Exit Festival",
                    City = "Novi Sad",
                    Address = "Petrovaradin Fortress",
                    Capacity = 40000,
                    VenueType = VenueType.Stadium
                },
                new Venue
                {
                    Name = "Sava Center",
                    Description = "Premier convention and concert venue in Belgrade",
                    City = "Belgrade",
                    Address = "Milentija Popovića 9",
                    Capacity = 4000,
                    VenueType = VenueType.Theater
                },
                new Venue
                {
                    Name = "Nisville Jazz Stage",
                    Description = "Outdoor stage for jazz and world music festival",
                    City = "Niš",
                    Address = "Niš Fortress",
                    Capacity = 8000,
                    VenueType = VenueType.Outdoor
                },
                new Venue
                {
                    Name = "Tašmajdan Stadium",
                    Description = "Historic stadium for large outdoor concerts",
                    City = "Belgrade",
                    Address = "Takovska 6",
                    Capacity = 35000,
                    VenueType = VenueType.Stadium
                },
                new Venue
                {
                    Name = "Drugstore Club",
                    Description = "Underground club for electronic music events",
                    City = "Belgrade",
                    Address = "Svetogorska 6",
                    Capacity = 800,
                    VenueType = VenueType.Club
                }
            };
            context.Venues.AddRange(venues);
            await context.SaveChangesAsync();

            // 2. Seed Segments
            var segments = new List<Segment>
            {
                // Belgrade Arena segments
                new Segment { Name = "Floor Standing", Description = "Main floor standing area", Capacity = 8000, SegmentType = SegmentType.Standing, VenueId = 1 },
                new Segment { Name = "West Tribune", Description = "Western seated section", Capacity = 4000, SegmentType = SegmentType.Seated, VenueId = 1 },
                new Segment { Name = "East Tribune", Description = "Eastern seated section", Capacity = 4000, SegmentType = SegmentType.Seated, VenueId = 1 },
                new Segment { Name = "North Tribune", Description = "Northern seated section", Capacity = 2000, SegmentType = SegmentType.Seated, VenueId = 1 },
                new Segment { Name = "South Tribune", Description = "Southern seated section", Capacity = 2000, SegmentType = SegmentType.Seated, VenueId = 1 },
                
                // Youth Center segments
                new Segment { Name = "Main Hall", Description = "Main hall of Youth Center", Capacity = 1500, SegmentType = SegmentType.Standing, VenueId = 2 },
                
                // Stark Arena segments
                new Segment { Name = "Floor Area", Description = "Main floor area", Capacity = 7000, SegmentType = SegmentType.Standing, VenueId = 3 },
                new Segment { Name = "Lower Bowl", Description = "Lower bowl seating", Capacity = 6000, SegmentType = SegmentType.Seated, VenueId = 3 },
                new Segment { Name = "Upper Bowl", Description = "Upper bowl seating", Capacity = 5400, SegmentType = SegmentType.Seated, VenueId = 3 },
                
                // Exit Festival segments
                new Segment { Name = "Main Stage Area", Description = "Main stage festival grounds", Capacity = 40000, SegmentType = SegmentType.Standing, VenueId = 4 },
                
                // Sava Center segments
                new Segment { Name = "Orchestra", Description = "Orchestra level seating", Capacity = 2000, SegmentType = SegmentType.Seated, VenueId = 5 },
                new Segment { Name = "Balcony", Description = "Balcony level seating", Capacity = 2000, SegmentType = SegmentType.Seated, VenueId = 5 },
                
                // Nisville segments
                new Segment { Name = "Festival Ground", Description = "Open air festival area", Capacity = 8000, SegmentType = SegmentType.Standing, VenueId = 6 },
                
                // Tašmajdan segments
                new Segment { Name = "Stadium Field", Description = "Main stadium field", Capacity = 25000, SegmentType = SegmentType.Standing, VenueId = 7 },
                new Segment { Name = "Stadium Seats", Description = "Stadium seating areas", Capacity = 10000, SegmentType = SegmentType.Seated, VenueId = 7 },
                
                // Drugstore segments
                new Segment { Name = "Club Floor", Description = "Main club dance floor", Capacity = 800, SegmentType = SegmentType.Standing, VenueId = 8 }
            };
            context.Segments.AddRange(segments);
            await context.SaveChangesAsync();

            // 3. Seed Zones
            var zones = new List<Zone>
            {
                // Belgrade Arena zones
                new Zone { Name = "Floor Front", Description = "Front section of the floor", Capacity = 3000, BasePrice = 8000, Position = ZonePosition.Front, SegmentId = 1 },
                new Zone { Name = "Floor Back", Description = "Back section of the floor", Capacity = 5000, BasePrice = 6500, Position = ZonePosition.Back, SegmentId = 1 },
                new Zone { Name = "West Lower", Description = "Lower west tribune", Capacity = 2000, BasePrice = 5500, Position = ZonePosition.Lower, SegmentId = 2 },
                new Zone { Name = "West Upper", Description = "Upper west tribune", Capacity = 2000, BasePrice = 4500, Position = ZonePosition.Upper, SegmentId = 2 },
                new Zone { Name = "East Lower", Description = "Lower east tribune", Capacity = 2000, BasePrice = 5500, Position = ZonePosition.Lower, SegmentId = 3 },
                new Zone { Name = "East Upper", Description = "Upper east tribune", Capacity = 2000, BasePrice = 4500, Position = ZonePosition.Upper, SegmentId = 3 },
                new Zone { Name = "North Section", Description = "North tribune seating", Capacity = 2000, BasePrice = 4000, Position = ZonePosition.Left, SegmentId = 4 },
                new Zone { Name = "South Section", Description = "South tribune seating", Capacity = 2000, BasePrice = 4000, Position = ZonePosition.Right, SegmentId = 5 },
                
                // Youth Center zones
                new Zone { Name = "Front Area", Description = "Close to stage area", Capacity = 500, BasePrice = 3500, Position = ZonePosition.Front, SegmentId = 6 },
                new Zone { Name = "Middle Area", Description = "Middle section of the hall", Capacity = 700, BasePrice = 3000, Position = ZonePosition.Center, SegmentId = 6 },
                new Zone { Name = "Back Area", Description = "Rear section of the hall", Capacity = 300, BasePrice = 2500, Position = ZonePosition.Back, SegmentId = 6 },
                
                // Stark Arena zones
                new Zone { Name = "Golden Circle", Description = "VIP standing area", Capacity = 1000, BasePrice = 12000, Position = ZonePosition.Front, SegmentId = 7 },
                new Zone { Name = "General Floor", Description = "General admission floor", Capacity = 6000, BasePrice = 7000, Position = ZonePosition.Center, SegmentId = 7 },
                new Zone { Name = "Lower Bowl Seats", Description = "Premium lower seating", Capacity = 6000, BasePrice = 6000, Position = ZonePosition.Lower, SegmentId = 8 },
                new Zone { Name = "Upper Bowl Seats", Description = "Upper level seating", Capacity = 5400, BasePrice = 4500, Position = ZonePosition.Upper, SegmentId = 9 },
                
                // Exit Festival zones
                new Zone { Name = "Main Stage Front", Description = "Close to main stage", Capacity = 10000, BasePrice = 15000, Position = ZonePosition.Front, SegmentId = 10 },
                new Zone { Name = "Main Stage Center", Description = "Central festival area", Capacity = 25000, BasePrice = 12000, Position = ZonePosition.Center, SegmentId = 10 },
                new Zone { Name = "Main Stage Back", Description = "Back festival area", Capacity = 5000, BasePrice = 10000, Position = ZonePosition.Back, SegmentId = 10 },
                
                // Sava Center zones
                new Zone { Name = "Orchestra Premium", Description = "Premium orchestra seats", Capacity = 1000, BasePrice = 5000, Position = ZonePosition.Front, SegmentId = 11 },
                new Zone { Name = "Orchestra Standard", Description = "Standard orchestra seats", Capacity = 1000, BasePrice = 4000, Position = ZonePosition.Back, SegmentId = 11 },
                new Zone { Name = "Balcony Level", Description = "Balcony seating", Capacity = 2000, BasePrice = 3500, Position = ZonePosition.Balcony, SegmentId = 12 },
                
                // Nisville zones
                new Zone { Name = "Jazz Front", Description = "Front of jazz stage", Capacity = 2000, BasePrice = 4500, Position = ZonePosition.Front, SegmentId = 13 },
                new Zone { Name = "Jazz General", Description = "General admission area", Capacity = 6000, BasePrice = 3500, Position = ZonePosition.Center, SegmentId = 13 },
                
                // Tašmajdan zones
                new Zone { Name = "Stadium Floor", Description = "Main stadium floor", Capacity = 25000, BasePrice = 6000, Position = ZonePosition.Center, SegmentId = 14 },
                new Zone { Name = "Stadium Seats", Description = "Stadium seating", Capacity = 10000, BasePrice = 4500, Position = ZonePosition.Upper, SegmentId = 15 },
                
                // Drugstore zones
                new Zone { Name = "DJ Booth Area", Description = "Close to DJ booth", Capacity = 300, BasePrice = 2500, Position = ZonePosition.Front, SegmentId = 16 },
                new Zone { Name = "Dance Floor", Description = "Main dance area", Capacity = 500, BasePrice = 2000, Position = ZonePosition.Center, SegmentId = 16 }
            };
            context.Zones.AddRange(zones);
            await context.SaveChangesAsync();

            // 4. Seed Locations
            var locations = new List<Location>
            {
                new Location { Name = "Belgrade" },
                new Location { Name = "Novi Sad" },
                new Location { Name = "Niš" },
                new Location { Name = "Kragujevac" },
                new Location { Name = "Subotica" },
                new Location { Name = "Pančevo" },
                new Location { Name = "Čačak" },
                new Location { Name = "Užice" }
            };
            context.Locations.AddRange(locations);
            await context.SaveChangesAsync();

            // 5. Seed Events
            var events = new List<Event>
            {
                new Event
                {
                    Name = "Rock Legends Live",
                    Description = "International rock festival featuring legendary bands and emerging artists",
                    EventInterval = DateTime.UtcNow.AddMonths(2),
                    Status = EventStatus.Planned,
                    CreatedById = Guid.NewGuid(),
                    LocationId = 1,
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow
                },
                new Event
                {
                    Name = "Indie Discovery Night",
                    Description = "Showcase of the best indie and alternative artists from the region",
                    EventInterval = DateTime.UtcNow.AddMonths(1),
                    Status = EventStatus.InProgress,
                    CreatedById = Guid.NewGuid(),
                    LocationId = 1,
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow
                },
                new Event
                {
                    Name = "Electronic Waves Festival",
                    Description = "Premier electronic music festival with top international DJs",
                    EventInterval = DateTime.UtcNow.AddMonths(3),
                    Status = EventStatus.Planned,
                    CreatedById = Guid.NewGuid(),
                    LocationId = 1,
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow
                },
                new Event
                {
                    Name = "Exit Festival 2025",
                    Description = "Award-winning music festival in Petrovaradin Fortress",
                    EventInterval = DateTime.UtcNow.AddMonths(4),
                    Status = EventStatus.Planned,
                    CreatedById = Guid.NewGuid(),
                    LocationId = 2,
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow
                },
                new Event
                {
                    Name = "Jazz & Blues Evening",
                    Description = "Elegant evening of jazz and blues with renowned musicians",
                    EventInterval = DateTime.UtcNow.AddDays(45),
                    Status = EventStatus.Planned,
                    CreatedById = Guid.NewGuid(),
                    LocationId = 1,
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow
                },
                new Event
                {
                    Name = "Nisville Jazz Festival",
                    Description = "Traditional jazz festival in the historic Niš Fortress",
                    EventInterval = DateTime.UtcNow.AddMonths(5),
                    Status = EventStatus.Planned,
                    CreatedById = Guid.NewGuid(),
                    LocationId = 3,
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow
                },
                new Event
                {
                    Name = "Underground Electronic",
                    Description = "Underground electronic music night with local and international DJs",
                    EventInterval = DateTime.UtcNow.AddDays(20),
                    Status = EventStatus.InProgress,
                    CreatedById = Guid.NewGuid(),
                    LocationId = 1,
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow
                },
                new Event
                {
                    Name = "Summer Stadium Concert",
                    Description = "Major outdoor concert with multiple international headliners",
                    EventInterval = DateTime.UtcNow.AddMonths(6),
                    Status = EventStatus.Planned,
                    CreatedById = Guid.NewGuid(),
                    LocationId = 1,
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow
                }
            };
            context.Events.AddRange(events);
            await context.SaveChangesAsync();

            // 6. Seed SpecialOffers
            var specialOffers = new List<SpecialOffer>
            {
                new SpecialOffer
                {
                    Name = "Early Bird Special",
                    Description = "Early bird discount for advance purchases",
                    StartDate = DateTime.UtcNow,
                    EndDate = DateTime.UtcNow.AddMonths(1),
                    ApplicationCondition = "Purchase within first month of ticket release",
                    DiscountValue = 20,
                    TicketLimit = 1000,
                    OfferType = OfferType.EarlyBird
                },
                new SpecialOffer
                {
                    Name = "Student Discount",
                    Description = "Special pricing for students with valid ID",
                    StartDate = DateTime.UtcNow,
                    EndDate = DateTime.UtcNow.AddMonths(3),
                    ApplicationCondition = "Valid student ID required",
                    DiscountValue = 15,
                    TicketLimit = 500,
                    OfferType = OfferType.StudentDiscount
                },
                new SpecialOffer
                {
                    Name = "Group Booking Deal",
                    Description = "Discount for group purchases of 5 or more tickets",
                    StartDate = DateTime.UtcNow,
                    EndDate = DateTime.UtcNow.AddMonths(2),
                    ApplicationCondition = "Purchase 5+ tickets in single transaction",
                    DiscountValue = 25,
                    TicketLimit = 200,
                    OfferType = OfferType.GroupDiscount
                },
                new SpecialOffer
                {
                    Name = "Last Minute Deal",
                    Description = "Special discount for last-minute purchases",
                    StartDate = DateTime.UtcNow.AddMonths(1).AddDays(20),
                    EndDate = DateTime.UtcNow.AddMonths(2),
                    ApplicationCondition = "Purchase within 7 days of event",
                    DiscountValue = 10,
                    TicketLimit = 300,
                    OfferType = OfferType.PercentageOff
                },
                new SpecialOffer
                {
                    Name = "Senior Citizen Discount",
                    Description = "Special pricing for visitors over 65",
                    StartDate = DateTime.UtcNow,
                    EndDate = DateTime.UtcNow.AddMonths(4),
                    ApplicationCondition = "Valid ID showing age 65+",
                    DiscountValue = 30,
                    TicketLimit = 150,
                    OfferType = OfferType.SeniorDiscount
                },
                new SpecialOffer
                {
                    Name = "Buy One Get One 50%",
                    Description = "Second ticket at 50% discount",
                    StartDate = DateTime.UtcNow.AddDays(10),
                    EndDate = DateTime.UtcNow.AddMonths(1).AddDays(10),
                    ApplicationCondition = "Valid for specific events only",
                    DiscountValue = 50,
                    TicketLimit = 400,
                    OfferType = OfferType.BuyOneGetOne
                },
                new SpecialOffer
                {
                    Name = "VIP Season Pass",
                    Description = "Access to all events with VIP treatment",
                    StartDate = DateTime.UtcNow,
                    EndDate = DateTime.UtcNow.AddYears(1),
                    ApplicationCondition = "Limited availability - premium access",
                    DiscountValue = 0,
                    TicketLimit = 50,
                    OfferType = OfferType.SeasonPass
                },
                new SpecialOffer
                {
                    Name = "Loyalty Member Discount",
                    Description = "Exclusive discount for returning customers",
                    StartDate = DateTime.UtcNow,
                    EndDate = DateTime.UtcNow.AddMonths(6),
                    ApplicationCondition = "Previous purchase history required",
                    DiscountValue = 12,
                    TicketLimit = 800,
                    OfferType = OfferType.LoyaltyDiscount
                }
            };
            context.SpecialOffers.AddRange(specialOffers);
            await context.SaveChangesAsync();


            // 7. Seed PricingRules
            var pricingRules = new List<PricingRule>
            {
                new PricingRule
                {
                    Name = "Standard Dynamic Pricing",
                    Description = "Standard pricing model with early bird discounts",
                    MinimumPrice = 1500,
                    MaximumPrice = 12000,
                    OccupancyPercentage1 = 50,
                    OccupancyPercentage2 = 80,
                    OccupancyThreshold1 = 1.2m,
                    OccupancyThreshold2 = 1.5m,
                    EarlyBirdPercentage = 20,
                    PricingCondition = PricingCondition.TimeBasedEarlyBird,
                    DynamicCondition = "Time-based pricing with demand adjustments",
                    Modifier = 1.0m
                },
                new PricingRule
                {
                    Name = "High Demand Pricing",
                    Description = "Dynamic pricing based on venue occupancy levels",
                    MinimumPrice = 2500,
                    MaximumPrice = 18000,
                    OccupancyPercentage1 = 60,
                    OccupancyPercentage2 = 90,
                    OccupancyThreshold1 = 1.3m,
                    OccupancyThreshold2 = 2.0m,
                    EarlyBirdPercentage = 25,
                    PricingCondition = PricingCondition.OccupancyBased,
                    DynamicCondition = "Price increases with venue capacity utilization",
                    Modifier = 1.2m
                },
                new PricingRule
                {
                    Name = "Premium VIP Pricing",
                    Description = "Luxury pricing for VIP zones and premium experiences",
                    MinimumPrice = 8000,
                    MaximumPrice = 35000,
                    OccupancyPercentage1 = 40,
                    OccupancyPercentage2 = 70,
                    OccupancyThreshold1 = 1.5m,
                    OccupancyThreshold2 = 2.5m,
                    EarlyBirdPercentage = 15,
                    PricingCondition = PricingCondition.VIPUpgrade,
                    DynamicCondition = "Premium pricing for exclusive access areas",
                    Modifier = 2.0m
                },
                new PricingRule
                {
                    Name = "Weekend Premium",
                    Description = "Higher pricing for weekend events",
                    MinimumPrice = 2000,
                    MaximumPrice = 15000,
                    OccupancyPercentage1 = 55,
                    OccupancyPercentage2 = 85,
                    OccupancyThreshold1 = 1.4m,
                    OccupancyThreshold2 = 1.8m,
                    EarlyBirdPercentage = 18,
                    PricingCondition = PricingCondition.DayOfWeek,
                    DynamicCondition = "Weekend events carry premium pricing",
                    Modifier = 1.3m
                },
                new PricingRule
                {
                    Name = "Last Minute Pricing",
                    Description = "Special pricing for tickets sold close to event date",
                    MinimumPrice = 1000,
                    MaximumPrice = 8000,
                    OccupancyPercentage1 = 30,
                    OccupancyPercentage2 = 60,
                    OccupancyThreshold1 = 0.8m,
                    OccupancyThreshold2 = 1.1m,
                    EarlyBirdPercentage = 0,
                    PricingCondition = PricingCondition.LastMinute,
                    DynamicCondition = "Reduced pricing for last-minute sales",
                    Modifier = 0.8m
                },
                new PricingRule
                {
                    Name = "Festival Season Discount",
                    Description = "Seasonal pricing adjustments for festival period",
                    MinimumPrice = 3000,
                    MaximumPrice = 20000,
                    OccupancyPercentage1 = 65,
                    OccupancyPercentage2 = 95,
                    OccupancyThreshold1 = 1.6m,
                    OccupancyThreshold2 = 2.2m,
                    EarlyBirdPercentage = 30,
                    PricingCondition = PricingCondition.SeasonalDiscount,
                    DynamicCondition = "Festival season pricing with volume discounts",
                    Modifier = 1.4m
                }
            };
            context.PricingRules.AddRange(pricingRules);
            await context.SaveChangesAsync();

            // 8. Seed TicketTypes
            var ticketTypes = new List<TicketType>
            {
                // Rock Legends Live tickets
                new TicketType { Name = "Floor Front - Rock Legends", Description = "Premium floor access close to stage", AvailableQuantity = 2800, Status = TicketTypeStatus.Active, ZoneId = 1, EventId = 1 },
                new TicketType { Name = "Floor General - Rock Legends", Description = "General floor admission", AvailableQuantity = 4800, Status = TicketTypeStatus.Active, ZoneId = 2, EventId = 1 },
                new TicketType { Name = "West Lower - Rock Legends", Description = "Lower west tribune seating", AvailableQuantity = 1900, Status = TicketTypeStatus.Active, ZoneId = 3, EventId = 1 },
                new TicketType { Name = "East Lower - Rock Legends", Description = "Lower east tribune seating", AvailableQuantity = 1900, Status = TicketTypeStatus.Active, ZoneId = 5, EventId = 1 },
                
                // Indie Discovery Night tickets
                new TicketType { Name = "Front Row - Indie Night", Description = "Close to stage experience", AvailableQuantity = 480, Status = TicketTypeStatus.Active, ZoneId = 9, EventId = 2 },
                new TicketType { Name = "General Admission - Indie", Description = "Standard admission ticket", AvailableQuantity = 680, Status = TicketTypeStatus.Active, ZoneId = 10, EventId = 2 },
                new TicketType { Name = "Back Area - Indie", Description = "Casual viewing area", AvailableQuantity = 280, Status = TicketTypeStatus.Active, ZoneId = 11, EventId = 2 },
                
                // Electronic Waves Festival tickets
                new TicketType { Name = "Golden Circle - Electronic", Description = "VIP access to main stage area", AvailableQuantity = 950, Status = TicketTypeStatus.Active, ZoneId = 12, EventId = 3 },
                new TicketType { Name = "General Floor - Electronic", Description = "Main dance floor access", AvailableQuantity = 5800, Status = TicketTypeStatus.Active, ZoneId = 13, EventId = 3 },
                new TicketType { Name = "Lower Bowl - Electronic", Description = "Seated viewing with great stage view", AvailableQuantity = 5700, Status = TicketTypeStatus.Active, ZoneId = 14, EventId = 3 },
                
                // Exit Festival tickets
                new TicketType { Name = "Exit - Main Stage Front", Description = "Premium access to main stage front", AvailableQuantity = 9500, Status = TicketTypeStatus.Active, ZoneId = 16, EventId = 4 },
                new TicketType { Name = "Exit - General Festival", Description = "Full festival grounds access", AvailableQuantity = 24000, Status = TicketTypeStatus.Active, ZoneId = 17, EventId = 4 },
                new TicketType { Name = "Exit - Chill Zone", Description = "Relaxed area with full festival access", AvailableQuantity = 4800, Status = TicketTypeStatus.Active, ZoneId = 18, EventId = 4 },
                
                // Jazz & Blues Evening tickets
                new TicketType { Name = "Orchestra Premium - Jazz", Description = "Premium orchestra seating", AvailableQuantity = 950, Status = TicketTypeStatus.Active, ZoneId = 19, EventId = 5 },
                new TicketType { Name = "Orchestra Standard - Jazz", Description = "Standard orchestra seating", AvailableQuantity = 950, Status = TicketTypeStatus.Active, ZoneId = 20, EventId = 5 },
                new TicketType { Name = "Balcony - Jazz", Description = "Balcony level seating", AvailableQuantity = 1900, Status = TicketTypeStatus.Active, ZoneId = 21, EventId = 5 },
                
                // Nisville Jazz Festival tickets
                new TicketType { Name = "Jazz Front Stage", Description = "Front of jazz stage access", AvailableQuantity = 1900, Status = TicketTypeStatus.Active, ZoneId = 22, EventId = 6 },
                new TicketType { Name = "Jazz Festival General", Description = "General festival access", AvailableQuantity = 5700, Status = TicketTypeStatus.Active, ZoneId = 23, EventId = 6 },
                
                // Underground Electronic tickets
                new TicketType { Name = "DJ Booth VIP", Description = "Close to DJ booth experience", AvailableQuantity = 280, Status = TicketTypeStatus.Active, ZoneId = 24, EventId = 7 },
                new TicketType { Name = "Club General", Description = "General club access", AvailableQuantity = 480, Status = TicketTypeStatus.Active, ZoneId = 25, EventId = 7 },
                
                // Summer Stadium Concert tickets
                new TicketType { Name = "Stadium Floor - Summer", Description = "Main stadium floor standing", AvailableQuantity = 23800, Status = TicketTypeStatus.Active, ZoneId = 26, EventId = 8 },
                new TicketType { Name = "Stadium Seats - Summer", Description = "Stadium seating with great view", AvailableQuantity = 9500, Status = TicketTypeStatus.Active, ZoneId = 27, EventId = 8 }
            };
            context.TicketTypes.AddRange(ticketTypes);
            await context.SaveChangesAsync();

            // 9. Seed individual Tickets
            var tickets = new List<Ticket>();
            var random = new Random();

            foreach (var ticketType in ticketTypes)
            {
                // Create between 15 to 75 tickets for each ticket type (more realistic numbers)
                int ticketsToCreate = random.Next(15, 76);
                var zone = zones.First(z => z.ZoneId == ticketType.ZoneId);

                for (int i = 0; i < ticketsToCreate; i++)
                {
                    // More realistic price variation (±20% from base price)
                    var priceVariation = (decimal)(random.NextDouble() * 0.4 - 0.2); // -20% to +20%
                    var finalPrice = zone.BasePrice + (zone.BasePrice * priceVariation);

                    // Ensure minimum price threshold
                    if (finalPrice < zone.BasePrice * 0.8m) finalPrice = zone.BasePrice * 0.8m;

                    var ticketStatuses = new[] { TicketStatus.Available, TicketStatus.Available, TicketStatus.Available,
                                               TicketStatus.Reserved, TicketStatus.Sold };
                    var randomStatus = ticketStatuses[random.Next(ticketStatuses.Length)];

                    tickets.Add(new Ticket
                    {
                        UniqueCode = $"TKT-{ticketType.TicketTypeId:D3}-{DateTime.Now:yyyyMMdd}-{i + 1:D4}",
                        QrCode = Guid.NewGuid().ToString(),
                        IssueDate = DateTime.UtcNow.AddDays(-random.Next(1, 45)),
                        FinalPrice = Math.Round(finalPrice, 0),
                        Status = randomStatus,
                        TicketTypeId = ticketType.TicketTypeId
                    });
                }
            }

            context.Tickets.AddRange(tickets);
            await context.SaveChangesAsync();

            // 10. Seed Performers
            var performers = new List<Performer>
            {
                new Performer
                {
                    Name = "Arctic Monkeys",
                    Email = "booking@arcticmonkeys.com",
                    Contact = "+44 20 7946 0958",
                    Genre = "Indie Rock",
                    Popularity = 95,
                    TechnicalRequirements = "Full light rig, 32-channel mixing desk, wireless IEM system",
                    MinPrice = 150000,
                    MaxPrice = 300000,
                    AverageResponseTime = TimeSpan.FromHours(24),
                    Status = "Available",
                    UpdatedAt = DateTime.UtcNow
                },
                new Performer
                {
                    Name = "Disclosure",
                    Email = "management@disclosure.co.uk",
                    Contact = "+44 20 8123 4567",
                    Genre = "Electronic",
                    Popularity = 88,
                    TechnicalRequirements = "DJ setup, LED screen, smoke machines, wireless microphones",
                    MinPrice = 80000,
                    MaxPrice = 180000,
                    AverageResponseTime = TimeSpan.FromHours(12),
                    Status = "Available",
                    UpdatedAt = DateTime.UtcNow
                },
                new Performer
                {
                    Name = "Goran Bregović",
                    Email = "office@bregovic.rs",
                    Contact = "+381 11 234 5678",
                    Genre = "World Music",
                    Popularity = 92,
                    TechnicalRequirements = "Orchestra setup, 16 wireless microphones, traditional instruments amplification",
                    MinPrice = 45000,
                    MaxPrice = 120000,
                    AverageResponseTime = TimeSpan.FromHours(48),
                    Status = "Busy",
                    UpdatedAt = DateTime.UtcNow
                },
                new Performer
                {
                    Name = "Dubioza Kolektiv",
                    Email = "booking@dubioza.ba",
                    Contact = "+387 33 567 890",
                    Genre = "Ska Punk",
                    Popularity = 78,
                    TechnicalRequirements = "Full band setup, horn section amplification, video projection",
                    MinPrice = 25000,
                    MaxPrice = 65000,
                    AverageResponseTime = TimeSpan.FromHours(18),
                    Status = "Available",
                    UpdatedAt = DateTime.UtcNow
                },
                new Performer
                {
                    Name = "Nina Kraviz",
                    Email = "booking@ninakraviz.com",
                    Contact = "+49 30 1234 5678",
                    Genre = "Techno",
                    Popularity = 85,
                    TechnicalRequirements = "Pioneer CDJ setup, Allen & Heath mixer, professional monitoring",
                    MinPrice = 35000,
                    MaxPrice = 85000,
                    AverageResponseTime = TimeSpan.FromHours(6),
                    Status = "Available",
                    UpdatedAt = DateTime.UtcNow
                },
                new Performer
                {
                    Name = "Bojan Marović Trio",
                    Email = "info@bojanmarovic.com",
                    Contact = "+381 11 345 6789",
                    Genre = "Jazz",
                    Popularity = 72,
                    TechnicalRequirements = "Acoustic piano, drum kit, bass amplification, intimate lighting",
                    MinPrice = 8000,
                    MaxPrice = 25000,
                    AverageResponseTime = TimeSpan.FromHours(36),
                    Status = "Available",
                    UpdatedAt = DateTime.UtcNow
                },
                new Performer
                {
                    Name = "Local Underground Collective",
                    Email = "contact@undergroundcollective.rs",
                    Contact = "+381 64 123 4567",
                    Genre = "Alternative Hip-Hop",
                    Popularity = 45,
                    TechnicalRequirements = "DJ setup, 4 wireless mics, basic lighting, laptop connection",
                    MinPrice = 3000,
                    MaxPrice = 12000,
                    AverageResponseTime = TimeSpan.FromHours(8),
                    Status = "Available",
                    UpdatedAt = DateTime.UtcNow
                },
                new Performer
                {
                    Name = "Symphony Orchestra Belgrade",
                    Email = "admin@bgphilharmonic.rs",
                    Contact = "+381 11 678 9012",
                    Genre = "Classical",
                    Popularity = 89,
                    TechnicalRequirements = "Full orchestral setup, conductor podium, acoustic optimization, 40+ music stands",
                    MinPrice = 60000,
                    MaxPrice = 150000,
                    AverageResponseTime = TimeSpan.FromDays(3),
                    Status = "Available",
                    UpdatedAt = DateTime.UtcNow
                }
            };
            context.Performers.AddRange(performers);
            await context.SaveChangesAsync();

            // 12. Seed RecordedSales
            var recordedSales = new List<RecordedSale>();
            var paymentMethods = new[] { PaymentMethod.CreditCard, PaymentMethod.DebitCard, PaymentMethod.BankTransfer, PaymentMethod.PayPal };
            var statuses = new[] { TransactionStatus.Completed, TransactionStatus.Completed, TransactionStatus.Completed,
                      TransactionStatus.Pending, TransactionStatus.Failed, TransactionStatus.Processing };

            // Create realistic sales data
            for (int i = 0; i < 50; i++) // 50 recorded sales
            {
                var user = applicationUsers[random.Next(applicationUsers.Count)];
                var saleDate = DateTime.UtcNow.AddDays(-random.Next(1, 90)); // Sales from last 3 months
                var ticketsInSale = new List<Ticket>();
                var specialOffersInSale = new List<SpecialOffer>();

                // Select 1-6 tickets for this sale
                var ticketsToAdd = random.Next(1, 7);
                var availableTickets = tickets.Where(t => t.RecordedSaleId == null).ToList();

                if (availableTickets.Count > 0)
                {
                    for (int j = 0; j < Math.Min(ticketsToAdd, availableTickets.Count); j++)
                    {
                        var ticket = availableTickets[random.Next(availableTickets.Count)];
                        ticketsInSale.Add(ticket);
                        availableTickets.Remove(ticket); // Avoid duplicate tickets
                    }
                }

                // Randomly apply 0-2 special offers
                var offersToAdd = random.Next(0, 3);
                for (int k = 0; k < offersToAdd; k++)
                {
                    var offer = specialOffers[random.Next(specialOffers.Count)];
                    if (!specialOffersInSale.Contains(offer))
                        specialOffersInSale.Add(offer);
                }

                var totalAmount = ticketsInSale.Sum(t => t.FinalPrice);

                // Apply special offer discounts
                foreach (var offer in specialOffersInSale)
                {
                    totalAmount -= offer.DiscountValue;
                }

                // Ensure total amount is not negative
                totalAmount = Math.Max(totalAmount, 0);

                var recordedSale = new RecordedSale
                {
                    TotalAmount = totalAmount,
                    SaleDate = saleDate,
                    TransactionStatus = statuses[random.Next(statuses.Length)],
                    PaymentMethod = paymentMethods[random.Next(paymentMethods.Length)],
                    ApplicationUserId = user.Id,
                    Tickets = ticketsInSale,
                    SpecialOffers = specialOffersInSale
                };

                recordedSales.Add(recordedSale);
            }

            context.RecordedSales.AddRange(recordedSales);
            await context.SaveChangesAsync();

            // Update tickets with their recorded sale IDs
            foreach (var sale in recordedSales)
            {
                foreach (var ticket in sale.Tickets)
                {
                    ticket.RecordedSaleId = sale.RecordedSaleId;
                    ticket.Status = sale.TransactionStatus == TransactionStatus.Completed ? TicketStatus.Sold :
                                   sale.TransactionStatus == TransactionStatus.Failed ? TicketStatus.Available :
                                   TicketStatus.Reserved;
                }
            }
            await context.SaveChangesAsync();

            // 13. Seed MediaChannels FIRST (no dependencies)
            var marina = applicationUsers.First(u => u.Email == "marina@mediacampaign.com");
            var stefan = applicationUsers.First(u => u.Email == "stefan@mediacampaign.com");

            var mediaChannels = new List<MediaChannel>
            {
                new MediaChannel { PlatformType = "Instagram", APIKey = "INSTAGRAM_API_KEY", APIURL = "https://api.instagram.com", APIVersion = "v12.0" },
                new MediaChannel { PlatformType = "Facebook", APIKey = "FACEBOOK_API_KEY", APIURL = "https://graph.facebook.com", APIVersion = "v15.0" },
                new MediaChannel { PlatformType = "YouTube", APIKey = "YOUTUBE_API_KEY", APIURL = "https://www.googleapis.com/youtube/v3", APIVersion = "v3" },
                new MediaChannel { PlatformType = "TikTok", APIKey = "TIKTOK_API_KEY", APIURL = "https://open-api.tiktok.com", APIVersion = "v2" }
            };
            context.MediaChannels.AddRange(mediaChannels);
            await context.SaveChangesAsync();

            // 14. Seed MediaWorkflows SECOND (minimal dependencies)
            var mediaWorkflows = new List<MediaWorkflow>
            {
                new MediaWorkflow
                {
                    WorkflowDescription = "Instagram Story Workflow - Create, Review, Schedule, Publish",
                    ApprovalId = null // Will be set later if needed
                },
                new MediaWorkflow
                {
                    WorkflowDescription = "Facebook Post Workflow - Design, Copy Review, Approval, Publish",
                    ApprovalId = null
                },
                new MediaWorkflow
                {
                    WorkflowDescription = "YouTube Video Workflow - Edit, Audio Mix, Thumbnail, Upload",
                    ApprovalId = null
                },
                new MediaWorkflow
                {
                    WorkflowDescription = "TikTok Short Workflow - Quick Edit, Hashtag Research, Publish",
                    ApprovalId = null
                },
                new MediaWorkflow
                {
                    WorkflowDescription = "Multi-Platform Campaign Workflow - Cross-platform coordination",
                    ApprovalId = null
                }
            };
            context.MediaWorkflows.AddRange(mediaWorkflows);
            await context.SaveChangesAsync();

            // 15. Seed AdTypes (depends on MediaWorkflows)
            var adTypes = new List<AdType>
            {
                new AdType
                {
                    TypeName = "Instagram Story",
                    TypeDescription = "Vertical image/video for Instagram stories with interactive elements",
                    Dimensions = "1080x1920",
                    Duration = 15,
                    FileFormat = "mp4",
                    MediaWorkflowId = 1
                },
                new AdType
                {
                    TypeName = "Facebook Post",
                    TypeDescription = "Standard Facebook image post with engaging copy",
                    Dimensions = "1200x628",
                    Duration = 0,
                    FileFormat = "jpg",
                    MediaWorkflowId = 2
                },
                new AdType
                {
                    TypeName = "YouTube Video",
                    TypeDescription = "Promotional video for YouTube with custom thumbnail",
                    Dimensions = "1920x1080",
                    Duration = 60,
                    FileFormat = "mp4",
                    MediaWorkflowId = 3
                },
                new AdType
                {
                    TypeName = "TikTok Short",
                    TypeDescription = "Short vertical video for TikTok with trending audio",
                    Dimensions = "1080x1920",
                    Duration = 30,
                    FileFormat = "mp4",
                    MediaWorkflowId = 4
                },
                new AdType
                {
                    TypeName = "Facebook Video",
                    TypeDescription = "Square video format for Facebook feed",
                    Dimensions = "1080x1080",
                    Duration = 45,
                    FileFormat = "mp4",
                    MediaWorkflowId = 2
                },
                new AdType
                {
                    TypeName = "Instagram Reel",
                    TypeDescription = "Vertical video for Instagram Reels with music",
                    Dimensions = "1080x1920",
                    Duration = 30,
                    FileFormat = "mp4",
                    MediaWorkflowId = 1
                }
            };
            context.AdTypes.AddRange(adTypes);
            await context.SaveChangesAsync();

            // 16. Seed MediaTasks (depends on MediaWorkflows)
            var mediaTasks = new List<MediaTask>
            {
                // Instagram Story Workflow Tasks
                new MediaTask { TaskName = "Design Instagram Story Creative", Order = 1, TaskStatus = MediaTaskStatus.Approved, WorkflowId = 1, ManagerId = marina.Id }, // ako vežeš na Ad },
                new MediaTask { TaskName = "Add Interactive Elements", Order = 2, TaskStatus = MediaTaskStatus.Approved,WorkflowId = 1, ManagerId = marina.Id },
                new MediaTask { TaskName = "Schedule Instagram Story Post", Order = 3,TaskStatus = MediaTaskStatus.Approved, WorkflowId = 1, ManagerId = marina.Id },
                
                // Facebook Post Workflow Tasks
                new MediaTask { TaskName = "Create Facebook Post Design", Order = 1,TaskStatus = MediaTaskStatus.Approved, WorkflowId = 2, ManagerId = marina.Id },
                new MediaTask { TaskName = "Write Engaging Copy", Order = 2,TaskStatus = MediaTaskStatus.Approved, WorkflowId = 2, ManagerId = marina.Id },
                new MediaTask { TaskName = "Schedule Facebook Post", Order = 3,TaskStatus = MediaTaskStatus.Approved, WorkflowId = 2, ManagerId = marina.Id },
                
                // YouTube Video Workflow Tasks
                new MediaTask { TaskName = "Edit Video Content", Order = 1, TaskStatus = MediaTaskStatus.Approved,WorkflowId = 3, ManagerId = marina.Id },
                new MediaTask { TaskName = "Create Custom Thumbnail", Order = 2,TaskStatus = MediaTaskStatus.Approved, WorkflowId = 3, ManagerId = marina.Id },
                new MediaTask { TaskName = "Upload to YouTube", Order = 3,TaskStatus = MediaTaskStatus.Approved,WorkflowId = 3, ManagerId = marina.Id },
                
                // TikTok Short Workflow Tasks
                new MediaTask { TaskName = "Edit TikTok Short", Order = 1, TaskStatus = MediaTaskStatus.Approved,WorkflowId = 4, ManagerId = marina.Id},
                new MediaTask { TaskName = "Add Trending Audio", Order = 2,TaskStatus = MediaTaskStatus.Approved, WorkflowId = 4, ManagerId = marina.Id },
                new MediaTask { TaskName = "Publish TikTok Short", Order = 3,TaskStatus = MediaTaskStatus.Approved, WorkflowId = 4, ManagerId = marina.Id }
            };
            context.MediaTasks.AddRange(mediaTasks);
            await context.SaveChangesAsync();

            // 17. Seed Approvals (depends on MediaTasks)
            var approvals = new List<Approval>
            {
                new Approval
                {
                    ApprovalStatus = "Approved",
                    Comment = "Instagram story looks engaging with good call-to-action",
                    ApprovalDate = DateTime.UtcNow.AddDays(-2),
                    MediaTaskId = 1
                },
                new Approval
                {
                    ApprovalStatus = "Pending",
                    Comment = "Waiting for final review from marketing team",
                    ApprovalDate = DateTime.UtcNow.AddDays(-1),
                    MediaTaskId = 4
                },
                new Approval
                {
                    ApprovalStatus = "Rejected",
                    Comment = "Video needs better audio quality and color correction",
                    ApprovalDate = DateTime.UtcNow.AddHours(-6),
                    MediaTaskId = 7
                },
                new Approval
                {
                    ApprovalStatus = "Approved",
                    Comment = "TikTok content is perfect for target audience",
                    ApprovalDate = DateTime.UtcNow.AddHours(-12),
                    MediaTaskId = 10
                },
                new Approval
                {
                    ApprovalStatus = "Revision Required",
                    Comment = "Facebook copy needs more compelling call-to-action",
                    ApprovalDate = DateTime.UtcNow.AddHours(-4),
                    MediaTaskId = 5
                }
            };
            context.Approvals.AddRange(approvals);
            await context.SaveChangesAsync();

            // 18. Seed Campaigns (brands are assigned by MarketingSeeder)
            var campaigns = new List<Campaign>
            {
                new Campaign
                {
                    Name = "Rock Legends Multi-Platform Campaign",
                    StartDate = DateTime.UtcNow.AddDays(-30),
                    EndDate = DateTime.UtcNow.AddDays(15),
                    TotalBudget = 15000
                },
                new Campaign
                {
                    Name = "Indie Night Social Media Push",
                    StartDate = DateTime.UtcNow.AddDays(-20),
                    EndDate = DateTime.UtcNow.AddDays(8),
                    TotalBudget = 8000
                },
                new Campaign
                {
                    Name = "Electronic Waves Digital Campaign",
                    StartDate = DateTime.UtcNow.AddDays(-25),
                    EndDate = DateTime.UtcNow.AddDays(35),
                    TotalBudget = 25000
                },
                new Campaign
                {
                    Name = "Exit Festival International Campaign",
                    StartDate = DateTime.UtcNow.AddDays(-45),
                    EndDate = DateTime.UtcNow.AddDays(60),
                    TotalBudget = 50000
                },
                new Campaign
                {
                    Name = "Underground Scene Viral Campaign",
                    StartDate = DateTime.UtcNow.AddDays(-10),
                    EndDate = DateTime.UtcNow.AddDays(5),
                    TotalBudget = 3500
                }
            };
            context.Campaigns.AddRange(campaigns);
            await context.SaveChangesAsync();

            // 19. Seed Ads (requires Campaigns, MediaWorkflows, AdTypes)
            var ads = new List<Ad>
            {
                // Rock Legends Campaign Ads
                new Ad
                {
                    Title = "Rock Legends - Instagram Story Countdown",
                    CreationDate = DateTime.UtcNow.AddDays(-25),
                    Deadline = DateTime.UtcNow.AddDays(5),
                    CurrentPhase = AdStatus.Published,
                    PublicationDate = DateTime.UtcNow.AddDays(-3),
                    CampaignId = 1,
                    MediaWorkflowId = 1,
                    AdTypeId = 1,
                    CreatedById = marina.Id
                },
                new Ad
                {
                    Title = "Rock Legends - Facebook Event Post",
                    CreationDate = DateTime.UtcNow.AddDays(-28),
                    Deadline = DateTime.UtcNow.AddDays(3),
                    CurrentPhase = AdStatus.Published,
                    PublicationDate = DateTime.UtcNow.AddDays(-5),
                    CampaignId = 1,
                    MediaWorkflowId = 2,
                    AdTypeId = 2,
                    CreatedById = marina.Id
                },
                new Ad
                {
                    Title = "Rock Legends - YouTube Trailer",
                    CreationDate = DateTime.UtcNow.AddDays(-20),
                    Deadline = DateTime.UtcNow.AddDays(10),
                    CurrentPhase = AdStatus.PendingApproval,
                    PublicationDate = null,
                    CampaignId = 1,
                    MediaWorkflowId = 3,
                    AdTypeId = 3,
                    CreatedById = marina.Id
                },
                
                // Indie Night Campaign Ads
                new Ad
                {
                    Title = "Indie Discovery - TikTok Behind Scenes",
                    CreationDate = DateTime.UtcNow.AddDays(-15),
                    Deadline = DateTime.UtcNow.AddDays(2),
                    CurrentPhase = AdStatus.ScheduledPublication,
                    PublicationDate = DateTime.UtcNow.AddDays(1),
                    CampaignId = 2,
                    MediaWorkflowId = 4,
                    AdTypeId = 4,
                    CreatedById = marina.Id
                },
                new Ad
                {
                    Title = "Indie Discovery - Instagram Reel Artist Spotlight",
                    CreationDate = DateTime.UtcNow.AddDays(-12),
                    Deadline = DateTime.UtcNow.AddDays(4),
                    CurrentPhase = AdStatus.InPreparation,
                    PublicationDate = null,
                    CampaignId = 2,
                    MediaWorkflowId = 1,
                    AdTypeId = 6,
                    CreatedById = marina.Id
                },
                
                // Electronic Waves Campaign Ads
                new Ad
                {
                    Title = "Electronic Waves - Festival Lineup Reveal",
                    CreationDate = DateTime.UtcNow.AddDays(-22),
                    Deadline = DateTime.UtcNow.AddDays(8),
                    CurrentPhase = AdStatus.Published,
                    PublicationDate = DateTime.UtcNow.AddDays(-7),
                    CampaignId = 3,
                    MediaWorkflowId = 2,
                    AdTypeId = 5,
                    CreatedById = marina.Id
                },
                new Ad
                {
                    Title = "Electronic Waves - DJ Mix Teaser",
                    CreationDate = DateTime.UtcNow.AddDays(-18),
                    Deadline = DateTime.UtcNow.AddDays(12),
                    CurrentPhase = AdStatus.PendingApproval,
                    PublicationDate = null,
                    CampaignId = 3,
                    MediaWorkflowId = 3,
                    AdTypeId = 3,
                    CreatedById = marina.Id
                },
                
                // Exit Festival Campaign Ads
                new Ad
                {
                    Title = "Exit 2025 - Early Bird Instagram Stories",
                    CreationDate = DateTime.UtcNow.AddDays(-40),
                    Deadline = DateTime.UtcNow.AddDays(20),
                    CurrentPhase = AdStatus.Published,
                    PublicationDate = DateTime.UtcNow.AddDays(-15),
                    CampaignId = 4,
                    MediaWorkflowId = 1,
                    AdTypeId = 1,
                    CreatedById = marina.Id
                },
                new Ad
                {
                    Title = "Exit 2025 - International YouTube Campaign",
                    CreationDate = DateTime.UtcNow.AddDays(-35),
                    Deadline = DateTime.UtcNow.AddDays(25),
                    CurrentPhase = AdStatus.ScheduledPublication,
                    PublicationDate = DateTime.UtcNow.AddDays(3),
                    CampaignId = 4,
                    MediaWorkflowId = 3,
                    AdTypeId = 3,
                    CreatedById = marina.Id
                },
                
                // Underground Electronic Campaign Ads
                new Ad
                {
                    Title = "Underground - TikTok Viral Challenge",
                    CreationDate = DateTime.UtcNow.AddDays(-8),
                    Deadline = DateTime.UtcNow.AddDays(2),
                    CurrentPhase = AdStatus.Published,
                    PublicationDate = DateTime.UtcNow.AddDays(-2),
                    CampaignId = 5,
                    MediaWorkflowId = 4,
                    AdTypeId = 4,
                    CreatedById = marina.Id
                }
            };
            context.Ads.AddRange(ads);
            await context.SaveChangesAsync();

            // 20. Seed MediaVersions (requires Ads)
            var mediaVersions = new List<MediaVersion>
            {
                // Rock Legends Instagram Story versions
                new MediaVersion
                {
                    AdId = 1,
                    VersionFileName = "rock_legends_story_v1.mp4",
                    FileType = "mp4",
                    FileURL = "https://cdn.mems.com/media/rock_legends_story_v1.mp4",
                    IsFinalVersion = false
                },
                new MediaVersion
                {
                    AdId = 1,
                    VersionFileName = "rock_legends_story_final.mp4",
                    FileType = "mp4",
                    FileURL = "https://cdn.mems.com/media/rock_legends_story_final.mp4",
                    IsFinalVersion = true
                },
                
                // Rock Legends Facebook Post versions
                new MediaVersion
                {
                    AdId = 2,
                    VersionFileName = "rock_legends_fb_post.jpg",
                    FileType = "jpg",
                    FileURL = "https://cdn.mems.com/media/rock_legends_fb_post.jpg",
                    IsFinalVersion = true
                },
                
                // Rock Legends YouTube Trailer versions
                new MediaVersion
                {
                    AdId = 3,
                    VersionFileName = "rock_legends_trailer_draft.mp4",
                    FileType = "mp4",
                    FileURL = "https://cdn.mems.com/media/rock_legends_trailer_draft.mp4",
                    IsFinalVersion = false
                },
                new MediaVersion
                {
                    AdId = 3,
                    VersionFileName = "rock_legends_trailer_v2.mp4",
                    FileType = "mp4",
                    FileURL = "https://cdn.mems.com/media/rock_legends_trailer_v2.mp4",
                    IsFinalVersion = false
                },
                
                // Indie Discovery TikTok versions
                new MediaVersion
                {
                    AdId = 4,
                    VersionFileName = "indie_tiktok_behind_scenes.mp4",
                    FileType = "mp4",
                    FileURL = "https://cdn.mems.com/media/indie_tiktok_behind_scenes.mp4",
                    IsFinalVersion = true
                },
                
                // Electronic Waves Facebook Video versions
                new MediaVersion
                {
                    AdId = 6,
                    VersionFileName = "electronic_waves_lineup_v1.mp4",
                    FileType = "mp4",
                    FileURL = "https://cdn.mems.com/media/electronic_waves_lineup_v1.mp4",
                    IsFinalVersion = false
                },
                new MediaVersion
                {
                    AdId = 6,
                    VersionFileName = "electronic_waves_lineup_final.mp4",
                    FileType = "mp4",
                    FileURL = "https://cdn.mems.com/media/electronic_waves_lineup_final.mp4",
                    IsFinalVersion = true
                },
                
                // Exit Festival versions
                new MediaVersion
                {
                    AdId = 8,
                    VersionFileName = "exit_early_bird_story.mp4",
                    FileType = "mp4",
                    FileURL = "https://cdn.mems.com/media/exit_early_bird_story.mp4",
                    IsFinalVersion = true
                },
                
                // Underground TikTok versions
                new MediaVersion
                {
                    AdId = 10,
                    VersionFileName = "underground_viral_challenge.mp4",
                    FileType = "mp4",
                    FileURL = "https://cdn.mems.com/media/underground_viral_challenge.mp4",
                    IsFinalVersion = true
                }
            };
            context.MediaVersions.AddRange(mediaVersions);
            await context.SaveChangesAsync();

            // 21. Seed IntegrationStatuses (requires Ads and MediaChannels)
            var integrationStatuses = new List<IntegrationStatus>
            {
                // Rock Legends Instagram Story
                new IntegrationStatus
                {
                    AdId = 1,
                    ChannelId = 1, // Instagram
                    Status = MusicEventManagementSystem.API.Enums.StatusIntegration.Published,
                    PublicationDate = DateTime.UtcNow.AddDays(-3),
                    Error = null,
                    LastSynced = DateTime.UtcNow.AddHours(-2)
                },
                
                // Rock Legends Facebook Post
                new IntegrationStatus
                {
                    AdId = 2,
                    ChannelId = 2, // Facebook
                    Status = MusicEventManagementSystem.API.Enums.StatusIntegration.Published,
                    PublicationDate = DateTime.UtcNow.AddDays(-5),
                    Error = null,
                    LastSynced = DateTime.UtcNow.AddHours(-1)
                },
                
                // Rock Legends YouTube Trailer
                new IntegrationStatus
                {
                    AdId = 3,
                    ChannelId = 3, // YouTube
                    Status = MusicEventManagementSystem.API.Enums.StatusIntegration.Published,
                    PublicationDate = null,
                    Error = null,
                    LastSynced = DateTime.UtcNow.AddMinutes(-30)
                },
                
                // Indie Discovery TikTok
                new IntegrationStatus
                {
                    AdId = 4,
                    ChannelId = 4, // TikTok
                    Status = MusicEventManagementSystem.API.Enums.StatusIntegration.Published,
                    PublicationDate = DateTime.UtcNow.AddDays(1),
                    Error = null,
                    LastSynced = DateTime.UtcNow.AddMinutes(-15)
                },
                
                // Electronic Waves Facebook Video
                new IntegrationStatus
                {
                    AdId = 6,
                    ChannelId = 2, // Facebook
                    Status = MusicEventManagementSystem.API.Enums.StatusIntegration.Published,
                    PublicationDate = DateTime.UtcNow.AddDays(-7),
                    Error = null,
                    LastSynced = DateTime.UtcNow.AddHours(-3)
                },
                
                // Electronic Waves YouTube DJ Mix
                new IntegrationStatus
                {
                    AdId = 7,
                    ChannelId = 3, // YouTube
                    Status = MusicEventManagementSystem.API.Enums.StatusIntegration.Failed,
                    PublicationDate = null,
                    Error = "Video copyright claim detected - audio needs replacement",
                    LastSynced = DateTime.UtcNow.AddHours(-4)
                },
                
                // Exit Festival Instagram
                new IntegrationStatus
                {
                    AdId = 8,
                    ChannelId = 1, // Instagram
                    Status = MusicEventManagementSystem.API.Enums.StatusIntegration.Published,
                    PublicationDate = DateTime.UtcNow.AddDays(-15),
                    Error = null,
                    LastSynced = DateTime.UtcNow.AddHours(-6)
                },
                
                // Exit Festival YouTube
                new IntegrationStatus
                {
                    AdId = 9,
                    ChannelId = 3, // YouTube
                    Status = MusicEventManagementSystem.API.Enums.StatusIntegration.Published,
                    PublicationDate = DateTime.UtcNow.AddDays(3),
                    Error = null,
                    LastSynced = DateTime.UtcNow.AddMinutes(-45)
                },
                
                // Underground TikTok
                new IntegrationStatus
                {
                    AdId = 10,
                    ChannelId = 4, // TikTok
                    Status = MusicEventManagementSystem.API.Enums.StatusIntegration.Published,
                    PublicationDate = DateTime.UtcNow.AddDays(-2),
                    Error = null,
                    LastSynced = DateTime.UtcNow.AddMinutes(-10)
                }
            };
            context.IntegrationStatuses.AddRange(integrationStatuses);
            await context.SaveChangesAsync();

            Console.WriteLine($"Database seeded successfully!");
            Console.WriteLine($"- {venues.Count} venues created");
            Console.WriteLine($"- {segments.Count} segments created");
            Console.WriteLine($"- {zones.Count} zones created");
            Console.WriteLine($"- {events.Count} events created");
            Console.WriteLine($"- {ticketTypes.Count} ticket types created");
            Console.WriteLine($"- {tickets.Count} individual tickets created");
            Console.WriteLine($"- {specialOffers.Count} special offers created");
            Console.WriteLine($"- {pricingRules.Count} pricing rules created");
            Console.WriteLine($"- {performers.Count} performers created");
            Console.WriteLine($"- {applicationUsers.Count} application users created");
            Console.WriteLine($"- {recordedSales.Count} recorded sales created");
        }
    }
}