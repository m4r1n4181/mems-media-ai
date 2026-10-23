using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace MusicEventManagementSystem.API.Migrations
{
    /// <inheritdoc />
    public partial class MarketingAgencyBrandsAndInfluencers : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Campaigns_Events_EventId",
                table: "Campaigns");

            migrationBuilder.DropIndex(
                name: "IX_Campaigns_EventId",
                table: "Campaigns");

            migrationBuilder.DropColumn(
                name: "EventId",
                table: "Campaigns");

            migrationBuilder.AddColumn<int>(
                name: "BrandId",
                table: "Campaigns",
                type: "integer",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Brief",
                table: "Campaigns",
                type: "text",
                nullable: true);

            migrationBuilder.CreateTable(
                name: "Brands",
                columns: table => new
                {
                    BrandId = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    Handle = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    DisplayName = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: false),
                    Niche = table.Column<string>(type: "text", nullable: true),
                    Followers = table.Column<int>(type: "integer", nullable: false),
                    TypicalPartnerFollowers = table.Column<int>(type: "integer", nullable: true),
                    IsClient = table.Column<bool>(type: "boolean", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Brands", x => x.BrandId);
                });

            migrationBuilder.CreateTable(
                name: "Creators",
                columns: table => new
                {
                    CreatorId = table.Column<string>(type: "character varying(40)", maxLength: 40, nullable: false),
                    Followers = table.Column<int>(type: "integer", nullable: false),
                    SizeTier = table.Column<string>(type: "text", nullable: true),
                    Niche = table.Column<string>(type: "text", nullable: true),
                    Email = table.Column<string>(type: "text", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Creators", x => x.CreatorId);
                });

            migrationBuilder.CreateTable(
                name: "CampaignCreators",
                columns: table => new
                {
                    CampaignCreatorId = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    CampaignId = table.Column<int>(type: "integer", nullable: false),
                    CreatorId = table.Column<string>(type: "character varying(40)", nullable: false),
                    Status = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    Rank = table.Column<int>(type: "integer", nullable: false),
                    Score = table.Column<double>(type: "double precision", nullable: false),
                    ReasonsJson = table.Column<string>(type: "text", nullable: false),
                    ModelVersion = table.Column<string>(type: "text", nullable: false),
                    SuggestedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    SelectedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    ContactedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    RespondedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    Note = table.Column<string>(type: "text", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_CampaignCreators", x => x.CampaignCreatorId);
                    table.ForeignKey(
                        name: "FK_CampaignCreators_Campaigns_CampaignId",
                        column: x => x.CampaignId,
                        principalTable: "Campaigns",
                        principalColumn: "CampaignId",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_CampaignCreators_Creators_CreatorId",
                        column: x => x.CreatorId,
                        principalTable: "Creators",
                        principalColumn: "CreatorId",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "OutreachEmails",
                columns: table => new
                {
                    OutreachEmailId = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    CampaignCreatorId = table.Column<int>(type: "integer", nullable: false),
                    ToEmail = table.Column<string>(type: "text", nullable: false),
                    FromEmail = table.Column<string>(type: "text", nullable: false),
                    Subject = table.Column<string>(type: "text", nullable: false),
                    Body = table.Column<string>(type: "text", nullable: false),
                    Provider = table.Column<string>(type: "text", nullable: false),
                    Model = table.Column<string>(type: "text", nullable: true),
                    ChecksPassed = table.Column<bool>(type: "boolean", nullable: false),
                    EditedByUser = table.Column<bool>(type: "boolean", nullable: false),
                    SentByUserId = table.Column<string>(type: "text", nullable: true),
                    SentAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_OutreachEmails", x => x.OutreachEmailId);
                    table.ForeignKey(
                        name: "FK_OutreachEmails_CampaignCreators_CampaignCreatorId",
                        column: x => x.CampaignCreatorId,
                        principalTable: "CampaignCreators",
                        principalColumn: "CampaignCreatorId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Campaigns_BrandId",
                table: "Campaigns",
                column: "BrandId");

            migrationBuilder.CreateIndex(
                name: "IX_Brands_Handle",
                table: "Brands",
                column: "Handle",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_CampaignCreators_CampaignId_CreatorId",
                table: "CampaignCreators",
                columns: new[] { "CampaignId", "CreatorId" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_CampaignCreators_CreatorId",
                table: "CampaignCreators",
                column: "CreatorId");

            migrationBuilder.CreateIndex(
                name: "IX_OutreachEmails_CampaignCreatorId",
                table: "OutreachEmails",
                column: "CampaignCreatorId");

            migrationBuilder.AddForeignKey(
                name: "FK_Campaigns_Brands_BrandId",
                table: "Campaigns",
                column: "BrandId",
                principalTable: "Brands",
                principalColumn: "BrandId",
                onDelete: ReferentialAction.Restrict);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Campaigns_Brands_BrandId",
                table: "Campaigns");

            migrationBuilder.DropTable(
                name: "Brands");

            migrationBuilder.DropTable(
                name: "OutreachEmails");

            migrationBuilder.DropTable(
                name: "CampaignCreators");

            migrationBuilder.DropTable(
                name: "Creators");

            migrationBuilder.DropIndex(
                name: "IX_Campaigns_BrandId",
                table: "Campaigns");

            migrationBuilder.DropColumn(
                name: "BrandId",
                table: "Campaigns");

            migrationBuilder.DropColumn(
                name: "Brief",
                table: "Campaigns");

            migrationBuilder.AddColumn<int>(
                name: "EventId",
                table: "Campaigns",
                type: "integer",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.CreateIndex(
                name: "IX_Campaigns_EventId",
                table: "Campaigns",
                column: "EventId");

            migrationBuilder.AddForeignKey(
                name: "FK_Campaigns_Events_EventId",
                table: "Campaigns",
                column: "EventId",
                principalTable: "Events",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);
        }
    }
}
